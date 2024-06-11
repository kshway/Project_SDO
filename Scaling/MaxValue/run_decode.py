# HM 디코더를 사용하여 .bin 파일들을 .yuv로 디코딩하는 Python 스크립트를 작성합니다.
# 이 스크립트는 주어진 경로에서 .bin 파일들을 찾고, 각 파일을 디코딩한 후, 결과를 지정된 형식으로 저장합니다.

import os
import subprocess

# 디코더 실행 파일 경로
decoder_path = r"C:\Users\1004t\HM\bin\vs16\msvc-19.29\x86_64\release\TAppDecoder.exe"

# 입력 및 출력 디렉토리 설정
input_directory = "encode42"
output_directory = "decoded_files_42"

# 디렉토리가 없으면 생성
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# 입력 디렉토리 내의 모든 .bin 파일을 순회
for filename in os.listdir(input_directory):
    if filename.endswith(".bin"):
        # 원본 파일 이름 추출 (확장자 제외)
        original_name = filename[:-4]

        # 출력 파일 이름 설정
        output_filename = f"{original_name}_decode.yuv"

        # 디코딩 명령어 조합
        command = [
            decoder_path,
            "-b", os.path.join(input_directory, filename),
            "-o", os.path.join(output_directory, output_filename)
        ]

        # 명령어 실행
        subprocess.run(command)

# Note: 실제 파일 경로, 디코더 경로 및 작업 환경에 따라 경로를 적절히 조정해야 합니다.
