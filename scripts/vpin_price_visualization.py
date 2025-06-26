import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import numpy as np

def load_and_prepare_data(pool_address):
    """
    Load VPIN analysis data and original price data, then merge them.
    
    Args:
        pool_address: The pool address to analyze
    
    Returns:
        DataFrame with VPIN values and price data merged
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(script_dir)
    
    # Load VPIN analysis data
    vpin_file = os.path.join(project_root, 'data', pool_address, f'all_days_combined_{pool_address}_vpin_analysis.csv')
    vpin_df = pd.read_csv(vpin_file)
    
    # Load original price data
    price_file = os.path.join(project_root, 'data', pool_address, f'all_days_combined_{pool_address}.csv')
    price_df = pd.read_csv(price_file)
    
    # Convert timestamps to datetime
    vpin_df['timestamp'] = pd.to_datetime(vpin_df['timestamp'])
    price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])
    
    # Filter out rows with zero trade volume from price data
    price_df = price_df[price_df['tradevolume'] != 0].copy()
    price_df = price_df.reset_index(drop=True)
    
    print(f"VPIN data shape: {vpin_df.shape}")
    print(f"Price data shape: {price_df.shape}")
    
    # Merge VPIN data with price data based on trade_index
    # We'll use the trade_index from VPIN data to get corresponding price data
    merged_data = []
    
    for idx, vpin_row in vpin_df.iterrows():
        trade_idx = vpin_row['trade_index']
        if trade_idx < len(price_df):
            price_row = price_df.iloc[trade_idx]
            merged_row = {
                'timestamp': vpin_row['timestamp'],
                'trade_index': trade_idx,
                'price': price_row['price'],
                'vpin_daily': vpin_row['vpin_daily'],
                'vpin_5day': vpin_row['vpin_5day'],
                'vpin_7day': vpin_row['vpin_7day'],
                'order_imbalance': vpin_row['order_imbalance'],
                'bucket_number': vpin_row['bucket_number']
            }
            merged_data.append(merged_row)
    
    merged_df = pd.DataFrame(merged_data)
    print(f"Merged data shape: {merged_df.shape}")
    
    return merged_df

def create_vpin_price_plot(merged_df, pool_address, output_dir=None):
    """
    Create a comprehensive plot showing VPIN values and price development over time on the same graph.
    
    Args:
        merged_df: DataFrame with VPIN and price data
        pool_address: Pool address for title
        output_dir: Directory to save the plot
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(script_dir)
    
    # Convert cm to inches (1 inch = 2.54 cm)
    width_inches = 16 / 2.54
    height_inches = 7 / 2.54
    
    # Create figure with dual y-axes
    fig, ax1 = plt.subplots(figsize=(width_inches, height_inches))
    
    # Plot price on primary y-axis (left)
    color1 = '#1f77b4'  # Blue color
    ax1.plot(merged_df['timestamp'], merged_df['price'], 
             color=color1, linewidth=2, alpha=0.9, label='Price')
    ax1.set_ylabel('Price', color=color1, fontsize=10, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1, labelsize=9)
    
    # Create secondary y-axis for VPIN values (right)
    ax2 = ax1.twinx()
    
    # Plot VPIN values on secondary y-axis (right)
    ax2.plot(merged_df['timestamp'], merged_df['vpin_daily'], 
             color='#d62728', linewidth=2, alpha=0.9, label='VPIN Daily')
    ax2.plot(merged_df['timestamp'], merged_df['vpin_5day'], 
             color='#ff7f0e', linewidth=2, alpha=0.9, label='VPIN 5-Day')
    ax2.plot(merged_df['timestamp'], merged_df['vpin_7day'], 
             color='#2ca02c', linewidth=2, alpha=0.9, label='VPIN 7-Day')
    
    ax2.set_ylabel('VPIN Value', color='#d62728', fontsize=10, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#d62728', labelsize=9)
    
    # Set title and labels
    # ax1.set_title(f'Price and VPIN Analysis - Pool {pool_address[:10]}...', fontsize=12, fontweight='bold', pad=15)
    # ax1.set_xlabel('Date', fontsize=10, fontweight='bold')
    ax1.tick_params(axis='x', labelsize=8)
    
    # Format x-axis for better readability
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add subtle grid
    ax1.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    
    # Combine legends from both axes with better positioning
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
              bbox_to_anchor=(0.02, 0.98), fontsize=8, framealpha=0.9)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot with high DPI for presentation quality
    if output_dir is None:
        output_dir = os.path.join(project_root, 'data', pool_address)
    
    output_file = os.path.join(output_dir, f'vpin_price_analysis_{pool_address}_presentation.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"VPIN-Price analysis plot saved to: {output_file}")
    
    plt.show()

def main():
    """
    Main function to run VPIN-Price visualization analysis
    """
    # Specify the pool address
    pool_address = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
    
    print(f"Loading and preparing data for pool: {pool_address}")
    
    try:
        # Load and prepare data
        merged_df = load_and_prepare_data(pool_address)
        
        if merged_df.empty:
            print("No data to plot. Exiting.")
            return
        
        # Create VPIN-Price plot
        print("Creating VPIN-Price analysis plot...")
        create_vpin_price_plot(merged_df, pool_address)
        
        # Print summary statistics
        print(f"\nSummary Statistics for Pool {pool_address}:")
        print(f"Date range: {merged_df['timestamp'].min()} to {merged_df['timestamp'].max()}")
        print(f"Total buckets: {len(merged_df)}")
        print(f"Average VPIN Daily: {merged_df['vpin_daily'].mean():.4f}")
        print(f"Average VPIN 5-Day: {merged_df['vpin_5day'].mean():.4f}")
        print(f"Average VPIN 7-Day: {merged_df['vpin_7day'].mean():.4f}")
        print(f"Price range: {merged_df['price'].min():.2e} to {merged_df['price'].max():.2e}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 