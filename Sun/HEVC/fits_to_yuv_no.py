from astropy.io import fits
import numpy as np

def fits_to_yuv_16bit_no_neg(fits_file_path, yuv_output_path):
    """
    FITS 파일에서 데이터를 읽고, 그 데이터에서 음수 값을 0으로 변환한 후,
    16비트 그레이스케일(Y 채널 데이터만)로 YUV 파일로 저장하는 함수입니다.
    
    :param fits_file_path: 읽을 FITS 파일의 경로입니다.
    :param yuv_output_path: 저장할 YUV 파일의 경로입니다.
    """
    # FITS 파일에서 이미지 데이터를 읽습니다.
    with fits.open(fits_file_path) as hdul:
         image_data = hdul[1].data
    
    # 이미지 데이터에서 음수 값을 0으로 변환합니다.
    image_data = np.clip(image_data, 0, None).astype(np.uint16)
    
    # YUV 파일로 데이터를 저장합니다. 여기서는 Y 채널 데이터만 사용하므로,
    # 직접 16비트 데이터를 파일에 쓰면 됩니다.
    with open(yuv_output_path, 'wb') as f:
         image_data.tofile(f)

# 함수 호출 예시 (실행하지 않음)
fits_to_yuv_16bit_no_neg("aia.lev1_euv_12s.2023-12-01T000010Z.171.image_lev1.fits", "sun.yuv")
