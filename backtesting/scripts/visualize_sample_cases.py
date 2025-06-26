import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def visualize_sample_cases():
    """
    Create horizontal bar chart visualization for dynamic fee sample cases
    """
    
    # Load the sample cases data
    pool_address = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
    data_file = f"../data/{pool_address}/dynamic_fee_examples_{pool_address}.csv"
    
    if not os.path.exists(data_file):
        print(f"Error: Sample cases file not found: {data_file}")
        print("Please run find_sample_swaps.py first to generate the sample cases.")
        return
    
    df = pd.read_csv(data_file)
    
    # Reorder scenarios as requested: Beating CEXs, Still competitive since VPIN low, LP Nightmare but get Comp., boring day
    scenario_order = ['Beating CEXs', 'Still competitive since VPIN low', 'LP Nightmare, but get Comp.', 'boring day']
    df['Scenario_Order'] = df['Scenario'].map({scenario: i for i, scenario in enumerate(scenario_order)})
    df = df.sort_values('Scenario_Order').drop('Scenario_Order', axis=1).reset_index(drop=True)
    
    # Define the metrics to visualize
    metrics = {
        'VPIN': 'VPIN',
        'ILLIQ': 'ILLIQ',
        'Real_Price_Impact': 'Real_Price_Impact',
        'Inventory_Exposure': 'Inventory_Exposure',
        'VPIN_Fee_Pct': 'VPIN_Fee_Pct',
        'Total_Fee_Pct': 'Total_Fee_Pct'
    }
    
    # Calculate min/max values for each metric across all samples
    metric_ranges = {}
    for metric_key, metric_col in metrics.items():
        metric_ranges[metric_key] = {
            'min': df[metric_col].min(),
            'max': df[metric_col].max(),
            'range': df[metric_col].max() - df[metric_col].min()
        }
    
    # Create the visualization - custom dimensions (20.5cm x 17.15cm)
    fig, axes = plt.subplots(2, 2, figsize=(8.07, 6.75))  # 20.5cm = 8.07", 17.15cm = 6.75"
    axes = axes.flatten()  # Convert 2x2 grid to 1D array for easier indexing
    
    # Color scheme will be determined dynamically based on metric and value
    
    for i, (idx, row) in enumerate(df.iterrows()):
        ax = axes[i]
        
        # Prepare data for this scenario
        scenario = row['Scenario']
        y_positions = np.arange(len(metrics))
        
        # Create horizontal bars for each metric
        for j, (metric_key, metric_col) in enumerate(metrics.items()):
            # Get min, max, and current value
            min_val = metric_ranges[metric_key]['min']
            max_val = metric_ranges[metric_key]['max']
            current_val = row[metric_col]
            
            # Calculate the "fill" percentage
            if metric_ranges[metric_key]['range'] > 0:
                fill_pct = (current_val - min_val) / metric_ranges[metric_key]['range']
            else:
                fill_pct = 1.0  # If all values are the same
            
            # Determine color based on metric type and fill percentage
            if metric_key in ['VPIN_Fee_Pct', 'Total_Fee_Pct']:
                # White to green for fees (lower fees = better = whiter)
                green_intensity = fill_pct
                bar_color = (1 - green_intensity * 0.8, 1, 1 - green_intensity * 0.8)  # White to green
            elif metric_key in ['VPIN', 'Real_Price_Impact', 'Inventory_Exposure']:
                # White to red for VPIN, Price Impact, and Inventory (higher = worse = redder)
                red_intensity = fill_pct
                bar_color = (1, 1 - red_intensity * 0.8, 1 - red_intensity * 0.8)  # White to red
            elif metric_key == 'ILLIQ':
                # Green to white for ILLIQ (higher ILLIQ = worse = whiter)
                white_intensity = fill_pct
                bar_color = (white_intensity * 0.8, 1, white_intensity * 0.8)  # Green to white
            else:
                bar_color = 'lightblue'  # Fallback color
            
            # Create the background bar (full range)
            ax.barh(j, 1.0, height=0.4, color='lightgray', alpha=0.3, 
                   left=0, edgecolor='gray', linewidth=0.5)
            
            # Create the filled bar (up to current value)
            ax.barh(j, fill_pct, height=0.4, color=bar_color, alpha=0.9, 
                   left=0, edgecolor='gray', linewidth=0.5)
            
            # Format values based on metric type
            if metric_key == 'ILLIQ':
                # ILLIQ stays as decimal
                current_label = f'{current_val:.3f}'
                min_label = f'{min_val:.3f}'
                max_label = f'{max_val:.3f}'
            elif metric_key == 'Real_Price_Impact':
                # Price Impact as basis points (multiply by 10000)
                current_label = f'{current_val*10000:.1f}bp'
                min_label = f'{min_val*10000:.1f}bp'
                max_label = f'{max_val*10000:.1f}bp'
            elif metric_key in ['VPIN_Fee_Pct', 'Total_Fee_Pct']:
                # Fee percentages - multiply by 100 to convert to basis points (0.065% -> 6.5bp)
                current_label = f'{current_val*100:.1f}bp'
                min_label = f'{min_val*100:.1f}bp'
                max_label = f'{max_val*100:.1f}bp'
            else:
                # VPIN and Inventory - convert to percentages
                current_label = f'{current_val*100:.1f}%'
                min_label = f'{min_val*100:.1f}%'
                max_label = f'{max_val*100:.1f}%'
            
            # Add value labels
            ax.text(fill_pct + 0.01, j, current_label, 
                   va='center', ha='left', fontweight='bold', fontsize=8)
        
        # Customize the subplot
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.3, len(metrics) - 0.7)  # Tighter vertical spacing
        ax.set_yticks(y_positions)
        ax.set_yticklabels([
            'VPIN',
            'ILLIQ',
            'Price Impact',
            'Inventory',
            'VPIN Fee (bp)',
            'Total Fee (bp)'
        ], fontsize=9)
        ax.set_xlabel('Min → Max', fontsize=9)
        ax.set_title(f'{scenario}', fontsize=11, fontweight='bold', pad=10)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        
        # Add grid for easier reading
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
    
    # Adjust layout for PowerPoint slide format
    plt.tight_layout(pad=2.0, h_pad=3.0, w_pad=2.0)
    
    # Save the visualization
    output_file = f"../data/{pool_address}/dynamic_fee_sample_visualization_{pool_address}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"Visualization saved to: {output_file}")
    
    # Also create a summary statistics table
    print("\n" + "="*80)
    print("METRIC RANGES ACROSS ALL SAMPLES")
    print("="*80)
    for metric_key, metric_col in metrics.items():
        min_val = metric_ranges[metric_key]['min']
        max_val = metric_ranges[metric_key]['max']
        range_val = metric_ranges[metric_key]['range']
        print(f"{metric_key:<20}: {min_val:.4f} → {max_val:.4f} (range: {range_val:.4f})")
    
    # Close the plot to free memory
    plt.close()
    return df, metric_ranges

if __name__ == "__main__":
    visualize_sample_cases() 