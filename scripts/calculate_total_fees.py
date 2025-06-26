import pandas as pd
import numpy as np
import os

def calculate_total_fees_earned(csv_file_path):
    """
    Calculate total fees earned in absolute amounts from the fee simulation data.
    
    Args:
        csv_file_path: Path to the fee_sim_position_and_fee_timeseries.csv file
    """
    
    print(f"Loading data from {csv_file_path}...")
    
    # Load the data
    df = pd.read_csv(csv_file_path)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter for rows where abs_trade_volume > 0 (only actual trades)
    df_trades = df[df['abs_trade_volume'] > 0].copy()
    
    print(f"Total rows: {len(df)}")
    print(f"Rows with trade volume > 0: {len(df_trades)}")
    print(f"Date range: {df_trades['timestamp'].min()} to {df_trades['timestamp'].max()}")
    
    # Calculate total fees earned
    total_base_fees = df_trades['base_fee'].sum()
    total_vpin_fees = df_trades['vpin_fee_absolute'].sum()
    total_fees = df_trades['total_fee'].sum()
    
    # Calculate total trade volume
    total_trade_volume = df_trades['abs_trade_volume'].sum()
    
    # Calculate average fees per trade
    avg_base_fee_per_trade = df_trades['base_fee'].mean()
    avg_vpin_fee_per_trade = df_trades['vpin_fee_absolute'].mean()
    avg_total_fee_per_trade = df_trades['total_fee'].mean()
    
    # Calculate fee percentages of total volume
    base_fee_pct_of_total_volume = (total_base_fees / total_trade_volume) * 100
    vpin_fee_pct_of_total_volume = (total_vpin_fees / total_trade_volume) * 100
    total_fee_pct_of_total_volume = (total_fees / total_trade_volume) * 100
    
    # Calculate statistics
    fee_stats = {
        'total_trades': len(df_trades),
        'total_trade_volume': total_trade_volume,
        'total_base_fees': total_base_fees,
        'total_vpin_fees': total_vpin_fees,
        'total_fees': total_fees,
        'avg_base_fee_per_trade': avg_base_fee_per_trade,
        'avg_vpin_fee_per_trade': avg_vpin_fee_per_trade,
        'avg_total_fee_per_trade': avg_total_fee_per_trade,
        'base_fee_pct_of_total_volume': base_fee_pct_of_total_volume,
        'vpin_fee_pct_of_total_volume': vpin_fee_pct_of_total_volume,
        'total_fee_pct_of_total_volume': total_fee_pct_of_total_volume
    }
    
    # Print results
    print("\n" + "=" * 80)
    print("TOTAL FEES EARNED ANALYSIS")
    print("=" * 80)
    
    print(f"\n📊 TRADE SUMMARY:")
    print(f"  Total Trades: {fee_stats['total_trades']:,}")
    print(f"  Total Trade Volume: {fee_stats['total_trade_volume']:,.2f}")
    
    print(f"\n💰 ABSOLUTE FEE AMOUNTS:")
    print(f"  Total Base Fees: {fee_stats['total_base_fees']:,.6f}")
    print(f"  Total VPIN Fees: {fee_stats['total_vpin_fees']:,.6f}")
    print(f"  Total Fees: {fee_stats['total_fees']:,.6f}")
    
    print(f"\n📈 AVERAGE FEES PER TRADE:")
    print(f"  Avg Base Fee per Trade: {fee_stats['avg_base_fee_per_trade']:,.6f}")
    print(f"  Avg VPIN Fee per Trade: {fee_stats['avg_vpin_fee_per_trade']:,.6f}")
    print(f"  Avg Total Fee per Trade: {fee_stats['avg_total_fee_per_trade']:,.6f}")
    
    print(f"\n📊 FEES AS PERCENTAGE OF TOTAL VOLUME:")
    print(f"  Base Fees: {fee_stats['base_fee_pct_of_total_volume']:.4f}%")
    print(f"  VPIN Fees: {fee_stats['vpin_fee_pct_of_total_volume']:.4f}%")
    print(f"  Total Fees: {fee_stats['total_fee_pct_of_total_volume']:.4f}%")
    
    # Calculate fee breakdown
    base_fee_contribution = (total_base_fees / total_fees) * 100
    vpin_fee_contribution = (total_vpin_fees / total_fees) * 100
    
    print(f"\n🔍 FEE BREAKDOWN:")
    print(f"  Base Fee Contribution: {base_fee_contribution:.2f}%")
    print(f"  VPIN Fee Contribution: {vpin_fee_contribution:.2f}%")
    
    # Daily fee analysis
    print(f"\n📅 DAILY FEE ANALYSIS:")
    df_trades['date'] = df_trades['timestamp'].dt.date
    daily_fees = df_trades.groupby('date').agg({
        'total_fee': 'sum',
        'base_fee': 'sum',
        'vpin_fee_absolute': 'sum',
        'abs_trade_volume': 'sum'
    }).reset_index()
    
    print(f"  Total Days: {len(daily_fees)}")
    print(f"  Avg Daily Total Fees: {daily_fees['total_fee'].mean():,.6f}")
    print(f"  Avg Daily Base Fees: {daily_fees['base_fee'].mean():,.6f}")
    print(f"  Avg Daily VPIN Fees: {daily_fees['vpin_fee_absolute'].mean():,.6f}")
    print(f"  Avg Daily Trade Volume: {daily_fees['abs_trade_volume'].mean():,.2f}")
    
    # Top fee days
    top_fee_days = daily_fees.nlargest(5, 'total_fee')
    print(f"\n🏆 TOP 5 FEE DAYS:")
    for idx, row in top_fee_days.iterrows():
        print(f"  {row['date']}: {row['total_fee']:,.6f} (Base: {row['base_fee']:,.6f}, VPIN: {row['vpin_fee_absolute']:,.6f})")
    
    return fee_stats, daily_fees

def main():
    """
    Main function to calculate total fees earned
    """
    print("=" * 80)
    print("TOTAL FEES EARNED CALCULATION")
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
    
    # Calculate total fees
    fee_stats, daily_fees = calculate_total_fees_earned(csv_file)
    
    print("\n" + "=" * 80)
    print("CALCULATION COMPLETE")
    print("=" * 80)
    print(f"✓ Total fees calculated successfully")
    print(f"✓ Daily breakdown provided")
    print(f"✓ Fee statistics compiled")

if __name__ == "__main__":
    main() 