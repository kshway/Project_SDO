import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps

# Load the Excel file
file_path = '비교all.xlsx'
excel_data = pd.ExcelFile(file_path)

# Load the data from the first sheet
df = excel_data.parse('Sheet1')

# Clean the dataframe by renaming the columns
df.columns = ['Index', 'hevc_psnr', 'hevc_bpp', 'jpeg2000_psnr', 'jpeg2000_bpp', 'balle_psnr', 'balle_bpp', 'cheng_psnr', 'cheng_bpp']

# Drop the first row which contains duplicate headers and the 'Index' column
df = df.drop([0]).reset_index(drop=True)
df = df.drop(columns=['Index'])

# Convert all columns to numeric values
df = df.apply(pd.to_numeric)

# Function to calculate BD-Rate
def calculate_bd_rate(bpp_ref, psnr_ref, bpp_cmp, psnr_cmp):
    # Interpolation
    interp_ref = np.interp(np.linspace(min(bpp_ref), max(bpp_ref), num=100), bpp_ref, psnr_ref)
    interp_cmp = np.interp(np.linspace(min(bpp_cmp), max(bpp_cmp), num=100), bpp_cmp, psnr_cmp)
    
    # Integration
    area_ref = simps(interp_ref, np.linspace(min(bpp_ref), max(bpp_ref), num=100))
    area_cmp = simps(interp_cmp, np.linspace(min(bpp_cmp), max(bpp_cmp), num=100))
    
    # BD-Rate calculation
    bd_rate = (area_cmp - area_ref) / area_ref * 100
    return bd_rate

# Calculate BD-Rate for each method compared to JPEG2000
bpp_ref, psnr_ref = df['jpeg2000_bpp'], df['jpeg2000_psnr']
bd_rates = {}

methods = {
    "HEVC": ('hevc_bpp', 'hevc_psnr'),
    "Balle ('18)": ('balle_bpp', 'balle_psnr'),
    "Cheng ('20)": ('cheng_bpp', 'cheng_psnr')
}

for method, (bpp_col, psnr_col) in methods.items():
    bpp_cmp, psnr_cmp = df[bpp_col], df[psnr_col]
    bd_rate = calculate_bd_rate(bpp_ref, psnr_ref, bpp_cmp, psnr_cmp)
    bd_rates[method] = bd_rate

print(bd_rates)
