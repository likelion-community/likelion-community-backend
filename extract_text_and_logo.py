import cv2
import numpy as np
import pytesseract
import easyocr
import torch
import re
import gc

# 글로벌 easyocr 인스턴스 생성
reader = easyocr.Reader(['ko', 'en'])

def clear_memory():
    """메모리 관리."""
    gc.collect()

def resize_image_for_ocr(img, max_dim=500):
    """유동적인 리사이즈: 가장 긴 변을 기준으로 max_dim에 맞추어 원본 비율을 유지하여 리사이즈."""
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    return img


def detect_logo_with_text(image, logo_templates, reader, logo_text='멋쟁이사자처럼', threshold=0.2):
    """로고와 텍스트 검출 최적화."""
    # 상단 1/4 영역만 사용하여 로고 감지
    h, w = image.shape[:2]
    roi = image[:h // 4, :]
    resized_image = resize_image_for_ocr(roi, max_dim=500)  # 빠른 처리 위해 축소
    img_gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # 템플릿 스케일 설정: 작은 로고를 감지할 수 있는 적절한 크기 선택
    scales = [0.6, 0.8, 1.0]  # 너무 많은 스케일 시도를 줄임
    template_scales = [0.5, 0.75]  # 템플릿 크기를 줄여 작은 로고 감지 시도

    for scale in scales:
        scaled_image = cv2.resize(img_gray, (int(img_gray.shape[1] * scale), int(img_gray.shape[0] * scale)))

        for logo_template in logo_templates:
            if logo_template is None:
                continue

            for t_scale in template_scales:
                resized_template = cv2.resize(logo_template, 
                                              (int(logo_template.shape[1] * t_scale), 
                                               int(logo_template.shape[0] * t_scale)))
                
                if resized_template.shape[0] > scaled_image.shape[0] or resized_template.shape[1] > scaled_image.shape[1]:
                    continue

                result = cv2.matchTemplate(scaled_image, resized_template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(result >= threshold)

                for pt in zip(*loc[::-1]):
                    logo_roi = scaled_image[pt[1]:pt[1] + resized_template.shape[0], pt[0]:pt[0] + resized_template.shape[1]]
                    easyocr_results = reader.readtext(logo_roi, detail=0)
                    easyocr_text = ' '.join(easyocr_results)

                    if logo_text in easyocr_text:
                        print("로고 텍스트 감지 성공")
                        clear_memory()
                        return True

                clear_memory()

    print("로고 텍스트 감지 실패")
    clear_memory()
    return False

    


def extract_text(image, reader):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_filtered = cv2.bilateralFilter(img_gray, 9, 75, 75)
    img_blurred = cv2.GaussianBlur(img_filtered, (5, 5), 0)
    img_resized = cv2.resize(img_blurred, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    ocr_data = pytesseract.image_to_data(img_resized, output_type=pytesseract.Output.DICT, config='--psm 6 -l kor')
    easyocr_results = reader.readtext(image, detail=0)

    tesseract_results = ocr_data['text'] if isinstance(ocr_data['text'], list) else [ocr_data['text']]
    combined_results = easyocr_results + tesseract_results
    
    text_data = {'아이디': None, '이름': None, '휴대폰': None}

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

    def find_field(field, text_result):
        for text in text_result:
            if field in text:
                return text
        return None
    
    text_data['이름'] = find_field('이름', ocr_data['text']) or find_field('이름', easyocr_results)
    text_data['아이디'] = find_field('아이디', ocr_data['text']) or find_field('아이디', easyocr_results)
    text_data['휴대폰'] = find_field('휴대폰', ocr_data['text']) or find_field('휴대폰', easyocr_results) or find_field('휴대', combined_results)

    return text_data

def extract_text_and_logo(image, reader):
    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = image

    if img is None:
        print("이미지를 불러올 수 없습니다.")
        return None, False
    
    logo_templates = [
        cv2.imread(r'/home/ubuntu/likelion-community-backend/dataset/lion_logo_template.png', 0),
        cv2.imread(r'/home/ubuntu/likelion-community-backend/dataset/logo.jpg', 0)
    ]

    print("로고 검출 검사 시작")
    logo_detected = detect_logo_with_text(img, logo_templates, reader) 
    print("로고 검출 검사 완료")
    
    if logo_detected:
        print("텍스트 추출 시작") 
        text_data = extract_text(img, reader)
        if not any(text_data.values()):
            print("로고는 검출되었지만 필수 필드 검출에 실패했습니다.")
            return None, True
        elif text_data:
            print("모든 필수 필드와 로고가 성공적으로 검출되었습니다.")
            return text_data, logo_detected
    else:
        print("로고 미검출로 인해 필드 검사를 수행하지 않았습니다.")
        return None, False
