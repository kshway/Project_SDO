from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

def crop_and_save_fits(fits_file_path, x1, x2, y1, y2, suffix):
    """
    FITS 파일에서 데이터를 읽고, 그 데이터에서 음수 값을 0으로 변환한 후,
    지정된 범위로 이미지를 자르고, 자른 이미지를 새로운 FITS 파일로 저장하는 함수입니다.
    
    :param fits_file_path: 읽을 FITS 파일의 경로입니다.
    :param x1, x2, y1, y2: 자를 이미지의 범위 좌표입니다.
    :param suffix: 저장할 새로운 FITS 파일 이름에 추가할 접미사입니다.
    """
    # FITS 파일에서 이미지 데이터를 읽습니다.
    with fits.open(fits_file_path) as hdul:
        image_data = hdul[1].data
    
    # 이미지 데이터에서 음수 값을 0으로 변환합니다.
    image_data = np.clip(image_data, 0, None).astype(np.uint16)
    print('origin: ', image_data.shape)
    
    # 지정된 범위로 이미지를 자릅니다.
    cropped_data = image_data[y1:y2, x1:x2]
    
    # 자른 이미지를 새로운 FITS 파일로 저장합니다.
    # cropped_fits_path = fits_file_path.replace('.fits', f'_{suffix}_cropped.fits')
    # hdu = fits.PrimaryHDU(cropped_data)
    # hdu.writeto(cropped_fits_path, overwrite=True)
    
    plt.imshow(cropped_data, cmap='gray', vmin=np.min(cropped_data), vmax=np.max(cropped_data))
    print('cropped: ', cropped_data.shape)
    plt.axis('off')
    plt.show()

# 함수 호출 예시 (실행하지 않음)
crop_and_save_fits('origin/aia.lev1_euv_12s.2013-03-28T120000Z.171.image_lev1.fits', 1476, 1800, 1264, 1516, 'QS')
