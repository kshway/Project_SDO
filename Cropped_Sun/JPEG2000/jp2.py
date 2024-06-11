import subprocess
import os
import pandas as pd
from astropy.io import fits
import numpy as np
import cv2
from skimage.metrics import peak_signal_noise_ratio as psnr

# FITS 데이터를 일반 이미지 형식으로 변환
def fits_to_tiff(fits_filename, tiff_filename):
    hdul = fits.open(fits_filename)
    fits_data = hdul[0].data
    hdul.close()

    # 음수값을 0으로 처리
    fits_data = np.maximum(fits_data, 0)
    
    # 16비트 정수로 변환
    fits_data_16bit = fits_data.astype(np.uint16)

    cv2.imwrite(tiff_filename, fits_data_16bit)

# 이미지를 JPEG2000으로 압축
def compress_to_jpeg2000(input_image, output_image, rate):
    command = f"opj_compress -i {input_image} -o {output_image} -r {rate}"
    subprocess.run(command, shell=True, check=True)

# JPEG2000 이미지를 복원
def decompress_jpeg2000(input_image, output_image):
    command = f"opj_decompress -i {input_image} -o {output_image}"
    subprocess.run(command, shell=True, check=True)

# 복원된 이미지를 FITS 형식으로 변환
def tiff_to_fits(tiff_filename, fits_filename):
    restored_image = cv2.imread(tiff_filename, cv2.IMREAD_UNCHANGED)
    restored_fits_data = restored_image.astype(np.float32)
    hdu = fits.PrimaryHDU(restored_fits_data)
    hdul = fits.HDUList([hdu])
    hdul.writeto(fits_filename, overwrite=True)

# PSNR 계산
def calculate_psnr(original_fits, restored_fits):
    original_hdul = fits.open(original_fits)
    original_data = original_hdul[0].data
    original_hdul.close()

    restored_hdul = fits.open(restored_fits)
    restored_data = restored_hdul[0].data
    restored_hdul.close()

    # 음수값을 0으로 처리 (원본 데이터에도 동일 적용)
    original_data = np.maximum(original_data, 0)
    restored_data = np.maximum(restored_data, 0)

    # 16비트 데이터 비교
    psnr_value = psnr(original_data, restored_data, data_range=65535)
    return psnr_value

# BPP 계산
def calculate_bpp(file_path, image_size):
    file_size = os.path.getsize(file_path)  # 파일 크기를 바이트 단위로 가져옴
    bpp = (file_size * 8) / image_size  # 비트 단위로 변환 후 픽셀 수로 나눔
    return bpp

# 특정 FITS 파일 처리 및 결과 저장
def process_single_fits(fits_file, output_xlsx, rates):
    results = []
    image_size = 1044*644  # 이미지 크기 (픽셀 수)

    fits_image_filename = fits_file
    tiff_image_filename = fits_image_filename.replace('.fits', '.tif')
    restored_fits_image_filename = fits_image_filename.replace('.fits', '_restored.fits')

    # FITS to TIFF
    fits_to_tiff(fits_image_filename, tiff_image_filename)

    for rate in rates:
        compressed_image_filename = fits_image_filename.replace('.fits', f'_compressed_r{rate}.j2k')
        restored_tiff_image_filename = fits_image_filename.replace('.fits', f'_restored_r{rate}.tif')

        # TIFF to JPEG2000
        compress_to_jpeg2000(tiff_image_filename, compressed_image_filename, rate)

        # JPEG2000 to TIFF
        decompress_jpeg2000(compressed_image_filename, restored_tiff_image_filename)

        # TIFF to FITS
        tiff_to_fits(restored_tiff_image_filename, restored_fits_image_filename)

        # PSNR 계산
        psnr_value = calculate_psnr(fits_image_filename, restored_fits_image_filename)

        # BPP 계산
        bpp_value = calculate_bpp(compressed_image_filename, image_size)

        # 결과 저장
        results.append({
            'filename': fits_file,
            'rate': rate,
            'psnr': psnr_value,
            'bpp': bpp_value
        })

        # 중간 파일 삭제
        os.remove(compressed_image_filename)
        os.remove(restored_tiff_image_filename)
    # 중간 파일 삭제
    os.remove(tiff_image_filename)
    os.remove(restored_fits_image_filename)

    # 결과를 DataFrame으로 변환하여 XLSX 파일로 저장
    df = pd.DataFrame(results)
    print(df)
    # with pd.ExcelWriter(output_xlsx) as writer:
    #     df.to_excel(writer, index=False, sheet_name='Compression Results')

# 메인 함수
def main():
    fits_file = 'paper_data/aia.lev1_euv_12s.2012-01-04T120001Z.171.image_lev1_AR_cropped.fits'  # 처리할 특정 FITS 파일 경로
    output_xlsx = 'result1.xlsx'  # 결과를 저장할 XLSX 파일명
    rates = [100]  # 여러 가지 압축률

    # 특정 FITS 파일 처리 및 결과 저장
    process_single_fits(fits_file, output_xlsx, rates)

if __name__ == "__main__":
    main()
