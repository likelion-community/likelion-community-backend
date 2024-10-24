import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import torch

# TensorFlow GPU 설정
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

torch.cuda.empty_cache()

# 이미지 전처리 함수
def preprocess_image_with_label(image_path, label):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_image(image, channels=3)
    image.set_shape([None, None, 3])  # None을 통해 가변적 크기를 설정하고 이후에 크기를 재조정
    image = tf.image.resize(image, [224, 224]) / 255.0
    return image, label

if __name__ == '__main__':
    # 학습 데이터 로드
    member_dir = os.path.join('dataset', 'member')
    non_member_dir = os.path.join('dataset', 'non_member')

    # 폴더에서 이미지 파일 경로 가져오기
    member_images = [os.path.join(member_dir, filename) for filename in os.listdir(member_dir) if filename.endswith(('.png', '.jpg', '.jpeg'))]
    non_member_images = [os.path.join(non_member_dir, filename) for filename in os.listdir(non_member_dir) if filename.endswith(('.png', '.jpg', '.jpeg'))]

    # 이미지 경로와 레이블 준비
    train_images = member_images + non_member_images
    train_labels = [1] * len(member_images) + [0] * len(non_member_images)

    if not train_images:
        print("학습 데이터셋이 비어 있습니다. 스크립트를 종료합니다.")
        exit()

    # 데이터셋 준비
    train_dataset = tf.data.Dataset.from_tensor_slices((train_images, train_labels))
    train_dataset = train_dataset.map(preprocess_image_with_label)
    train_dataset = train_dataset.batch(32).prefetch(tf.data.experimental.AUTOTUNE)

    # 모델 구조 정의
    model = Sequential([
        Conv2D(16, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D(2, 2),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])

    # 모델 컴파일
    model.compile(optimizer=Adam(learning_rate=0.00005),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # 모델 학습
    early_stopping = EarlyStopping(monitor='accuracy', patience=5, restore_best_weights=True)
    model.fit(
        train_dataset,
        epochs=30,
        callbacks=[early_stopping]
    )

    # 모델 저장
    model.save('like_a_lion_member_model.h5')
    print("모델이 성공적으로 저장되었습니다!")
