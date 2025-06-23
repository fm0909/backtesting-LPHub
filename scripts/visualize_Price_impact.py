import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import os

def calculate_r2_score(y_true, y_pred):
    """
    Calculate R² score using numpy.
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    return r2

def linear_regression(X, y):
    """
    Perform linear regression using numpy.
    Returns coefficients and intercept.
    """
    # Add bias term
    X_with_bias = np.column_stack([np.ones(X.shape[0]), X])
    
    # Solve normal equation: (X^T X)^(-1) X^T y
    coefficients = np.linalg.inv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y
    
    intercept = coefficients[0]
    slope = coefficients[1]
    
    return slope, intercept

def plot_comprehensive_price_impact_analysis(bin_analysis_df, filtered_df, data_folder, pool_address):
    """
    Generates and saves a comprehensive price impact analysis plot.
    """
    fig = plt.figure(figsize=(22, 20))
    gs = gridspec.GridSpec(3, 3, figure=fig)
    fig.suptitle(f'Comprehensive Price Impact Analysis for Pool: {pool_address}', fontsize=18, y=0.95)

    # Plot 1: Price Impact vs Trade Volume
    ax1 = fig.add_subplot(gs[0, 0])
    scatter = ax1.scatter(bin_analysis_df['abs_tradevolume'], bin_analysis_df['last_price_impact'], 
                          c=bin_analysis_df.index, cmap='viridis', s=bin_analysis_df['timestamp']/10)
    ax1.set_title('Price Impact vs Trade Volume\n(Size = Trade Count)')
    ax1.set_xlabel('Average Trade Volume')
    ax1.set_ylabel('Average Price Impact')
    fig.colorbar(scatter, ax=ax1, label='Volume Bin')

    # Plot 2: Price Impact Efficiency by Volume Bin
    ax2 = fig.add_subplot(gs[0, 1])
    sns.barplot(x=bin_analysis_df.index, y=bin_analysis_df['price_impact_per_unit'], hue=bin_analysis_df.index, palette='viridis', ax=ax2, legend=False)
    ax2.set_title('Price Impact Efficiency by Volume Bin')
    ax2.set_xlabel('Volume Bin')
    ax2.set_ylabel('Price Impact per Unit Volume')

    # Plot 3: ILLIQ by Volume Bin
    ax3 = fig.add_subplot(gs[0, 2])
    sns.lineplot(x=bin_analysis_df.index, y=bin_analysis_df['ILLIQ'], marker='o', color='r', ax=ax3)
    ax3.set_title('ILLIQ by Volume Bin')
    ax3.set_xlabel('Volume Bin')
    ax3.set_ylabel('ILLIQ')

    # Plot 4: Trade Count Distribution by Volume Bin
    ax4 = fig.add_subplot(gs[1, 0])
    sns.barplot(x=bin_analysis_df.index, y=bin_analysis_df['timestamp'], hue=bin_analysis_df.index, palette='viridis', ax=ax4, legend=False)
    ax4.set_title('Trade Count Distribution by Volume Bin')
    ax4.set_xlabel('Volume Bin')
    ax4.set_ylabel('Number of Trades')

    # Plot 5: Average Trade Volume by Bin
    ax5 = fig.add_subplot(gs[1, 1])
    sns.barplot(x=bin_analysis_df.index, y=bin_analysis_df['abs_tradevolume'], hue=bin_analysis_df.index, palette='viridis', ax=ax5, legend=False)
    ax5.set_title('Average Trade Volume by Bin')
    ax5.set_xlabel('Volume Bin')
    ax5.set_ylabel('Average Trade Volume')

    # Plot 6: Average Price Impact by Bin
    ax6 = fig.add_subplot(gs[1, 2])
    sns.barplot(x=bin_analysis_df.index, y=bin_analysis_df['last_price_impact'], hue=bin_analysis_df.index, palette='viridis', ax=ax6, legend=False)
    ax6.set_title('Average Price Impact by Bin')
    ax6.set_xlabel('Volume Bin')
    ax6.set_ylabel('Average Price Impact')

    # Plot 7: Price Impact vs Volume (Log-Log Scale)
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(bin_analysis_df['abs_tradevolume'], bin_analysis_df['last_price_impact'], marker='o', linestyle='-')
    ax7.set_xscale('log')
    ax7.set_yscale('log')
    ax7.set_title('Price Impact vs Volume (Log-Log Scale)')
    ax7.set_xlabel('Average Trade Volume (log scale)')
    ax7.set_ylabel('Average Price Impact (log scale)')

    # Plot 8: ILLIQ vs Price Impact
    ax8 = fig.add_subplot(gs[2, 1])
    scatter2 = ax8.scatter(bin_analysis_df['last_price_impact'], bin_analysis_df['ILLIQ'],
                           s=bin_analysis_df['abs_tradevolume']*100, c=bin_analysis_df.index, cmap='viridis')
    ax8.set_title('ILLIQ vs Price Impact\n(Size = Volume)')
    ax8.set_xlabel('Average Price Impact')
    ax8.set_ylabel('ILLIQ')
    fig.colorbar(scatter2, ax=ax8, label='Volume Bin')

    # Table: Summary Statistics
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.set_title('Summary Statistics')
    stats = filtered_df[['last_price_impact', 'abs_tradevolume', 'ILLIQ']].describe().loc[['mean', 'std', 'min', 'max']]
    stats.columns = ['Price Impact', 'Volume', 'ILLIQ']
    stats.index = ['Mean', 'Std', 'Min', 'Max']
    table = ax9.table(cellText=np.round(stats.values, 6), colLabels=stats.columns, rowLabels=stats.index, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    ax9.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_path = os.path.join(data_folder, f'comprehensive_price_impact_analysis2_{pool_address}.png')
    plt.savefig(save_path)
    print(f"Saved comprehensive price impact analysis plot to {save_path}")
    plt.close()

def plot_comprehensive_raw_data_analysis(filtered_df, data_folder, pool_address):
    """
    Generates and saves a comprehensive raw data analysis plot.
    """
    if len(filtered_df) > 10000:
        plot_df = filtered_df.sample(10000, random_state=42)
    else:
        plot_df = filtered_df

    fig = plt.figure(figsize=(22, 15))
    gs = gridspec.GridSpec(2, 3, figure=fig)
    fig.suptitle(f'Comprehensive Raw Data Analysis for Pool: {pool_address}', fontsize=18, y=0.96)

    # Plot 1: Price Impact vs Trade Volume (Raw Data)
    ax1 = fig.add_subplot(gs[0, 0])
    scatter1 = ax1.scatter(plot_df['abs_tradevolume'], plot_df['last_price_impact'], c=plot_df['last_price_impact'], 
                             cmap='viridis', s=5, norm=plt.cm.colors.LogNorm())
    ax1.set_title(f'Price Impact vs Trade Volume\n(Raw Data Sample of {len(plot_df)})')
    ax1.set_xlabel('Trade Volume')
    ax1.set_ylabel('Price Impact')
    fig.colorbar(scatter1, ax=ax1, label='Price Impact (log scale)')

    # Plot 2: Power Law Validation on Raw Data
    ax2 = fig.add_subplot(gs[0, 1])
    fit_df = plot_df[(plot_df['abs_tradevolume'] > 0) & (plot_df['last_price_impact'] > 0)].copy()
    fit_df['log_volume'] = np.log10(fit_df['abs_tradevolume'])
    fit_df['log_impact'] = np.log10(fit_df['last_price_impact'])
    
    X = fit_df[['log_volume']].values
    y = fit_df['log_impact'].values
    
    slope, intercept = linear_regression(X, y)
    y_pred = slope * X.flatten() + intercept
    r2 = calculate_r2_score(y, y_pred)
    
    ax2.scatter(fit_df['log_volume'], fit_df['log_impact'], alpha=0.1, s=5)
    ax2.plot(fit_df['log_volume'], y_pred, color='red', label=f'Power Law Fit (R²: {r2:.3f})')
    ax2.set_title(f'Power Law Validation on Raw Data\n(Raw Trades Sample of {len(fit_df)})')
    ax2.set_xlabel('Trade Volume (log scale)')
    ax2.set_ylabel('Price Impact (log Scale)')
    ax2.legend()

    # Plot 3: Trade Volume vs ILLIQ
    ax3 = fig.add_subplot(gs[0, 2])
    scatter3 = ax3.scatter(plot_df['abs_tradevolume'], plot_df['ILLIQ'], c=plot_df['last_price_impact'], 
                             cmap='plasma', s=5, norm=plt.cm.colors.LogNorm())
    ax3.set_title('Trade Volume vs ILLIQ\n(Color = Price Impact)')
    ax3.set_xlabel('Trade Volume')
    ax3.set_ylabel('ILLIQ')
    fig.colorbar(scatter3, ax=ax3, label='Price Impact (log scale)')

    # Plot 4: Price Impact Distribution
    ax4 = fig.add_subplot(gs[1, 0])
    q99 = plot_df['last_price_impact'].quantile(0.99)
    sns.histplot(plot_df[plot_df['last_price_impact'] < q99]['last_price_impact'], bins=50, ax=ax4)
    ax4.set_title('Price Impact Distribution\n(Raw Data Sample - Outliers Removed)')
    ax4.set_xlabel('Price Impact')
    ax4.set_ylabel('Frequency')

    # Plot 5: Trade Volume vs ILLIQ (Zoomed)
    ax5 = fig.add_subplot(gs[1, 1])
    zoomed_df = plot_df[plot_df['ILLIQ'] < plot_df['ILLIQ'].quantile(0.95)]
    scatter5 = ax5.scatter(zoomed_df['abs_tradevolume'], zoomed_df['ILLIQ'], c=zoomed_df['last_price_impact'], 
                             cmap='magma', s=5, norm=plt.cm.colors.LogNorm())
    ax5.set_title(f'Trade Volume vs ILLIQ (Zoomed)\n(ILLIQ < {plot_df["ILLIQ"].quantile(0.95):.1f}, {len(zoomed_df)} obs)')
    ax5.set_xlabel('Trade Volume')
    ax5.set_ylabel('ILLIQ')
    fig.colorbar(scatter5, ax=ax5, label='Price Impact (log scale)')

    # Table: Raw Data Summary Statistics
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_title('Raw Data Summary Statistics')
    stats = filtered_df[['last_price_impact', 'abs_tradevolume', 'ILLIQ']].describe().loc[['mean', 'std', 'min', 'max']]
    stats.columns = ['Price Impact', 'Trade Volume', 'ILLIQ']
    stats.index = ['Mean', 'Std', 'Min', 'Max']
    table = ax6.table(cellText=np.round(stats.values, 6), colLabels=stats.columns, rowLabels=stats.index, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    ax6.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_path = os.path.join(data_folder, f'comprehensive_raw_data_analysis2_{pool_address}.png')
    plt.savefig(save_path)
    print(f"Saved comprehensive raw data analysis plot to {save_path}")
    plt.close()

def main():
    """
    Main function to run the visualization script.
    """
    # Specify the pool address you want to process
    pool_address = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
    pool_address = pool_address.lower()  # Ensure lowercase for file matching

    # Load the data
    data_folder = os.path.join('..', 'data', pool_address)
    bin_analysis_file = os.path.join(data_folder, f'price_impact_bin_analysis_{pool_address}.csv')
    filtered_metrics_file = os.path.join(data_folder, f'filtered_impact_metrics_{pool_address}.csv')

    if not os.path.exists(bin_analysis_file) or not os.path.exists(filtered_metrics_file):
        print("Required data files not found. Please run combine_minute_csvs.py first.")
        return

    # Read the data
    bin_analysis_df = pd.read_csv(bin_analysis_file).set_index('volume_bin')
    filtered_df = pd.read_csv(filtered_metrics_file)

    # Create the plots
    plot_comprehensive_price_impact_analysis(bin_analysis_df, filtered_df, data_folder, pool_address)
    plot_comprehensive_raw_data_analysis(filtered_df, data_folder, pool_address)

if __name__ == '__main__':
    # Set a backend that doesn't require a GUI
    import matplotlib
    matplotlib.use('Agg')
    main() 