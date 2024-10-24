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

# 이미지 전처리 함수
def preprocess_images(image_paths):
    images = []
    for image_path in image_paths:
        image = tf.io.read_file(image_path)
        image = tf.image.decode_image(image, channels=3)
        image = tf.image.resize(image, [224, 224]) / 255.0
        images.append(image)
    return tf.stack(images)



# 예측 및 검증 함수
def predict_images(image_paths):
    try:
        start_time = time.time()
        
        # 배치 이미지 전처리
        images = preprocess_images(image_paths)
        predictions = model.predict(images)  # 모든 이미지의 예측 확률을 한 번에 가져옴

        results = []
        for i, prediction in enumerate(predictions):
            image_path = image_paths[i]
            
            # 각 이미지에 대해 필드 검출 및 확률 조정
            text_data, logo_detected = extract_text_and_logo(image_path)
            if text_data is None:
                print(f"{image_path}: 텍스트 데이터 없음")
                results.append(0)  # 비회원으로 예측
                continue

            required_fields = ['아이디', '이름', '휴대폰']
            field_status = {field: (text_data.get(field) is not None) for field in required_fields}
            field_status['로고'] = logo_detected
            adjusted_prediction = adjust_prediction_based_on_fields(prediction[0], field_status)
            
            print(f"--------------------------------\n이미지: {image_path} \n**원래 예측 확률: {prediction[0]:.2f}, \n**조정된 예측 확률: {adjusted_prediction:.2f}")

    

        # 최종 예측 결과 판단
        if adjusted_prediction >= 0.5:
            is_member_valid = is_valid_member(image_path)
            result = 1 if is_member_valid else 2
        else:
            is_member_valid = is_valid_member(image_path)
            result = 3 if not is_member_valid else 4
        results.append(result)


        end_time = time.time()
        print(f"**처리 시간: {end_time - start_time:.2f} 초--------------------------------\nn")
        return results
    
    except Exception as e:
        print(f"오류 발생: {image_path} 처리 중 - {e}")
        return []
    finally:
        # 메모리 해제
        tf.keras.backend.clear_session()
        torch.cuda.empty_cache()  # CUDA 캐시 비우기


# 필드 상태에 따라 확률을 조정하는 함수
def adjust_prediction_based_on_fields(prediction, field_status):
    # 필수 필드가 누락된 개수를 셉니다.
    missing_fields = sum([1 for field, detected in field_status.items() if field != '로고' and not detected])
    if missing_fields == 0:
        # 모든 필드가 있을 때 예측 확률을 높여줌
        adjusted_prediction = prediction * 1.2 

    else:
        # 검출 실패한 필드 수에 따라 확률 조정 (예: 누락된 필드당 0.8을 곱함)
        adjusted_prediction = prediction * (0.8 ** missing_fields)
    
    # 조정된 확률이 1을 넘지 않도록 함
    adjusted_prediction = min(adjusted_prediction, 1.0)

    return adjusted_prediction

    

if __name__ == '__main__':
    # 테스트 이미지 경로 설정
    test_member_dir = r'C:\Users\sunca\Desktop\likelion_community\dataset\test\member'
    test_non_member_dir = r'C:\Users\sunca\Desktop\likelion_community\dataset\test\non_member'

    # 이미지 파일 목록 생성
    test_images = [os.path.join(test_member_dir, filename) for filename in os.listdir(test_member_dir) if filename.endswith(('.png', '.jpg', '.jpeg'))]
    test_images += [os.path.join(test_non_member_dir, filename) for filename in os.listdir(test_non_member_dir) if filename.endswith(('.png', '.jpg', '.jpeg'))]

    # 시작 시간 기록
    total_start_time = time.time()

    batch_size = 3  # 배치 크기를 조정하여 적절한 속도를 찾습니다
    results = []
    for i in range(0, len(test_images), batch_size):
        image_batch = test_images[i:i + batch_size]
        results.extend(predict_images(image_batch))

    true_labels = [1] * len(os.listdir(test_member_dir)) + [0] * len(os.listdir(test_non_member_dir))
    predicted_labels = [1 if result in [1, 3] else 0 for result in results]


    # 예측 결과 평가
    true_labels = [1] * len(os.listdir(test_member_dir)) + [0] * len(os.listdir(test_non_member_dir))
    predicted_labels = [1 if result in [1, 3] else 0 for result in results]

    accuracy = accuracy_score(true_labels, predicted_labels)
    precision = precision_score(true_labels, predicted_labels, zero_division=1)
    recall = recall_score(true_labels, predicted_labels, zero_division=1)

    print("\n=== 모델 성능 평가 ===")
    print(f"정확도 (Accuracy): {accuracy:.2f}")
    print(f"정밀도 (Precision): {precision:.2f}")
    print(f"재현율 (Recall): {recall:.2f}")

    # 종료 시간 기록 및 총 시간 계산
    total_end_time = time.time()
    total_elapsed_time = total_end_time - total_start_time

    # 시간 변환 (시, 분, 초 단위로 변환)
    hours = int(total_elapsed_time // 3600)
    minutes = int((total_elapsed_time % 3600) // 60)
    seconds = int(total_elapsed_time % 60)
    
    print(f"\n=== 총 실행 시간: {hours}시간 {minutes}분 {seconds}초 ===")


