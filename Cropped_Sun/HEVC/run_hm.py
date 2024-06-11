import os
import subprocess

# "data/" 디렉토리 설정
directory = "data/"

# encoder의 실행 파일 경로
encoder_path = r"C:\Users\1004t\HM\bin\vs16\msvc-19.29\x86_64\release\TAppEncoder.exe"

# 설정 파일 경로
config_path1 = "encoder_intra_monochrome16.cfg"
config_path2 = "sun.cfg"

input_filename = 'aia.lev1_euv_12s.2012-01-04T120001Z.171.image_lev1_AR'
        
        # 명령어 조합
command = [
    encoder_path,
    "-c", config_path1,
    "-c", config_path2,
    "-i", os.path.join(directory, f"{input_filename}.yuv"),
    "-b", os.path.join(directory, f"{input_filename}_3.bin"),
    "-o", os.path.join(directory, f"{input_filename}_3_recon.yuv"),
    ">", os.path.join(directory, f"{input_filename}_3.log"),
    "2>&1"
        ]
        
# 명령어 실행
subprocess.run(command, shell=True)
