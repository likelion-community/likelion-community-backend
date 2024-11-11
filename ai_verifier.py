import cv2
import numpy as np
import pytesseract
import easyocr
import torch
import re
import gc
import time
from extract_text_and_logo import extract_text_and_logo, detect_logo_with_text, extract_text 
from concurrent.futures import ThreadPoolExecutor

# 글로벌 EasyOCR 인스턴스 생성 (한 번만 생성하여 전체에서 재사용)
reader = easyocr.Reader(['ko', 'en'])

# 메모리 해제 함수
def clear_memory():
    """메모리 관리."""
    gc.collect()

# 회원 검증 함수
def verify_like_a_lion_member(uploaded_image):
    print("이미지 업로드 처리 시작")
    start_time = time.time()

    # 이미지 데이터를 NumPy 배열로 변환
    image_data = uploaded_image.read()
    img_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        print("이미지를 불러올 수 없습니다.")
        return False

    print("이미지 디코딩 완료")

    # OCR에 필요한 이미지 크기 조정
    img = resize_image_for_ocr(img, max_dim=500)  # 해상도를 더 낮춤

    try:
        print("텍스트 및 로고 추출 시작")
        
        # 병렬 처리로 로고 검출과 텍스트 필드 추출
        with ThreadPoolExecutor() as executor:
            logo_future = executor.submit(detect_logo_with_text, img, logo_templates, reader)
            text_future = executor.submit(extract_text, img, reader)
        
        # 결과 받기
        logo_detected = logo_future.result()
        text_data = text_future.result()

        print("로고 및 텍스트 검출 완료")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

    # 로고가 감지되지 않았을 때 False 반환
    if not logo_detected:
        print("로고를 감지할 수 없습니다.")
        return False
    elif text_data is None or not any(text_data.values()):
        print("필수 필드(ID, 이름, 휴대폰)를 감지할 수 없습니다.")
        return False
    else:
        print("유효한 회원입니다. 필드 데이터:", text_data)

    # 최종 결과 판단 및 메모리 해제
    clear_memory()
    print(f"전체 처리 시간: {time.time() - start_time}초 소요")
    return True


# OCR을 위한 이미지 리사이즈 함수
def resize_image_for_ocr(img, max_dim=500, min_dim=200):
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    elif max(h, w) < min_dim:
        scale = min_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    return img
