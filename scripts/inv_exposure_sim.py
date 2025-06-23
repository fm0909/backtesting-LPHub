import math
from typing import Dict
import matplotlib.pyplot as plt
import numpy as np
import os

class UniswapV3LPCalculator:
    """
    Calculator for Uniswap V3 LP positions (double-sided, price in the middle of the range)
    Takes token0 as input, calculates L, then required token1 and total value.
    """
    
    def __init__(self, initial_price: float, r_factor: float, token0_amount: float):
        """
        Initialize the calculator with position parameters
        Args:
            initial_price: Price of token1 in terms of token0 (e.g., USDC per ETH)
            r_factor: Distance factor for upper and lower bounds
            token0_amount: Amount of token0 (e.g., ETH) for the position
        """
        self.initial_price = initial_price
        self.r_factor = r_factor
        self.token0_amount = token0_amount
        
        # Calculate price bounds
        self.lower_price = initial_price / r_factor
        self.upper_price = initial_price * r_factor
        self.current_price = initial_price
        
        self.sqrt_lower = math.sqrt(self.lower_price)
        self.sqrt_upper = math.sqrt(self.upper_price)
        self.sqrt_current = math.sqrt(self.current_price)

    def calculate_liquidity(self) -> float:
        """
        Calculate the liquidity (L) for the position using token0 formula
        Returns:
            Liquidity value L
        """
        L = self.token0_amount * (self.sqrt_upper * self.sqrt_current) / (self.sqrt_upper - self.sqrt_current)
        return L

    def calculate_token1_amount(self, liquidity: float) -> float:
        """
        Calculate the amount of token1 required for the position
        Args:
            liquidity: The calculated liquidity value
        Returns:
            Amount of token1 required
        """
        amount1 = liquidity * (self.sqrt_current - self.sqrt_lower)
        return amount1

    def calculate_position_value_token1(self, token1_amount: float) -> float:
        """
        Calculate the total position value denominated in token1
        Args:
            token1_amount: Amount of token1 in the position
        Returns:
            Total position value in token1 terms
        """
        token0_value_in_token1 = self.token0_amount * self.current_price
        total_value = token0_value_in_token1 + token1_amount
        return total_value

    def calculate_all_metrics(self) -> Dict[str, float]:
        """
        Calculate all position metrics
        Returns:
            Dictionary containing all calculated values
        """
        liquidity = self.calculate_liquidity()
        token1_amount = self.calculate_token1_amount(liquidity)
        total_value = self.calculate_position_value_token1(token1_amount)
        return {
            'initial_price': self.initial_price,
            'r_factor': self.r_factor,
            'lower_price': self.lower_price,
            'upper_price': self.upper_price,
            'token0_amount': self.token0_amount,
            'liquidity': liquidity,
            'token1_amount': token1_amount,
            'total_position_value_token1': total_value
        }

    def print_results(self, results: Dict[str, float]):
        """
        Print formatted results
        Args:
            results: Dictionary of calculated results
        """
        print("=== Uniswap V3 LP Position Calculator ===")
        print(f"Initial Price: {results['initial_price']:.2f} USDC per ETH")
        print(f"R Factor: {results['r_factor']:.2f}")
        print(f"Price Range: {results['lower_price']:.2f} - {results['upper_price']:.2f} USDC per ETH")
        print(f"Token0 Amount (ETH): {results['token0_amount']:.4f} ETH")
        print(f"Liquidity (L): {results['liquidity']:.6f}")
        print(f"Token1 Amount (USDC): {results['token1_amount']:.2f} USDC")
        print(f"Total Position Value: {results['total_position_value_token1']:.2f} USDC")
        print("=" * 45)

    def calculate_price_range_data(self, liquidity: float) -> list:
        """
        Calculate all metrics for the price range and return as structured data
        Args:
            liquidity: The calculated liquidity value
        Returns:
            List of dictionaries containing all calculated values for each price
        """
        # Build price list: 52 points total - 50 points from lower to upper, plus one below and one above
        num_points = 50
        prices = np.linspace(self.lower_price, self.upper_price, num_points)
        
        # Calculate step size for extending beyond bounds
        step_size = (self.upper_price - self.lower_price) / (num_points - 1)
        
        # Add one point below lower bound and one above upper bound
        extended_prices = np.concatenate([
            [self.lower_price - step_size],  # One point below lower bound
            prices,                          # Original 50 points
            [self.upper_price + step_size]   # One point above upper bound
        ])
        
        data = [{} for _ in range(len(extended_prices))]
        
        # Find the index of the initial price (closest match)
        initial_idx = np.argmin(np.abs(extended_prices - self.initial_price))
        
        # Upwards sweep (initial price and above)
        for i in range(initial_idx, len(extended_prices)):
            price = extended_prices[i]
            sqrt_price = math.sqrt(price)
            if price <= self.lower_price:
                token0 = liquidity * (self.sqrt_upper - self.sqrt_lower) / (self.sqrt_lower * self.sqrt_upper)
                token1 = 0
            elif price >= self.upper_price:
                token0 = 0
                token1 = liquidity * (self.sqrt_upper - self.sqrt_lower)
            else:
                token0 = liquidity * (self.sqrt_upper - sqrt_price) / (sqrt_price * self.sqrt_upper)
                token1 = liquidity * (sqrt_price - self.sqrt_lower)
            total_value = token0 * price + token1
            token0_share = (token0 * price / total_value) * 100 if total_value > 0 else 0
            if i == initial_idx:
                price_impact = 0.0
                incremental_il = 0.0
                prior_price = price
                prior_total_value = total_value
            else:
                prior_price = extended_prices[i-1]
                price_impact = (price / prior_price - 1) * 100
                # IL calculation
                sqrt_prior_price = math.sqrt(prior_price)
                if prior_price <= self.lower_price:
                    prior_token0 = liquidity * (self.sqrt_upper - self.sqrt_lower) / (self.sqrt_lower * self.sqrt_upper)
                    prior_token1 = 0
                elif prior_price >= self.upper_price:
                    prior_token0 = 0
                    prior_token1 = liquidity * (self.sqrt_upper - self.sqrt_lower)
                else:
                    prior_token0 = liquidity * (self.sqrt_upper - sqrt_prior_price) / (sqrt_prior_price * self.sqrt_upper)
                    prior_token1 = liquidity * (sqrt_prior_price - self.sqrt_lower)
                prior_total_value = prior_token0 * prior_price + prior_token1
                incremental_il = (total_value / prior_total_value - 1) * 100
            il_price_ratio = (incremental_il / price_impact) * 100 if abs(price_impact) > 1e-6 else 0.0
            data[i] = {
                'price': price,
                'token0': token0,
                'token1': token1,
                'total_value': total_value,
                'token0_share': token0_share,
                'price_impact': price_impact,
                'incremental_il': incremental_il,
                'il_price_ratio': il_price_ratio
            }
        # Downwards sweep (below initial price)
        for i in range(initial_idx-1, -1, -1):
            price = extended_prices[i]
            sqrt_price = math.sqrt(price)
            if price <= self.lower_price:
                token0 = liquidity * (self.sqrt_upper - self.sqrt_lower) / (self.sqrt_lower * self.sqrt_upper)
                token1 = 0
            elif price >= self.upper_price:
                token0 = 0
                token1 = liquidity * (self.sqrt_upper - self.sqrt_lower)
            else:
                token0 = liquidity * (self.sqrt_upper - sqrt_price) / (sqrt_price * self.sqrt_upper)
                token1 = liquidity * (sqrt_price - self.sqrt_lower)
            total_value = token0 * price + token1
            token0_share = (token0 * price / total_value) * 100 if total_value > 0 else 0
            # Use the next price as prior (since we're moving down)
            prior_price = extended_prices[i+1]
            price_impact = (price / prior_price - 1) * 100
            # IL calculation
            sqrt_prior_price = math.sqrt(prior_price)
            if prior_price <= self.lower_price:
                prior_token0 = liquidity * (self.sqrt_upper - self.sqrt_lower) / (self.sqrt_lower * self.sqrt_upper)
                prior_token1 = 0
            elif prior_price >= self.upper_price:
                prior_token0 = 0
                prior_token1 = liquidity * (self.sqrt_upper - self.sqrt_lower)
            else:
                prior_token0 = liquidity * (self.sqrt_upper - sqrt_prior_price) / (sqrt_prior_price * self.sqrt_upper)
                prior_token1 = liquidity * (sqrt_prior_price - self.sqrt_lower)
            prior_total_value = prior_token0 * prior_price + prior_token1
            incremental_il = (total_value / prior_total_value - 1) * 100
            il_price_ratio = (incremental_il / price_impact) * 100 if abs(price_impact) > 1e-6 else 0.0
            data[i] = {
                'price': price,
                'token0': token0,
                'token1': token1,
                'total_value': total_value,
                'token0_share': token0_share,
                'price_impact': price_impact,
                'incremental_il': incremental_il,
                'il_price_ratio': il_price_ratio
            }
        return data

    def print_value_table(self, liquidity: float):
        """
        Print formatted value table using pre-calculated data
        Args:
            liquidity: The calculated liquidity value
        """
        data = self.calculate_price_range_data(liquidity)
        
        print("\nPrice (USDC) | Token0 in LP | Token1 in LP | Total Value (USDC) | Token0 Share (%) | Price Impact (%) | Incremental IL (%) | IL/Price Impact (%)")
        print("--------------------------------------------------------------------------------------------------------------------------------")
        
        for row in data:
            print(f"{row['price']:12.2f} | {row['token0']:12.6f} | {row['token1']:12.2f} | {row['total_value']:17.2f} | {row['token0_share']:15.2f} | {row['price_impact']:10.2f}% | {row['incremental_il']:12.2f}% | {row['il_price_ratio']:15.2f}%")

    def save_to_excel(self, liquidity: float, filename: str = "uniswap_v3_lp_analysis.xlsx"):
        """
        Save the calculated data to an Excel file
        Args:
            liquidity: The calculated liquidity value
            filename: Name of the Excel file to save
        """
        try:
            import pandas as pd
            
            # Create the output directory if it doesn't exist
            output_dir = os.path.join("..", "inventory exposure sim")
            os.makedirs(output_dir, exist_ok=True)
            
            # Combine the directory path with the filename
            full_path = os.path.join(output_dir, filename)
            
            data = self.calculate_price_range_data(liquidity)
            df = pd.DataFrame(data)
            
            # Rename columns for better readability
            df.columns = ['Price (USDC)', 'Token0 in LP', 'Token1 in LP', 'Total Value (USDC)', 
                         'Token0 Share (%)', 'Price Impact (%)', 'Incremental IL (%)', 'IL/Price Impact (%)']
            
            # Save to Excel
            df.to_excel(full_path, index=False, sheet_name='LP Analysis')
            print(f"\nData saved to {full_path}")
            
            return df
            
        except ImportError:
            print("pandas not available. Install with: pip install pandas openpyxl")
            return None

    def plot_combined_presentation_friendly(self, calculator1, calculator2, liquidity1: float, liquidity2: float, save_filename: str = None):
        """
        Create a combined plot showing both scenarios' IL/Price Impact vs Token 0 share
        Optimized for presentation slides (compact, clear, readable)
        Args:
            calculator1: First calculator instance (R=2)
            calculator2: Second calculator instance (R=1.2)
            liquidity1: Liquidity for first scenario
            liquidity2: Liquidity for second scenario
            save_filename: Optional filename to save the plot
        """
        data1 = calculator1.calculate_price_range_data(liquidity1)
        data2 = calculator2.calculate_price_range_data(liquidity2)
        
        token0_shares1 = [row['token0_share'] for row in data1]
        il_price_ratios1 = [row['il_price_ratio'] for row in data1]
        token0_shares2 = [row['token0_share'] for row in data2]
        il_price_ratios2 = [row['il_price_ratio'] for row in data2]
        
        # Create the combined plot with smaller size for presentation
        plt.figure(figsize=(8, 6))
        
        # Plot both scenarios with scatter dots for better visibility
        plt.scatter(token0_shares1, il_price_ratios1, alpha=0.8, s=20, label=f'R=2 (Wide Range)', color='blue')
        plt.scatter(token0_shares2, il_price_ratios2, alpha=0.8, s=20, label=f'R=1.2 (Tight Range)', color='red')
        
        plt.xlabel('Token 0 Share (%)', fontsize=14, fontweight='bold')
        plt.ylabel('IL/Price Impact (%)', fontsize=14, fontweight='bold')
        plt.title(f'IL/Price Impact vs Token 0 Share\nInitial Price: {self.initial_price} USDC', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12, loc='upper left')
        
        # Add vertical lines for initial price token0 shares
        initial_sqrt_price = math.sqrt(self.initial_price)
        
        # For R=2
        initial_token0_1 = liquidity1 * (calculator1.sqrt_upper - initial_sqrt_price) / (initial_sqrt_price * calculator1.sqrt_upper)
        initial_token1_1 = liquidity1 * (initial_sqrt_price - calculator1.sqrt_lower)
        initial_total_value_1 = initial_token0_1 * self.initial_price + initial_token1_1
        initial_token0_share_1 = (initial_token0_1 * self.initial_price / initial_total_value_1) * 100
        plt.axvline(x=initial_token0_share_1, color='blue', linestyle='--', alpha=0.7, linewidth=2)
        
        # For R=1.2
        initial_token0_2 = liquidity2 * (calculator2.sqrt_upper - initial_sqrt_price) / (initial_sqrt_price * calculator2.sqrt_upper)
        initial_token1_2 = liquidity2 * (initial_sqrt_price - calculator2.sqrt_lower)
        initial_total_value_2 = initial_token0_2 * self.initial_price + initial_token1_2
        initial_token0_share_2 = (initial_token0_2 * self.initial_price / initial_total_value_2) * 100
        plt.axvline(x=initial_token0_share_2, color='red', linestyle='--', alpha=0.7, linewidth=2)
        
        # Increase tick label sizes
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        
        plt.tight_layout()
        
        if save_filename:
            # Create the output directory if it doesn't exist
            output_dir = os.path.join("..", "inventory exposure sim")
            os.makedirs(output_dir, exist_ok=True)
            
            # Combine the directory path with the filename
            full_path = os.path.join(output_dir, save_filename)
            
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"Combined plot saved to {full_path}")
            plt.close()
        else:
            plt.show()

