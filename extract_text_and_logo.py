import cv2
import numpy as np
import pytesseract
import easyocr
import re
import gc

# Tesseract 및 EasyOCR 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\sunca\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
reader = easyocr.Reader(['ko', 'en'])

def clear_memory():
    """메모리 관리."""
    gc.collect()


def detect_logo_with_text(image, logo_templates, logo_text='멋쟁이사자처럼', threshold=0.35):
    detected = False

    # 이미지 자체 확대 (작은 로고 검출을 위해)
    scales = [1.0, 2.0]  # 원본 크기와 확대 크기
    for scale in scales:
        resized_image = cv2.resize(image, (int(image.shape[1] * scale), int(image.shape[0] * scale)))

        img_gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        
        for logo_template in logo_templates:
            if logo_template is None:
                continue
            # 템플릿 매칭을 위한 다양한 스케일 적용
            for template_scale in np.linspace(0.2, 1.6, 10):  # 더 작은 크기에서 큰 크기까지 시도
                resized_template = cv2.resize(logo_template, 
                                              (int(logo_template.shape[1] * template_scale), 
                                               int(logo_template.shape[0] * template_scale)))
                if resized_template.shape[0] > img_gray.shape[0] or resized_template.shape[1] > img_gray.shape[1]:
                    continue
                
                # 템플릿 매칭 수행
                result = cv2.matchTemplate(img_gray, resized_template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(result >= threshold)
                
                # 매칭된 위치에서 로고 텍스트 검사
                for pt in zip(*loc[::-1]):
                    x, y = pt
                    w, h = resized_template.shape[::-1]
                    logo_roi = resized_image[y:y+h, x:x+w]
                    
                    # ROI 내 OCR 및 EasyOCR 수행
                    tess_text = pytesseract.image_to_string(logo_roi, config='--psm 6', lang='kor').strip()
                    easyocr_results = reader.readtext(logo_roi, detail=0)
                    easyocr_text = ' '.join(easyocr_results)
                    
                    # 두 OCR 결과에서 텍스트가 포함되어 있는지 확인
                    if logo_text in tess_text or logo_text in easyocr_text:
                        detected = True
                        break
                if detected:
                    break
            if detected:
                break
        if detected:
            break

    return detected



def extract_text(image):
    # Tesseract를 사용하여 전체 텍스트 추출
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_filtered = cv2.bilateralFilter(img_gray, 9, 75, 75)
    img_blurred = cv2.GaussianBlur(img_filtered, (5, 5), 0)
    img_resized = cv2.resize(img_blurred, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Tesseract를 사용하여 전체 텍스트 추출
    ocr_data = pytesseract.image_to_data(img_resized, output_type=pytesseract.Output.DICT, config='--psm 6 -l kor')


    #  Tesseract OCR 결과 출력
    #print(f"Tesseract 전체 텍스트 결과: {ocr_data['text']}")

    # EasyOCR 결과로 필드 탐지
    easyocr_results = reader.readtext(image, detail=0)

    # EasyOCR 결과 출력
    #print(f"EasyOCR 전체 텍스트 결과: {easyocr_results}")


    tesseract_results = ocr_data['text'] if isinstance(ocr_data['text'], list) else [ocr_data['text']]
    combined_results = easyocr_results + tesseract_results
    
    text_data = {'아이디': None, '이름': None, '휴대폰': None}

    # EasyOCR 통합 필드 탐지
    for i, word in enumerate(combined_results):
        if re.search(r'아이\s*디|아이다|아이디', word):
            if i + 1 < len(easyocr_results):
                text_data['아이디'] = easyocr_results[i + 1]
        elif '이름' in word:
            if i + 1 < len(easyocr_results):
                text_data['이름'] = easyocr_results[i + 1]
        elif re.search(r'휴대폰|휴대포|휴대.*', word):
            if i + 1 < len(easyocr_results):
                text_data['휴대폰'] = easyocr_results[i + 1]


    # 필드 매칭 함수
    def find_field(field, text_result):
        for text in text_result:
            if field in text:
                return text
        return None
    
    # 필드별 결과 통합 (Tesseract + EasyOCR)
    text_data['이름'] = find_field('이름', ocr_data['text']) or find_field('이름', easyocr_results)
    text_data['아이디'] = find_field('아이디', ocr_data['text']) or find_field('아이디', easyocr_results)
    text_data['휴대폰'] = find_field('휴대폰', ocr_data['text']) or find_field('휴대폰', easyocr_results) or find_field('휴대', combined_results)
   
    # # 필드 검출이 실패한 경우에만 OCR 결과 출력
    # if text_data['이름'] is None or text_data['아이디'] is None or text_data['휴대폰'] is None:
    #     print(f"Tesseract 전체 텍스트 결과: {ocr_data['text']}")
    #     print(f"EasyOCR 전체 텍스트 결과: {easyocr_results}")

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
        cv2.imread('/home/ubuntu/likelion-community-backend/dataset/t/lion_logo_template.png', 0),
        cv2.imread('/home/ubuntu/likelion-community-backend/dataset/t/logo.jpg', 0)
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
