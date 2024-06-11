import numpy as np
import os

# 파일에서 평균과 표준편차를 읽어오는 함수
def read_scaling_factors(file_path):
    scaling_factors = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(':')
            filename = parts[0].strip()
            mean_std = parts[1].strip().split(',')
            mean = float(mean_std[0].split('=')[1].strip())
            std_dev = float(mean_std[1].split('=')[1].strip())
            scaling_factors[filename] = (mean, std_dev)
    return scaling_factors

# 복원된 YUV 파일들을 역 스케일링하는 함수
def reverse_scale_yuv_files(input_folder, output_folder, scaling_factors, k):
    width, height = 4096, 4096  # 이미지의 해상도를 정의

    # 입력 폴더 내의 모든 파일을 순회
    for filename in os.listdir(input_folder):
        if filename.endswith("_decode.yuv"):
            original_name = filename.replace("_scaled_22_decode.yuv", ".yuv")
            if original_name in scaling_factors:
                mean, std_dev = scaling_factors[original_name]

                input_file_path = os.path.join(input_folder, filename)
                output_file_path = os.path.join(output_folder, filename.replace("_decode.yuv", "_restored.yuv"))
                
                # YUV 이미지 데이터를 읽기
                with open(input_file_path, 'rb') as file:
                    scaled_data = np.fromfile(file, dtype=np.uint16).reshape((height, width)).astype(np.float32)
                
                # 정규화 해제
                normalized_data = (scaled_data - (2**15)) / (2**(15-k))

                # 중간 결과 확인 (디버깅)
                print(f"Processing {filename}")
                print(f"Mean: {mean}, Std Dev: {std_dev}")
                print(f"Scaled Data Max: {np.max(scaled_data)}, Min: {np.min(scaled_data)}")
                print(f"Normalized Data Max: {np.max(normalized_data)}, Min: {np.min(normalized_data)}")

                # 복원
                original_data = (normalized_data * std_dev) + mean +0.5       
                original_data = np.floor(original_data)
                original_data = np.clip(original_data, 0, 65535).astype(np.uint16)
                
                # 중간 결과 확인 (디버깅)
                print(f"Original Data Max: {np.max(original_data)}, Min: {np.min(original_data)}")
                
                # 역 스케일된 이미지 데이터를 새 YUV 파일에 쓰기
                with open(output_file_path, 'wb') as file:
                    original_data.tofile(file)

# 평균과 표준편차 파일 읽기
scaling_factors = read_scaling_factors("data/scaling_factors.txt")

# 역 스케일링 함수 실행
input_folder = "decoded_files_22"
output_folder = "restored_files_22"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

k = 4
reverse_scale_yuv_files(input_folder, output_folder, scaling_factors, k)
