import os
from PIL import Image
import numpy as np

# Define the paths
input_path = 'data/'  # Change to the correct local path
output_path = 'data_yuv/'

# Create the output directory if it doesn't exist
os.makedirs(output_path, exist_ok=True)

# Function to convert RGB image to YUV
def rgb_to_yuv(image):
    """Convert an RGB image to YUV format."""
    if image.mode != 'RGB':
        raise ValueError('Image is not in RGB mode')
    rgb = np.array(image)
    yuv = np.empty_like(rgb, dtype=np.float32)
    yuv[..., 0] = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    yuv[..., 1] = -0.14713 * rgb[..., 0] - 0.28886 * rgb[..., 1] + 0.436 * rgb[..., 2]
    yuv[..., 2] = 0.615 * rgb[..., 0] - 0.51499 * rgb[..., 1] - 0.10001 * rgb[..., 2]
    return yuv

# Read, convert, and save images
for filename in os.listdir(input_path):
    if filename.lower().endswith(('.png')):
        image_path = os.path.join(input_path, filename)
        image = Image.open(image_path)
        yuv_image = rgb_to_yuv(image)
        yuv_filename = os.path.join(output_path, os.path.splitext(filename)[0] + '.yuv')
        yuv_image.astype(np.uint8).tofile(yuv_filename)

"YUV 형식으로 변환이 완료되었습니다."

