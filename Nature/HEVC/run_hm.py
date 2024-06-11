import os
import subprocess

# "data/" 디렉토리 설정
directory = "data_512/"

# encoder의 실행 파일 경로
encoder_path = r"C:\Users\1004t\HM\bin\vs16\msvc-19.29\x86_64\release\TAppEncoder.exe"

# 설정 파일 경로
config_path1 = "encoder_intra_main.cfg"
config_path2 = "kodak24.cfg"

# "data/" 디렉토리 내의 모든 파일을 순회
for filename in os.listdir(directory):
    if filename.endswith(".yuv"):
        input_image_path = os.path.join(directory, filename)
        input_filename = filename[:-4]
        
        # 명령어 조합
        command = [
            encoder_path,
            "-c", config_path1,
            "-c", config_path2,
            "-i", input_image_path,
            "-b", os.path.join(directory, f"{input_filename}_37.bin"),
            "-o", os.path.join(directory, f"{input_filename}_37_recon.yuv"),
            ">", os.path.join(directory, f"{input_filename}_37.log"),
            "2>&1"
        ]
        
        # 명령어 실행
        subprocess.run(" ".join(command), shell=True)
