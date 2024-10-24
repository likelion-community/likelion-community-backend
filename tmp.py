import tensorflow as tf
print("TensorFlow version:", tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

import tensorflow as tf

# 사용 가능한 GPU 장치 리스트 확인
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # 모든 GPU에 메모리 증가 설정 (메모리를 필요 시에만 점진적으로 사용)
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"사용 가능한 GPU: {gpus}")
    except RuntimeError as e:
        print(e)
else:
    print("GPU를 찾을 수 없습니다. NVIDIA GPU가 제대로 설치되었는지 확인하세요.")

import torch
torch.cuda.empty_cache()