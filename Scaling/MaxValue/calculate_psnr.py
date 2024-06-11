import numpy as np
import os
import pandas as pd

def calculate_psnr(file1, file2, max_pixel_value=65535):
    # 이미지 데이터 불러오기 및 float 타입으로 변환
    original = np.fromfile(file1, dtype=np.uint16).reshape((4096, 4096)).astype(np.float32)
    restored = np.fromfile(file2, dtype=np.uint16).reshape((4096, 4096)).astype(np.float32)
    
    # MSE 계산
    mse = np.mean((original - restored) ** 2)
    if mse == 0:
        return float('inf')  # 두 이미지가 완전히 동일한 경우
    # PSNR 계산
    psnr = 20 * np.log10(max_pixel_value / np.sqrt(mse))
    return psnr

def match_files_and_calculate_psnr_to_excel(origin_folder, restored_folder, output_excel_path):
    psnr_results = []
    # 원본 폴더의 모든 파일에 대하여
    for origin_filename in os.listdir(origin_folder):
        if origin_filename.endswith(".yuv"):
            restored_filename = f"{origin_filename.replace('.yuv', '_scaled_42_restored.yuv')}"
            origin_file_path = os.path.join(origin_folder, origin_filename)
            restored_file_path = os.path.join(restored_folder, restored_filename)
            # PSNR 계산
            if os.path.exists(restored_file_path):
                psnr = calculate_psnr(origin_file_path, restored_file_path)
                psnr_results.append({'Original File': origin_filename, 
                                     'Restored File': restored_filename, 
                                     'PSNR': psnr})

    # 결과를 DataFrame으로 변환 후 Excel 파일로 저장
    df_psnr = pd.DataFrame(psnr_results)
    df_psnr.to_excel(output_excel_path, index=False)
    return output_excel_path

# 파일 저장 경로 설정
output_excel_path = "psnr_42.xlsx"

# 폴더 경로 설정
origin_folder = "origin_data"
restored_folder = "restored_files_42"

# 결과를 Excel 파일로 저장
match_files_and_calculate_psnr_to_excel(origin_folder, restored_folder, output_excel_path)
