import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps

# Load the new Excel file
file_path_new = 'sun_all.xlsx'
excel_data_new = pd.ExcelFile(file_path_new)

# Load the data from the first sheet
df_new = excel_data_new.parse('Sheet1')

# Clean the dataframe by renaming the columns
df_new.columns = ['jpeg2000_bpp', 'jpeg2000_psnr', 'hevc_bpp', 'hevc_psnr', 'balle_bpp', 'balle_psnr', 'cheng_bpp', 'cheng_psnr']

# Drop the first row which contains duplicate headers
df_new = df_new.drop([0]).reset_index(drop=True)

# Convert all columns to numeric values
df_new = df_new.apply(pd.to_numeric)

# Function to calculate BD-Rate within overlapping PSNR ranges
def calculate_bd_rate_with_psnr_overlap(bpp_ref, psnr_ref, bpp_cmp, psnr_cmp):
    # Determine the overlapping psnr range
    min_psnr = max(min(psnr_ref), min(psnr_cmp))
    max_psnr = min(max(psnr_ref), max(psnr_cmp))
    
    # Filter the data within the overlapping range
    mask_ref = (psnr_ref >= min_psnr) & (psnr_ref <= max_psnr)
    mask_cmp = (psnr_cmp >= min_psnr) & (psnr_cmp <= max_psnr)
    
    bpp_ref_overlap = bpp_ref[mask_ref]
    psnr_ref_overlap = psnr_ref[mask_ref]
    bpp_cmp_overlap = bpp_cmp[mask_cmp]
    psnr_cmp_overlap = psnr_cmp[mask_cmp]
    
    # Interpolation
    interp_psnr = np.linspace(min_psnr, max_psnr, num=100)
    interp_ref = np.interp(interp_psnr, psnr_ref_overlap, bpp_ref_overlap)
    interp_cmp = np.interp(interp_psnr, psnr_cmp_overlap, bpp_cmp_overlap)
    
    # Integration
    area_ref = simps(interp_ref, interp_psnr)
    area_cmp = simps(interp_cmp, interp_psnr)
    
    # BD-Rate calculation
    bd_rate = (area_cmp - area_ref) / area_ref * 100
    return bd_rate

# Calculate BD-Rate for each method compared to JPEG2000 within overlapping psnr ranges
bpp_ref_new, psnr_ref_new = df_new['jpeg2000_bpp'], df_new['jpeg2000_psnr']
bd_rates_jpeg2000_psnr_overlap = {}

methods_jpeg2000_new = {
    "HEVC": ('hevc_bpp', 'hevc_psnr'),
    "Balle ('18)": ('balle_bpp', 'balle_psnr'),
    "Cheng ('20)": ('cheng_bpp', 'cheng_psnr')
}

for method, (bpp_col, psnr_col) in methods_jpeg2000_new.items():
    bpp_cmp, psnr_cmp = df_new[bpp_col], df_new[psnr_col]
    bd_rate = calculate_bd_rate_with_psnr_overlap(bpp_ref_new, psnr_ref_new, bpp_cmp, psnr_cmp)
    bd_rates_jpeg2000_psnr_overlap[method] = bd_rate

print(bd_rates_jpeg2000_psnr_overlap)
