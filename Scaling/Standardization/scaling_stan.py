import numpy as np
import os

def scale_yuv_files_with_normalization(folder_path,k):
    # Define the image resolution for the provided format
    width, height = 4096, 4096
    scaling_factors = []

    # Iterate through all files in the provided folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".yuv"):
            input_file_path = os.path.join(folder_path, filename)
            output_file_path = os.path.join(folder_path, filename.replace(".yuv", "_scaled.yuv"))
            
            # Read the YUV image data
            with open(input_file_path, 'rb') as file:
                image_data = np.fromfile(file, dtype=np.uint16).reshape((height, width)).astype(np.float32)
            
            # Calculate mean and standard deviation
            mean = np.mean(image_data)
            std_dev = np.std(image_data)
            
            # Normalize the image data
            if std_dev > 0:
                normalized_data = (image_data - mean) / std_dev
            else:
                normalized_data = image_data - mean  # Avoid division by zero
            
            # Scale to mean 2^15
            scaled_data = (normalized_data * (2**(15-k))) + (2**15)        
            scaled_data = np.round(scaled_data).astype(np.uint16)
            scaled_data = np.clip(scaled_data, 0, 65535)
            
            # Write the scaled image data to a new YUV file
            with open(output_file_path, 'wb') as file:
                scaled_data.tofile(file)
            
            # Record the filename, mean, and standard deviation
            scaling_factors.append(f"{filename}: mean={mean}, std_dev={std_dev}\n")

    # Write all scaling factors to a text file
    with open(os.path.join(folder_path, "scaling_factors.txt"), 'w') as file:
        file.writelines(scaling_factors)

# Example usage (commented out for initial code writing phase):
folder_path = "origin_data"
k = 4
scale_yuv_files_with_normalization(folder_path,k)
