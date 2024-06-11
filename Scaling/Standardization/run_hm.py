import os
import subprocess

# "data/" 디렉토리 설정
directory = "data/"

# encoder의 실행 파일 경로
encoder_path = r"C:\Users\1004t\HM\bin\vs16\msvc-19.29\x86_64\release\TAppEncoder.exe"

# 설정 파일 경로
config_path1 = "encoder_intra_monochrome16.cfg"
config_path2 = "sun.cfg"

# "data/" 디렉토리 내의 모든 파일을 순회
for filename in os.listdir(directory):
    if filename.endswith(".yuv"):
        # 파일명에서 확장자 제거
        input_filename = filename[:-4]
        
        # 명령어 조합
        command = [
            encoder_path,
            "-c", config_path1,
            "-c", config_path2,
            "-i", os.path.join(directory, f"{input_filename}.yuv"),
            "-b", os.path.join(directory, f"{input_filename}_22.bin"),
            "-o", os.path.join(directory, f"{input_filename}_22_recon.yuv"),
            ">", os.path.join(directory, f"{input_filename}_22.log"),
            "2>&1"
        ]
        
        # 명령어 실행
        subprocess.run(command, shell=True)

