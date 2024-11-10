import cv2
import numpy as np
import pytesseract
import easyocr
import re
import gc

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
            
            for template_scale in np.linspace(0.6, 1.0, 5):
                resized_template = cv2.resize(logo_template, 
                                              (int(logo_template.shape[1] * template_scale), 
                                               int(logo_template.shape[0] * template_scale)))
                if resized_template.shape[0] > img_gray.shape[0] or resized_template.shape[1] > img_gray.shape[1]:
                    continue
                
                result = cv2.matchTemplate(img_gray, resized_template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(result >= threshold)
                
                for pt in zip(*loc[::-1]):
                    logo_roi = resized_image[pt[1]:pt[1]+resized_template.shape[0], pt[0]:pt[0]+resized_template.shape[1]]
                    tess_text = pytesseract.image_to_string(logo_roi, config='--psm 6', lang='kor').strip()

                    # easyocr.Reader 인스턴스 생성 및 사용 후 삭제
                    reader = easyocr.Reader(['ko', 'en'])
                    easyocr_results = reader.readtext(logo_roi, detail=0)
                    del reader  # 메모리 해제
                    
                    easyocr_text = ' '.join(easyocr_results)

                    if logo_text in tess_text or logo_text in easyocr_text:
                        return True
    return False

def extract_text(image):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_filtered = cv2.bilateralFilter(img_gray, 9, 75, 75)
    img_blurred = cv2.GaussianBlur(img_filtered, (5, 5), 0)
    img_resized = cv2.resize(img_blurred, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    ocr_data = pytesseract.image_to_data(img_resized, output_type=pytesseract.Output.DICT, config='--psm 6 -l kor')

    # easyocr.Reader 인스턴스 생성 및 사용 후 삭제
    reader = easyocr.Reader(['ko', 'en'])
    easyocr_results = reader.readtext(image, detail=0)
    del reader  # 메모리 해제

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

def extract_text_and_logo(image):
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
    logo_detected = detect_logo_with_text(img, logo_templates)
    print("로고 검출 검사 완료")
    
    if logo_detected:
        print("텍스트 추출 시작") 
        text_data = extract_text(img)
        if not any(text_data.values()):
            print("로고는 검출되었지만 필수 필드 검출에 실패했습니다.")
            return None, True
        elif text_data:
            print("모든 필수 필드와 로고가 성공적으로 검출되었습니다.")
            return text_data, logo_detected
    else:
        print("로고 미검출로 인해 필드 검사를 수행하지 않았습니다.")
        return None, False