def main():
    """
    Main function to run the test case for five different r factors
    """
    # Test case: ETH/USDC position
    initial_price = 2500  # USDC per ETH
    token0_amount = 10  # ETH
    
    # Define the five scenarios
    r_factors = [1.0001, 1.1, 1.5, 2, 5]
    scenario_names = ["Ultra Tight (R=1.0001)", "Very Tight (R=1.1)", "Tight (R=1.5)", "Wide (R=2)", "Very Wide (R=5)"]
    colors = ['red', 'orange', 'yellow', 'blue', 'purple']
    
    calculators = []
    results = []
    
    print("=" * 80)
    print("UNISWAP V3 LP POSITION ANALYSIS - FIVE SCENARIOS")
    print("=" * 80)
    
    # Run all scenarios
    for i, (r_factor, name, color) in enumerate(zip(r_factors, scenario_names, colors)):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i+1}: {name.upper()}")
        print(f"{'='*60}")
        
        calculator = UniswapV3LPCalculator(initial_price, r_factor, token0_amount)
        result = calculator.calculate_all_metrics()
        calculator.print_results(result)
        
        # Save data to Excel for each scenario
        filename = f"uniswap_v3_lp_analysis_r{r_factor}.xlsx"
        df = calculator.save_to_excel(result['liquidity'], filename)
        
        calculators.append(calculator)
        results.append(result)
    
    # Create a compact combined plot for presentation
    print("\n" + "=" * 80)
    print("CREATING PRESENTATION-FRIENDLY COMBINED PLOT")
    print("=" * 80)
    
    plt.figure(figsize=(8, 5))
    
    # Plot all scenarios with scatter dots for better visibility
    for i, (calculator, result, name, color) in enumerate(zip(calculators, results, scenario_names, colors)):
        data = calculator.calculate_price_range_data(result['liquidity'])
        token0_shares = [row['token0_share'] for row in data]
        il_price_ratios = [row['il_price_ratio'] for row in data]
        
        plt.scatter(token0_shares, il_price_ratios, alpha=0.8, s=15, label=f'R={result["r_factor"]}', color=color)
    
    plt.xlabel('Token 0 Share (%)', fontsize=12, fontweight='bold')
    plt.ylabel('IL/Price Impact (%)', fontsize=12, fontweight='bold')
    plt.title(f'IL/Price Impact vs Token 0 Share\nInitial Price: {initial_price} USDC', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10, loc='upper left', bbox_to_anchor=(0, 1))
    
    # Increase tick label sizes
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join("..", "inventory exposure sim", "presentation_combined_plot.png"), dpi=300, bbox_inches='tight')
    print("Presentation combined plot saved to inventory exposure sim/presentation_combined_plot.png")
    plt.close()
    
    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Scenario':<20} {'R Factor':<10} {'Price Range':<25} {'Token0 Share':<15} {'Total Value':<15}")
    print("-" * 80)
    
    for i, (result, name) in enumerate(zip(results, scenario_names)):
        initial_sqrt_price = math.sqrt(initial_price)
        initial_token0 = result['liquidity'] * (calculators[i].sqrt_upper - initial_sqrt_price) / (initial_sqrt_price * calculators[i].sqrt_upper)
        initial_token1 = result['liquidity'] * (initial_sqrt_price - calculators[i].sqrt_lower)
        initial_total_value = initial_token0 * initial_price + initial_token1
        initial_token0_share = (initial_token0 * initial_price / initial_total_value) * 100
        
        print(f"{name:<20} {result['r_factor']:<10.4f} {result['lower_price']:.1f}-{result['upper_price']:.1f} USDC{'':<10} {initial_token0_share:<15.1f}% {result['total_position_value_token1']:<15.2f}")
    
    return results, calculators

if __name__ == "__main__":
    main() 