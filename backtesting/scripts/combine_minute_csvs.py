import pandas as pd
import glob
import os
import numpy as np
import matplotlib.pyplot as plt

# Specify the pool address you want to process
pool_address = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
pool_address = pool_address.lower()  # Ensure lowercase for file matching

# Specify quote asset: 'token0' or 'token1'
quote_asset = 'token1'  # Change this to 'token0' if you want token0 as quote asset

# Specify token decimals
token0_decimals = 18
token1_decimals = 18

# Path to the data folder and output file
data_folder = os.path.join('..', 'data', pool_address)
if not os.path.exists(data_folder):
    os.makedirs(data_folder, exist_ok=True)
output_file = os.path.join(data_folder, f'all_days_combined_{pool_address}.csv')

# Find all .minute.csv files in the data folder for the specified pool address
csv_files = glob.glob(os.path.join(data_folder, f'ethereum-{pool_address}-*.minute.csv'))

# Read and concatenate all CSVs
df_list = [pd.read_csv(f) for f in csv_files]
combined_df = pd.concat(df_list, ignore_index=True)
combined_df = combined_df.sort_values('timestamp')

# Ensure netAmount0 and netAmount1 are numeric
combined_df['netAmount0'] = pd.to_numeric(combined_df['netAmount0'], errors='coerce')
combined_df['netAmount1'] = pd.to_numeric(combined_df['netAmount1'], errors='coerce')

# Calculate price based on quote asset specification
if quote_asset == 'token1':
    # Price in token1/token0 terms (current implementation)
    if pool_address == '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640':
        combined_df['price'] = (1 / (1.0001 ** combined_df['closeTick'])) * 1e12
        # Trade volume in token0 terms (preserve sign)
        combined_df['tradevolume'] = (combined_df['netAmount0'] / (10 ** token0_decimals)) * 1e12
    else:
        combined_df['price'] = 1 / (1.0001 ** combined_df['closeTick'])
        # Trade volume in token0 terms (preserve sign)
        combined_df['tradevolume'] = combined_df['netAmount0'] / (10 ** token0_decimals)
    print(f"Using {quote_asset} as quote asset: Price in token1/token0, Volume in token0")
elif quote_asset == 'token0':
    # Price in token0/token1 terms (no inversion)
    if pool_address == '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640':
        combined_df['price'] = (1.0001 ** combined_df['closeTick']) * 1e12
        # Trade volume in token1 terms (preserve sign)
        combined_df['tradevolume'] = (combined_df['netAmount1'] / (10 ** token1_decimals)) * 1e12
    else:
        combined_df['price'] = 1.0001 ** combined_df['closeTick']
        # Trade volume in token1 terms (preserve sign)
        combined_df['tradevolume'] = combined_df['netAmount1'] / (10 ** token1_decimals)
    print(f"Using {quote_asset} as quote asset: Price in token0/token1, Volume in token1")
else:
    raise ValueError("quote_asset must be either 'token0' or 'token1'")

## ILLIQ Calculation
# Calculate price impact only for rows where tradevolume != 0
combined_df['last_price_impact'] = np.nan
mask_trading = combined_df['tradevolume'] != 0
combined_df.loc[mask_trading, 'last_price_impact'] = np.abs(combined_df['price'] / combined_df['price'].shift(1) - 1)

# Add absolute tradevolume column next to ILLIQ, only for non-zero values
combined_df['abs_tradevolume'] = np.nan  # Initialize with NaN
mask_abs_volume = combined_df['tradevolume'] != 0
combined_df.loc[mask_abs_volume, 'abs_tradevolume'] = np.abs(combined_df['tradevolume'])

# Add ILLIQ column: (last_price_impact / abs_tradevolume) * 1e6
# Only calculate ILLIQ for rows where we have both price impact and trade volume
mask_illiq = (combined_df['tradevolume'] != 0) & (~combined_df['last_price_impact'].isna())
combined_df['ILLIQ'] = np.nan  # Initialize with NaN
combined_df.loc[mask_illiq, 'ILLIQ'] = (combined_df['last_price_impact'] / combined_df['abs_tradevolume']) * 1e6

# Save the combined DataFrame to the output file
combined_df.to_csv(output_file, index=False)

# Add analysis of price impact vs volume relationship over time
print("\nAnalyzing price impact vs volume relationship over time...")

# Create volume bins for grouping similar sized trades
# We'll create 10 equal-sized bins based on absolute trade volume
volume_bins = pd.qcut(combined_df['abs_tradevolume'].dropna(), q=10, labels=False)
combined_df['volume_bin'] = volume_bins

# Calculate average price impact for each volume bin
bin_analysis = combined_df.groupby('volume_bin').agg({
    'last_price_impact': 'mean',
    'abs_tradevolume': 'mean',
    'timestamp': 'count',
    'ILLIQ': 'mean'
}).reset_index()

# Calculate the price impact per unit of volume for each bin
bin_analysis['price_impact_per_unit'] = bin_analysis['last_price_impact'] / bin_analysis['abs_tradevolume']

# Save the bin analysis results
bin_analysis_output = os.path.join(data_folder, f'price_impact_bin_analysis_{pool_address}.csv')
bin_analysis.to_csv(bin_analysis_output, index=False)
print(f"Price impact bin analysis saved to: {bin_analysis_output}")

# Filter impact metrics - create a simplified version with only essential columns
print("\nFiltering impact metrics...")

# Select only the columns we want for impact metrics analysis
columns_to_keep = ['timestamp', 'last_price_impact', 'ILLIQ', 'abs_tradevolume']
filtered_df = combined_df[columns_to_keep]

# Remove rows where any of these columns are NaN
filtered_df = filtered_df.dropna(subset=['last_price_impact', 'ILLIQ', 'abs_tradevolume'])

# Save the filtered data to a new CSV file
filtered_output_file = os.path.join(data_folder, f'filtered_impact_metrics_{pool_address}.csv')
filtered_df.to_csv(filtered_output_file, index=False)

print(f"Filtered impact metrics data saved to: {filtered_output_file}")
print(f"Number of rows in original combined file: {len(combined_df)}")
print(f"Number of rows in filtered impact metrics file: {len(filtered_df)}")
print(f"Filtered data contains {len(filtered_df)} rows with complete impact metrics data")

