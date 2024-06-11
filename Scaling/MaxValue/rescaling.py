import numpy as np
import os

# 파일에서 최댓값을 읽어오는 함수
def read_max_values(file_path):
    max_values = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(':')
            max_values[parts[0].strip()] = int(parts[1].strip())
    return max_values

# 복원된 YUV 파일들을 역 스케일링하는 함수
def unscale_yuv_files(input_folder, output_folder, max_values):
    width, height = 4096, 4096  # 이미지의 해상도를 정의

    # 입력 폴더 내의 모든 파일을 순회
    for filename in os.listdir(input_folder):
        if filename.endswith("_decode.yuv"):
            original_name = filename.replace("_scaled_42_decode.yuv", ".yuv")
            max_value = max_values[original_name] if original_name in max_values else 65535

            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename.replace("_decode.yuv", "_restored.yuv"))
            
            # YUV 이미지 데이터를 읽기
            with open(input_file_path, 'rb') as file:
                image_data = np.fromfile(file, dtype=np.uint16).reshape((height, width))
            
            # 이미지 데이터를 역 스케일링
            if max_value > 0:
                image_data = (image_data.astype(float) / 65535) * max_value
            
            image_data = np.round(image_data).astype(np.uint16)
            
            # 스케일된 이미지 데이터를 새 YUV 파일에 쓰기
            with open(output_file_path, 'wb') as file:
                image_data.tofile(file)

# 최댓값 파일 읽기
max_values = read_max_values("data/max_values.txt")

# 역 스케일링 함수 실행
input_folder = "decoded_files_42"
output_folder = "restored_files_42"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

unscale_yuv_files(input_folder, output_folder, max_values)
