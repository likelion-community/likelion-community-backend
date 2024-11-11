import cv2
import numpy as np
import pytesseract
import easyocr
import re
import gc

# 글로벌 easyocr 인스턴스 생성
reader = easyocr.Reader(['ko', 'en'])

def clear_memory():
    """메모리 관리."""
    gc.collect()



def detect_logo_with_text(image, logo_templates, logo_text='멋쟁이사자처럼', threshold=0.3):
    detected = False

    # 예상 위치 (상단 왼쪽)에 대한 검출 영역 설정
    height, width = image.shape[:2]
    roi = image[:height // 3, :width // 2] 

    # 여러 크기의 확대 이미지로 검출
    scales = [1.0, 1.5]  # 원본 크기와 약간 확대된 크기
    for scale in scales:
        resized_image = cv2.resize(roi, (int(roi.shape[1] * scale), int(roi.shape[0] * scale)))
        img_gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

        
        for logo_template in logo_templates:
            if logo_template is None:
                continue
            
            for template_scale in np.linspace(0.2, 1.0, 5):  # 템플릿 크기 조정 감소
                resized_template = cv2.resize(logo_template, 
                                              (int(logo_template.shape[1] * template_scale), 
                                               int(logo_template.shape[0] * template_scale)))
                if resized_template.shape[0] > img_gray.shape[0] or resized_template.shape[1] > img_gray.shape[1]:
                    continue
                
                result = cv2.matchTemplate(img_gray, resized_template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(result >= threshold)
                
                for pt in zip(*loc[::-1]):
                    logo_roi = resized_image[pt[1]:pt[1]+resized_template.shape[0], pt[0]:pt[0]+resized_template.shape[1]]
                    easyocr_results = reader.readtext(logo_roi, detail=0)
                    easyocr_text = ' '.join(easyocr_results)
                    
                    if logo_text in easyocr_text:
                        print("로고 텍스트 감지 성공 (EasyOCR)")
                        clear_memory()
                        return True
                    else:
                        # EasyOCR 실패 시에만 Tesseract 검증
                        tess_text = pytesseract.image_to_string(logo_roi, config='--psm 6', lang='kor').strip()
                        if logo_text in tess_text:
                            print("로고 텍스트 감지 성공 (Tesseract)")
                            clear_memory()
                            return True
                clear_memory()
    print("로고 텍스트 감지 실패")
    clear_memory()
    return False


def extract_text(image):
    text_data = {'아이디': None, '이름': None, '휴대폰': None}

    # EasyOCR로 필드 탐지 시도 (더 다양한 스케일 적용)
    easyocr_scales = [1.0, 1.25, 1.5, 2.0]  # 작은 글자부터 큰 글자까지
    for scale in easyocr_scales:
        resized_image = cv2.resize(image, (int(image.shape[1] * scale), int(image.shape[0] * scale)))
        easyocr_results = reader.readtext(resized_image, detail=0)

        print(f"[EasyOCR] 스케일 {scale}에서 검출된 텍스트: {easyocr_results}")
        
        # EasyOCR 결과 필드 탐지
        for i, word in enumerate(easyocr_results):
            if re.search(r'아이\s*디|아이다|아이디', word):
                text_data['아이디'] = easyocr_results[i + 1] if i + 1 < len(easyocr_results) else None
            elif '이름' in word:
                text_data['이름'] = easyocr_results[i + 1] if i + 1 < len(easyocr_results) else None
            elif re.search(r'휴대폰|휴대포|휴대.*', word):
                text_data['휴대폰'] = easyocr_results[i + 1] if i + 1 < len(easyocr_results) else None
        
        # 필드가 모두 검출되었으면 반복 중단
        if any(text_data.values()):
            print("EasyOCR로 텍스트 필드 검출 성공")
            print(f"[EasyOCR] 검출된 필드 데이터: {text_data}")
            return text_data

    print("최종 텍스트 필드 검출 결과:", text_data)
    return text_data


   


def extract_text_and_logo(image):
    # 이미지가 경로인지 확인
    if isinstance(image, str):
        img = cv2.imread(image)  # 경로가 문자열일 경우 파일 경로로부터 이미지 읽기
    else:
        img = image  # 이미지 객체일 경우 바로 사용

    if img is None:
        print("이미지를 불러올 수 없습니다.")
        return None, False
    
    # 1단계: 로고 검출
    # 로고 템플릿 경로를 서버의 절대 경로로 변경
    logo_templates = [
        cv2.imread('/home/ubuntu/likelion-community-backend/dataset/lion_logo_template.png', 0),
        cv2.imread('/home/ubuntu/likelion-community-backend/dataset/logo.jpg', 0)
    ]


    print("로고 검출 검사 시작")
    logo_detected = detect_logo_with_text(img, logo_templates)
    print("로고 검출 검사 완료")
    if logo_detected:
        print("텍스트 추출 시작") 
        text_data = extract_text(img)
        # 필드가 검출되지 않았는지 확인하는 조건 추가
        if not any(text_data.values()):
            print("로고는 검출되었지만 필수 필드 검출에 실패했습니다.")
            return None, True  # 검출 실패로 처리
        elif text_data:
            print("모든 필수 필드와 로고가 성공적으로 검출되었습니다.")
            return text_data, logo_detected
    else:
        print("로고 미검출로 인해 필드 검사를 수행하지 않았습니다.")
        return None, False
