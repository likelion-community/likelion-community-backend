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
    start_time = time.time()

    # 이미지 데이터를 NumPy 배열로 변환
    image_data = uploaded_image.read()
    img_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        print("이미지를 불러올 수 없습니다.")
        return False

    # OCR에 필요한 이미지 크기 조정
    img = resize_image_for_ocr(img)  # 해상도를 더 낮춤

    # 텍스트와 로고 추출 (추출 시간 측정)
    extraction_start = time.time()

    # extract_text_and_logo 함수 호출 전후에 로그 추가
    try:
        print("텍스트 및 로고 추출 시작")
        # extract_text_and_logo 함수 호출 전후에 디버깅 로그 추가
        text_data, logo_detected = extract_text_and_logo(img)  # 문제 발생 가능 지점
        print(f"텍스트 및 로고 추출 완료: {time.time() - extraction_start}초 소요")
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
        # 텍스트 데이터가 없을 경우 체크
        if text_data is None:
            print("필수 필드(ID, 이름, 휴대폰)를 감지할 수 없습니다.")
            return False
        
        else:
            print("유효한 회원입니다.")

    # 최종 결과 판단 및 메모리 해제
    clear_memory()
    print(f"전체 처리 시간: {time.time() - start_time}초 소요")
    return True


# OCR을 위한 이미지 리사이즈 함수
def resize_image_for_ocr(img, max_dim=800, min_dim=200):
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    elif max(h, w) < min_dim:
        scale = min_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    return img
