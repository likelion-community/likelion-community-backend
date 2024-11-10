import cv2
import numpy as np
import tensorflow as tf
from extract_text_and_logo import extract_text_and_logo
import time
import os

from tensorflow.keras.models import load_model # type: ignore

model = load_model('like_a_lion_member_model.h5')


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

    def resize_image_for_ocr(img, max_dim=1000):
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        return img

    # 리사이즈 후 OCR 수행
    img = resize_image_for_ocr(img)


    # 텍스트와 로고 추출 (추출 시간 측정)
    extraction_start = time.time()

    # extract_text_and_logo 함수 호출 전후에 로그 추가
    try:
        print("텍스트 및 로고 추출 시작")
        # extract_text_and_logo 함수 호출 전후에 디버깅 로그 추가
        print("extract_text_and_logo 호출 시작")
        text_data, logo_detected = extract_text_and_logo(img)  # 문제 발생 가능 지점
        print("extract_text_and_logo 호출 성공")
        print(f"텍스트 및 로고 추출 완료: {time.time() - extraction_start}초 소요")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

    # 로고가 감지되지 않았을 때 필드 검사를 생략하고 False 반환
    if not logo_detected:
        print("로고를 감지할 수 없습니다. 필드 검사를 생략합니다.")
        return False
    else:
        # 텍스트 데이터가 없을 경우 체크
        if text_data is None:
            print("필수 필드(ID, 이름, 휴대폰)를 감지할 수 없습니다.")
            return False
        
        else:
            print("유효한 회원입니다.")

    # 필드 상태 확인
    required_fields = ['아이디', '이름', '휴대폰']
    field_status = {field: (text_data.get(field) is not None) for field in required_fields}
    field_status['로고'] = logo_detected

    prediction = preprocess_and_predict_image(img)

    # 필드 상태에 따라 확률 조정
    adjusted_prediction = adjust_prediction_based_on_fields(prediction, field_status)

    # 최종 결과 판단
    print(f"전체 처리 시간: {time.time() - start_time}초 소요")
    return adjusted_prediction >= 0.5


# 이미지 전처리 및 예측 수행 함수
def preprocess_and_predict_image(img):
    
    img_resized = cv2.resize(img, (224, 224)) / 255.0
    img_resized = np.expand_dims(img_resized, axis=0)
    
    # 모델로 예측 수행
    prediction = model.predict(img_resized)[0][0]

    return prediction

# 필드 상태에 따라 확률을 조정하는 함수
def adjust_prediction_based_on_fields(prediction, field_status):
    missing_fields = sum([1 for field, detected in field_status.items() if field != '로고' and not detected])
    if missing_fields == 0:
        adjusted_prediction = prediction * 1.2
    else:
        adjusted_prediction = prediction * (0.8 ** missing_fields)
    return min(adjusted_prediction, 1.0)
