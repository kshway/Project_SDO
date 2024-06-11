import os
import re
import pandas as pd

def extract_values(log_content):
    # 바이트 값을 추출하여 변환
    byte_pattern = re.compile(r'Bytes written to file: (\d+)')
    byte_matches = byte_pattern.findall(log_content)
    
    byte_values = [int(byte) for byte in byte_matches]
    converted_values = [byte_value * 8 / (768 * 512) for byte_value in byte_values]
    
    # YUV-PSNR 값을 추출 (SUMMARY 섹션에서)
    summary_pattern = re.compile(
        r'SUMMARY\s+[-]+\n\s*Total Frames\s*\|\s*Bitrate\s*Y-PSNR\s*U-PSNR\s*V-PSNR\s*YUV-PSNR\s*\n\s*\d+\s+[ai]\s+\d+\.\d+\s+[\d\.]+\s+[\d\.]+\s+[\d\.]+\s+([\d\.]+)', 
        re.DOTALL
    )
    summary_match = summary_pattern.search(log_content)
    
    yuv_psnr_values = []
    if summary_match:
        yuv_psnr_value = float(summary_match.group(1))
        yuv_psnr_values = [yuv_psnr_value] * len(converted_values)
    
    return converted_values, yuv_psnr_values

# 'encode1' 폴더 내 모든 로그 파일을 처리
folder_path = 'encode37'
data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".log"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as file:
            log_contents = file.read()
        
        byte_converted_values, yuv_psnr_values = extract_values(log_contents)
        
        # 길이가 맞지 않는 경우를 대비하여 최소 길이로 조정
        min_length = min(len(byte_converted_values), len(yuv_psnr_values))
        for i in range(min_length):
            data.append(( yuv_psnr_values[i],byte_converted_values[i]))

# 데이터프레임으로 정리
df = pd.DataFrame(data, columns=["psnr", "bpp"])

# 엑셀 파일로 저장
output_file = 'encode37.xlsx'
df.to_excel(output_file, index=False)
