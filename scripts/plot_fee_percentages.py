import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
from datetime import datetime

def plot_fee_percentages_over_time(csv_file_path, output_path=None):
    """
    Plot total fee and VPIN fee as percentages over time.
    Only includes data points where abs_trade_volume > 0.
    
    Args:
        csv_file_path: Path to the fee_sim_position_and_fee_timeseries.csv file
        output_path: Path to save the plot (optional)
    """
    
    print(f"Loading data from {csv_file_path}...")
    
    # Load the data
    df = pd.read_csv(csv_file_path)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter for rows where abs_trade_volume > 0
    df_filtered = df[df['abs_trade_volume'] > 0].copy()
    
    print(f"Total rows: {len(df)}")
    print(f"Rows with trade volume > 0: {len(df_filtered)}")
    print(f"Date range: {df_filtered['timestamp'].min()} to {df_filtered['timestamp'].max()}")
    
    # Convert fee percentages to actual percentages (multiply by 100)
    df_filtered['total_fee_pct'] = df_filtered['fee_pct_of_volume'] * 100
    df_filtered['vpin_fee_pct'] = df_filtered['vpin_fee_pct_of_volume'] * 100
    
    # Calculate statistics
    total_fee_stats = {
        'mean': df_filtered['total_fee_pct'].mean(),
        'median': df_filtered['total_fee_pct'].median(),
        'std': df_filtered['total_fee_pct'].std(),
        'min': df_filtered['total_fee_pct'].min(),
        'max': df_filtered['total_fee_pct'].max()
    }
    
    vpin_fee_stats = {
        'mean': df_filtered['vpin_fee_pct'].mean(),
        'median': df_filtered['vpin_fee_pct'].median(),
        'std': df_filtered['vpin_fee_pct'].std(),
        'min': df_filtered['vpin_fee_pct'].min(),
        'max': df_filtered['vpin_fee_pct'].max()
    }
    
    print(f"\nTotal Fee Statistics (%):")
    print(f"  Mean: {total_fee_stats['mean']:.4f}%")
    print(f"  Median: {total_fee_stats['median']:.4f}%")
    print(f"  Std Dev: {total_fee_stats['std']:.4f}%")
    print(f"  Range: {total_fee_stats['min']:.4f}% - {total_fee_stats['max']:.4f}%")
    
    print(f"\nVPIN Fee Statistics (%):")
    print(f"  Mean: {vpin_fee_stats['mean']:.4f}%")
    print(f"  Median: {vpin_fee_stats['median']:.4f}%")
    print(f"  Std Dev: {vpin_fee_stats['std']:.4f}%")
    print(f"  Range: {vpin_fee_stats['min']:.4f}% - {vpin_fee_stats['max']:.4f}%")
    
    # Create the plot
    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    
    # Plot 1: Total Fee Percentage over time
    ax1.scatter(df_filtered['timestamp'], df_filtered['total_fee_pct'], 
                alpha=0.5, s=15, color='blue', label='Total Fee %')
    
    # Add mean line
    ax1.axhline(y=total_fee_stats['mean'], color='red', linestyle='--', 
                linewidth=1.5, label=f'Mean: {total_fee_stats["mean"]:.3f}%')
    
    ax1.set_ylabel('Total Fee (%)', fontsize=11, fontweight='bold')
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(True, alpha=0.2)
    
    # Format y-axis to show percentages clearly
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.2f}%'))
    
    # Plot 2: VPIN Fee Percentage over time
    ax2.scatter(df_filtered['timestamp'], df_filtered['vpin_fee_pct'], 
                alpha=0.5, s=15, color='green', label='VPIN Fee %')
    
    # Add mean line
    ax2.axhline(y=vpin_fee_stats['mean'], color='red', linestyle='--', 
                linewidth=1.5, label=f'Mean: {vpin_fee_stats["mean"]:.3f}%')
    
    ax2.set_ylabel('VPIN Fee (%)', fontsize=11, fontweight='bold')
    ax2.legend(fontsize=9, loc='upper right')
    ax2.grid(True, alpha=0.2)
    
    # Format y-axis to show percentages clearly
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.2f}%'))
    
    # Format x-axis dates - show fewer dates for cleaner look
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=14))  # Show every 14 days
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
    
    # Remove x-axis label but keep the dates
    ax2.set_xlabel('')
    
    # Adjust layout to be more compact
    plt.tight_layout(pad=2.0)
    
    # Save the plot
    if output_path is None:
        # Auto-generate output path
        data_dir = os.path.dirname(csv_file_path)
        pool_address = os.path.basename(os.path.dirname(csv_file_path))
        output_path = os.path.join(data_dir, f'fee_percentages_over_time_{pool_address}.png')
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {output_path}")
    
    # Close the plot to free memory
    plt.close()
    
    return df_filtered, total_fee_stats, vpin_fee_stats

def main():
    """
    Main function to run the fee percentage plotting
    """
    print("=" * 80)
    print("FEE PERCENTAGE PLOTTING - PRESENTATION FRIENDLY")
    print("=" * 80)
    
    # Configuration - change pool address as needed
    POOL_ADDRESS = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Input file path
    csv_file = os.path.join(project_root, f"data/{POOL_ADDRESS}/fee_sim_position_and_fee_timeseries.csv")
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        return
    
    # Run the plotting
    df_filtered, total_stats, vpin_stats = plot_fee_percentages_over_time(csv_file)
    
    print("\n" + "=" * 80)
    print("PLOTTING COMPLETE")
    print("=" * 80)
    print(f"✓ Data loaded and filtered successfully")
    print(f"✓ Plots generated with presentation-friendly styling")
    print(f"✓ Statistics calculated and displayed")

if __name__ == "__main__":
    main() 