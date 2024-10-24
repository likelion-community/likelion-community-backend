import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
from extract_text_and_logo import extract_text_and_logo
import os
os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'
from sklearn.metrics import accuracy_score, precision_score, recall_score
import time
from multiprocessing import Pool
import torch
import tensorflow as tf

# GPU 설정
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # GPU 메모리 할당을 동적으로 조정
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"{len(gpus)}개의 GPU가 사용 가능합니다.")
    except RuntimeError as e:
        print(f"GPU 설정 중 오류 발생: {e}")
else:
    print("외장 GPU를 사용할 수 없습니다.")

torch.cuda.empty_cache()

# 트레인된 모델 로드
model = load_model('like_a_lion_member_model.h5')

# 이미지 유효성 검사 함수
def is_valid_member(image_path):
    text_data, logo_detected = extract_text_and_logo(image_path)
    if text_data is None:
        print(f"{image_path}: 텍스트 데이터 없음")
        return False

    required_fields = ['아이디', '이름', '휴대폰']
    field_status = {field: (text_data.get(field) is not None) for field in required_fields}
    field_status['로고'] = logo_detected

    return all(field_status.get(field) for field in required_fields + ['로고'])

# 이미지 전처리 및 예측 수행 함수
def preprocess_and_predict_image(img):
    # 이미지를 NumPy 배열로 변환하고, 전처리 수행
    img_resized = cv2.resize(img, (224, 224)) / 255.0
    img_resized = np.expand_dims(img_resized, axis=0)

    # 모델로 예측 수행
    prediction = model.predict(img_resized)[0][0]
    return prediction


# 필드 상태에 따라 확률을 조정하는 함수
def adjust_prediction_based_on_fields(prediction, field_status):
    # 필수 필드가 누락된 개수를 셈
    missing_fields = sum([1 for field, detected in field_status.items() if field != '로고' and not detected])
    if missing_fields == 0:
        # 모든 필드가 있을 때 예측 확률을 높여줌
        adjusted_prediction = prediction * 1.2
    else:
        # 검출 실패한 필드 수에 따라 확률 조정
        adjusted_prediction = prediction * (0.8 ** missing_fields)
    
    # 조정된 확률이 1을 넘지 않도록 함
    adjusted_prediction = min(adjusted_prediction, 1.0)
    return adjusted_prediction

import logging

logger = logging.getLogger(__name__)

# 회원 검증 함수
def verify_like_a_lion_member(image):
    # 이미지를 NumPy 배열로 변환하여 OpenCV에서 사용 가능하도록 함
    image_data = image.read()  
    img_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    if img is None:
        print("이미지를 불러올 수 없습니다.")
        return False
    
    text_data, logo_detected = extract_text_and_logo(img)
    
    if logo_detected is None:
        logger.info("Logo not detected in the image.")
        return False

    if text_data is None:
        logger.info("Required fields (ID, Name, Phone) not detected in the image.")
        return False  # 텍스트 검출 실패 시 비회원으로 판단

    # 필수 필드 확인
    required_fields = ['아이디', '이름', '휴대폰']
    field_status = {field: (text_data.get(field) is not None) for field in required_fields}
    field_status['로고'] = logo_detected

    # 이미지 예측 수행 - 이미지를 다시 읽는 대신 메모리 버퍼를 사용하여 재사용
    prediction = preprocess_and_predict_image(img)  # 예측 값 얻기

    # 필드 상태에 따라 확률 조정
    adjusted_prediction = adjust_prediction_based_on_fields(prediction, field_status)


    # 최종 결과 판단: 조정된 확률이 0.5 이상일 경우 True, 그렇지 않으면 False
    return adjusted_prediction >= 0.5