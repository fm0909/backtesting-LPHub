import pandas as pd
import numpy as np
import os
from datetime import datetime

def calculate_vpin(input_file_path, output_file_path=None):
    """
    Calculate VPIN (Volume-synchronized Probability of Informed Trading) for multiple sample lengths.
    
    Args:
        input_file_path: Path to the all_days_combined CSV file
        output_file_path: Path for the output file (optional)
    
    Returns:
        DataFrame with VPIN calculations for daily, 5-day, and 7-day periods.
    """
    
    print(f"Loading data from: {input_file_path}")
    
    # Load the data
    df = pd.read_csv(input_file_path)
    
    # Filter out rows with zero trade volume
    df = df[df['tradevolume'] != 0].copy()
    df = df.reset_index(drop=True)
    
    print(f"Total trades with non-zero volume: {len(df)}")
    
    # Calculate average daily trading volume
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_volume = df.groupby('date')['abs_tradevolume'].sum()
    avg_daily_volume = daily_volume.mean()
    
    print(f"Average daily trading volume: {avg_daily_volume:.6f}")
    
    # Calculate bucket size (average daily volume / 50)
    bucket_size = avg_daily_volume / 50
    print(f"Bucket size: {bucket_size:.6f}")
    
    # Initialize variables for VPIN calculation
    current_bucket_abs_volume = 0.0
    current_bucket_net_volume = 0.0
    
    # VPIN configurations: daily (50), 5-day (250), 7-day (350)
    sample_lengths = {'vpin_daily': 50, 'vpin_5day': 250, 'vpin_7day': 350}
    bucket_imbalances_map = {key: [] for key in sample_lengths.keys()}

    bucket_details = []  # For debugging and output
    
    # Process each trade
    for idx, row in df.iterrows():
        trade_volume = row['tradevolume']
        abs_trade_volume = abs(trade_volume)
        
        # Handle trades that might fill multiple buckets
        remaining_volume = abs_trade_volume
        remaining_net_volume = trade_volume
        
        while remaining_volume > 0:
            # Calculate how much volume fits in current bucket
            volume_needed_for_bucket = bucket_size - current_bucket_abs_volume
            volume_to_add = min(remaining_volume, volume_needed_for_bucket)
            
            # Calculate the proportion of net volume to add
            proportion = volume_to_add / abs_trade_volume
            net_volume_to_add = remaining_net_volume * proportion
            
            # Add to current bucket
            current_bucket_abs_volume += volume_to_add
            current_bucket_net_volume += net_volume_to_add
            
            # Update remaining volumes
            remaining_volume -= volume_to_add
            remaining_net_volume -= net_volume_to_add
            
            # Check if bucket is full
            if current_bucket_abs_volume >= bucket_size:
                # Calculate order imbalance for this bucket
                order_imbalance = abs(current_bucket_net_volume) / bucket_size
                
                # Calculate VPIN for each sample length
                vpin_values = {}
                for key, sample_length in sample_lengths.items():
                    imbalances = bucket_imbalances_map[key]
                    imbalances.append(order_imbalance)
                    if len(imbalances) > sample_length:
                        imbalances.pop(0)
                    vpin_values[key] = np.mean(imbalances) if len(imbalances) > 0 else np.nan
                
                # Store bucket details for output
                details = {
                    'trade_index': idx,
                    'timestamp': row['timestamp'],
                    'bucket_start_trade': idx - (len(bucket_details) if bucket_details else 0),
                    'bucket_abs_volume': current_bucket_abs_volume,
                    'bucket_net_volume': current_bucket_net_volume,
                    'order_imbalance': order_imbalance,
                    'bucket_number': len(bucket_details)
                }
                details.update(vpin_values)
                bucket_details.append(details)
                
                # Reset bucket
                current_bucket_abs_volume = 0.0
                current_bucket_net_volume = 0.0
    
    # Handle any remaining volume in the last bucket
    if current_bucket_abs_volume > 0:
        order_imbalance = abs(current_bucket_net_volume) / bucket_size
        
        # Calculate VPIN for each sample length for the final bucket
        vpin_values = {}
        for key, sample_length in sample_lengths.items():
            imbalances = bucket_imbalances_map[key]
            imbalances.append(order_imbalance)
            if len(imbalances) > sample_length:
                imbalances.pop(0)
            vpin_values[key] = np.mean(imbalances) if len(imbalances) > 0 else np.nan
        
        details = {
            'trade_index': len(df) - 1,
            'timestamp': df.iloc[-1]['timestamp'],
            'bucket_start_trade': len(df) - 1,
            'bucket_abs_volume': current_bucket_abs_volume,
            'bucket_net_volume': current_bucket_net_volume,
            'order_imbalance': order_imbalance,
            'bucket_number': len(bucket_details)
        }
        details.update(vpin_values)
        bucket_details.append(details)
    
    # Create output DataFrame
    vpin_df = pd.DataFrame(bucket_details)
    
    # Add summary statistics
    print(f"\nVPIN Calculation Summary:")
    print(f"Total buckets created: {len(vpin_df)}")
    print(f"Average order imbalance: {vpin_df['order_imbalance'].mean():.6f}")
    
    for key in sample_lengths.keys():
        if key in vpin_df.columns:
            print(f"Final {key.replace('_', ' ')} value: {vpin_df[key].iloc[-1]:.6f}")
            print(f"{key.replace('_', ' ')} range: {vpin_df[key].min():.6f} - {vpin_df[key].max():.6f}")

    # Save to file
    if output_file_path is None:
        # Generate output filename based on input
        input_dir = os.path.dirname(input_file_path)
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_path = os.path.join(input_dir, f"{base_name}_vpin_analysis.csv")
    
    vpin_df.to_csv(output_file_path, index=False)
    print(f"\nVPIN analysis saved to: {output_file_path}")
    
    return vpin_df

def main():
    """
    Main function to run VPIN calculation on the specified pool data
    """
    # Specify the pool address
    pool_address = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
    
    # Construct input file path
    input_file = os.path.join('data', pool_address, f'all_days_combined_{pool_address}.csv')
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    # Run VPIN calculation
    vpin_results = calculate_vpin(input_file)
    
    # Print first few rows for verification
    print(f"\nFirst 5 buckets:")
    print(vpin_results.head().to_string(index=False))
    
    print(f"\nLast 5 buckets:")
    print(vpin_results.tail().to_string(index=False))

if __name__ == "__main__":
    main() 