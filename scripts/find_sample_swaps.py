import pandas as pd
import numpy as np
import os

def find_sample_swaps():
    """
    Find 4 sample swaps with different risk profiles and show key metrics only
    """
    
    # Load the fee simulation data
    data_file = "../data/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640/fee_sim_position_and_fee_timeseries.csv"
    
    print("Loading fee simulation data...")
    df = pd.read_csv(data_file)
    
    # Filter for trades with non-zero volume and valid metrics
    df_trades = df[
        (df['abs_trade_volume'] > 0) & 
        (df['ILLIQ'].notna()) & 
        (df['ILLIQ'] > 0) & 
        (df['vpin_used'].notna()) & 
        (df['real_price_impact'].notna())
    ].copy()
    
    # Focus on larger trades (top 25%) for better demonstration
    volume_threshold = df_trades['abs_trade_volume'].quantile(0.75)
    df_large_trades = df_trades[df_trades['abs_trade_volume'] >= volume_threshold].copy()
    
    # Calculate percentiles for each metric using large trades (tertiles for low/medium/high)
    metrics = ['vpin_used', 'ILLIQ', 'real_price_impact', 'inventory_exposure_pos']
    percentiles = {}
    
    for metric in metrics:
        values = df_large_trades[metric].values
        percentiles[metric] = {
            'p33': np.percentile(values, 33.33),
            'p67': np.percentile(values, 66.67)
        }
    
    # Define thresholds for low/medium/high using tertiles
    def classify_metric(value, metric):
        p33 = percentiles[metric]['p33']
        p67 = percentiles[metric]['p67']
        if value >= p67:
            return 'high'
        elif value <= p33:
            return 'low'
        else:
            return 'medium'
    
    # Print tertile thresholds for reference
    print("\nTertile thresholds (33rd/67th percentiles):")
    for metric in metrics:
        p33 = percentiles[metric]['p33']
        p67 = percentiles[metric]['p67']
        print(f"{metric:<25}: Low ≤ {p33:.4f} < Medium ≤ {p67:.4f} < High")
    
    # Add classifications
    for metric in metrics:
        df_large_trades[f'{metric}_class'] = df_large_trades[metric].apply(lambda x: classify_metric(x, metric))
    
    # Use very broad trade size range to find perfect matches (including smaller trades)
    # For boring day, we want to find the absolute lowest VPIN fee possible
    target_volume = df_large_trades['abs_trade_volume'].quantile(0.85)
    volume_tolerance = target_volume * 1.0  # Allow ±100% deviation to include smaller trades
    volume_min = target_volume - volume_tolerance
    volume_max = target_volume + volume_tolerance
    
    # Make sure we don't go below the large trades threshold but allow smaller sizes for boring day
    volume_min = max(volume_min, df_large_trades['abs_trade_volume'].quantile(0.50))  # At least 50th percentile
    
    df_volume_filtered = df_large_trades[
        (df_large_trades['abs_trade_volume'] >= volume_min) & 
        (df_large_trades['abs_trade_volume'] <= volume_max)
    ].copy()
    
    # Define the 4 scenarios with exact tertile-based criteria
    scenarios = [
        {
            'name': 'LP Nightmare, but get Comp.',
            'criteria': {
                'vpin_used_class': 'high',
                'ILLIQ_class': 'high', 
                'real_price_impact_class': 'high',
                'inventory_exposure_pos_class': 'high'
            }
        },
        {
            'name': 'Still competitive since VPIN low',
            'criteria': {
                'vpin_used_class': 'low',
                'ILLIQ_class': 'medium',
                'real_price_impact_class': 'medium', 
                'inventory_exposure_pos_class': 'medium'
            }
        },
        {
            'name': 'Beating CEXs',
            'criteria': {
                'vpin_used_class': 'medium',
                'ILLIQ_class': 'low',
                'real_price_impact_class': 'low',
                'inventory_exposure_pos_class': 'medium'
            }
        },
        {
            'name': 'boring day',
            'criteria': {
                'vpin_used_class': 'low',
                'ILLIQ_class': 'low',
                'real_price_impact_class': 'low',
                'inventory_exposure_pos_class': 'low'
            }
        }
    ]
    
    # Find samples for each scenario
    sample_swaps = []
    
    for scenario in scenarios:
        # Filter for this scenario
        scenario_df = df_volume_filtered.copy()
        for col, value in scenario['criteria'].items():
            scenario_df = scenario_df[scenario_df[col] == value]
        
        if len(scenario_df) > 0:
            if scenario['name'] == 'LP Nightmare, but get Comp.':
                # For LP nightmare, find high values but not the absolute maximum
                # Target around 90th percentile of each metric within the high category
                target_metrics = ['vpin_used', 'ILLIQ', 'real_price_impact', 'inventory_exposure_pos']
                scenario_df['distance_from_target'] = 0
                
                for metric in target_metrics:
                    high_threshold = percentiles[metric]['p67']
                    max_val = df_large_trades[metric].max()
                    # Target 90th percentile between high threshold and max
                    target_val = high_threshold + 0.9 * (max_val - high_threshold)
                    scenario_df['distance_from_target'] += abs(scenario_df[metric] - target_val)
                
                best_match = scenario_df.loc[scenario_df['distance_from_target'].idxmin()]
                
            elif scenario['name'] == 'boring day':
                # For boring day, find low values but not the absolute minimum
                # Target around 15-25th percentile of each metric within the low category
                target_metrics = ['vpin_used', 'ILLIQ', 'real_price_impact', 'inventory_exposure_pos']
                scenario_df['distance_from_target'] = 0
                
                for metric in target_metrics:
                    low_threshold = percentiles[metric]['p33']
                    min_val = df_large_trades[metric].min()
                    # Target 20th percentile between min and low threshold
                    target_val = min_val + 0.2 * (low_threshold - min_val)
                    scenario_df['distance_from_target'] += abs(scenario_df[metric] - target_val)
                
                best_match = scenario_df.loc[scenario_df['distance_from_target'].idxmin()]
                
            else:
                # For other scenarios, pick the trade closest to target volume
                scenario_df['volume_diff'] = abs(scenario_df['abs_trade_volume'] - target_volume)
                best_match = scenario_df.loc[scenario_df['volume_diff'].idxmin()]
                
            sample_swaps.append((scenario['name'], best_match))
        else:
            # No perfect match found - record as missing
            sample_swaps.append((f"{scenario['name']} (NO MATCH)", None))
    
    # Prepare data for CSV export
    csv_data = []
    for scenario_name, trade in sample_swaps:
        if trade is not None:
            csv_data.append({
                'Scenario': scenario_name,
                'Trade_Size_K': round(trade['abs_trade_volume']/1000, 0),
                'Trade_Size_Absolute': trade['abs_trade_volume'],
                'VPIN': round(trade['vpin_used'], 3),
                'VPIN_Category': trade['vpin_used_class'],
                'ILLIQ': round(trade['ILLIQ'], 3),
                'ILLIQ_Category': trade['ILLIQ_class'],
                'Real_Price_Impact': round(trade['real_price_impact'], 4),
                'Price_Impact_Category': trade['real_price_impact_class'],
                'Inventory_Exposure': round(trade['inventory_exposure_pos'], 3),
                'Inventory_Category': trade['inventory_exposure_pos_class'],
                'Base_Fee_Pct': 0.05,
                'VPIN_Fee_Pct': round((trade['vpin_fee_absolute']/trade['abs_trade_volume'])*100, 3),
                'Total_Fee_Pct': round(trade['fee_pct_of_volume']*100, 3),
                'Base_Fee_Absolute': round(trade['base_fee'], 2),
                'VPIN_Fee_Absolute': round(trade['vpin_fee_absolute'], 2),
                'Total_Fee_Absolute': round(trade['total_fee'], 2),
                'Timestamp': trade['timestamp']
            })
    
    # Export to CSV in the pool-specific folder
    csv_df = pd.DataFrame(csv_data)
    pool_address = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
    output_file = f"../data/{pool_address}/dynamic_fee_examples_{pool_address}.csv"
    csv_df.to_csv(output_file, index=False)
    
    # Display results in clean format
    print("\n" + "="*80)
    print("DYNAMIC FEE EXAMPLES - KEY METRICS")
    print("="*80)
    print(f"{'Scenario':<25} {'Trade Size':<12} {'VPIN':<8} {'ILLIQ':<8} {'Price Impact':<12} {'Inventory':<10} {'VPIN Fee':<10} {'Total Fee':<10}")
    print("-"*80)
    
    for scenario_name, trade in sample_swaps:
        if trade is not None:
            trade_size = f"{trade['abs_trade_volume']/1000:.0f}k"
            vpin = f"{trade['vpin_used']:.3f}"
            illiq = f"{trade['ILLIQ']:.3f}"
            price_impact = f"{trade['real_price_impact']:.4f}"
            inventory = f"{trade['inventory_exposure_pos']:.3f}"
            vpin_fee = f"{(trade['vpin_fee_absolute']/trade['abs_trade_volume'])*100:.3f}%"
            total_fee = f"{trade['fee_pct_of_volume']*100:.3f}%"
            
            print(f"{scenario_name:<25} {trade_size:<12} {vpin:<8} {illiq:<8} {price_impact:<12} {inventory:<10} {vpin_fee:<10} {total_fee:<10}")
        else:
            print(f"{scenario_name:<25} {'N/A':<12} {'N/A':<8} {'N/A':<8} {'N/A':<12} {'N/A':<10} {'N/A':<10} {'N/A':<10}")
    
    print(f"\nResults exported to: {output_file}")
    return sample_swaps

if __name__ == "__main__":
    find_sample_swaps() 