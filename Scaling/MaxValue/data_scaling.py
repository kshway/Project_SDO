import numpy as np
import os

def scale_yuv_files_and_record_max(folder_path):
    # Define the image resolution for the provided format
    width, height = 4096, 4096
    max_values = []

    # Iterate through all files in the provided folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".yuv"):
            input_file_path = os.path.join(folder_path, filename)
            output_file_path = os.path.join(folder_path, filename.replace(".yuv", "_scaled.yuv"))
            
            # Read the YUV image data
            with open(input_file_path, 'rb') as file:
                image_data = np.fromfile(file, dtype=np.uint16).reshape((height, width))
            
            # Scale the image data
            max_value = np.max(image_data)
            if max_value > 0:
                image_data = (image_data.astype(float) / max_value) * 65535
            
            image_data = np.round(image_data).astype(np.uint16)
            
            # Write the scaled image data to a new YUV file
            with open(output_file_path, 'wb') as file:
                image_data.tofile(file)
            
            # Record the filename and its max value
            max_values.append(f"{filename}: {max_value}\n")

    # Write all max values to a text file
    with open(os.path.join(folder_path, "max_values.txt"), 'w') as file:
        file.writelines(max_values)

# Example usage (commented out for initial code writing phase):
folder_path = "data"
scale_yuv_files_and_record_max(folder_path)
