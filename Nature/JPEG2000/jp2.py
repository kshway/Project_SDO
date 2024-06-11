import os
import cv2
import numpy as np
import pandas as pd
from skimage.metrics import peak_signal_noise_ratio as psnr

def read_yuv_file(file_path, width, height):
    frame_size = width * height * 3  # YUV 444 형식에서는 각 채널이 동일한 크기
    with open(file_path, 'rb') as f:
        raw = f.read(frame_size)
    y = np.frombuffer(raw[0:width*height], dtype=np.uint8).reshape((height, width))
    u = np.frombuffer(raw[width*height:width*height*2], dtype=np.uint8).reshape((height, width))
    v = np.frombuffer(raw[width*height*2:], dtype=np.uint8).reshape((height, width))
    return np.dstack((y, u, v))

def calculate_bpp(file_path, width, height):
    file_size = os.path.getsize(file_path)
    total_pixels = width * height
    return (file_size * 8) / total_pixels

def compress_and_decompress(yuv_data, output_file, compression_ratio):
    image = cv2.cvtColor(yuv_data, cv2.COLOR_YUV2BGR)
    encode_param = [cv2.IMWRITE_JPEG2000_COMPRESSION_X1000, compression_ratio]
    _, encoded_image = cv2.imencode('.jp2', image, encode_param)
    with open(output_file, 'wb') as f:
        f.write(encoded_image)
    decompressed_image = cv2.imdecode(np.fromfile(output_file, np.uint8), cv2.IMREAD_COLOR)
    decompressed_yuv = cv2.cvtColor(decompressed_image, cv2.COLOR_BGR2YUV)
    return decompressed_yuv

def main():
    input_folder = 'data_yuv_768'
    output_folder = 'output_jp2'
    os.makedirs(output_folder, exist_ok=True)
    width, height = 768, 512  # 예제 해상도, 파일에 맞게 수정하세요
    compression_ratios = [10, 20, 30, 40, 50]  # 예제 압축률, 필요한 대로 수정하세요
    results = []

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.yuv'):
            input_file_path = os.path.join(input_folder, file_name)
            yuv_data = read_yuv_file(input_file_path, width, height)
            base_name = os.path.splitext(file_name)[0]
            row = [base_name]
            
            for ratio in compression_ratios:
                output_file_path = os.path.join(output_folder, f'{base_name}_{ratio}.jp2')
                decompressed_yuv = compress_and_decompress(yuv_data, output_file_path, ratio)
                bpp_value = calculate_bpp(output_file_path, width, height)
                psnr_value = psnr(yuv_data, decompressed_yuv)

                row.append(bpp_value)
                row.append(psnr_value)

                # 압축 파일 삭제
                os.remove(output_file_path)
            
            results.append(row)
    
    # 결과를 DataFrame으로 변환
    columns = ['File Name']
    for ratio in compression_ratios:
        columns.append(f'BPP_{ratio}')
        columns.append(f'PSNR_{ratio}')
    df = pd.DataFrame(results, columns=columns)

    # 엑셀 파일로 저장
    df.to_excel('compression_results_yuv.xlsx', index=False)

if __name__ == "__main__":
    main()
