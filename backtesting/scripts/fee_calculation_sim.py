import math
import pandas as pd
import numpy as np
import os
from typing import Dict, Tuple

class FeeCalculationSimulator:
    """
    Simulator for fee calculation logic using real market data
    """
    
    def __init__(self, data_file_path: str, vpin_file_path: str = None):
        """
        Initialize the simulator with market data
        Args:
            data_file_path: Path to the combined minute data CSV file
            vpin_file_path: Path to the VPIN analysis CSV file (optional)
        """
        self.data_file_path = data_file_path
        self.vpin_file_path = vpin_file_path
        self.data = None
        self.vpin_data = None
        self.load_data()
        if vpin_file_path:
            self.load_vpin_data()
        
    def load_data(self):
        """Load and prepare the market data"""
        print(f"Loading data from {self.data_file_path}...")
        self.data = pd.read_csv(self.data_file_path)
        
        # Convert timestamp to datetime
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        
        # Sort by timestamp
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)
        
        print(f"Loaded {len(self.data)} data points")
        print(f"Date range: {self.data['timestamp'].min()} to {self.data['timestamp'].max()}")
    
    def load_vpin_data(self):
        """Load VPIN analysis data"""
        if self.vpin_file_path is None:
            # Auto-generate VPIN file path based on data file path
            data_dir = os.path.dirname(self.data_file_path)
            base_name = os.path.splitext(os.path.basename(self.data_file_path))[0]
            self.vpin_file_path = os.path.join(data_dir, f"{base_name}_vpin_analysis.csv")
        
        if not os.path.exists(self.vpin_file_path):
            print(f"Warning: VPIN file not found: {self.vpin_file_path}")
            return
        
        print(f"Loading VPIN data from {self.vpin_file_path}...")
        self.vpin_data = pd.read_csv(self.vpin_file_path)
        
        # Convert timestamp to datetime
        self.vpin_data['timestamp'] = pd.to_datetime(self.vpin_data['timestamp'])
        
        # Sort by timestamp
        self.vpin_data = self.vpin_data.sort_values('timestamp').reset_index(drop=True)
        
        print(f"Loaded {len(self.vpin_data)} VPIN buckets")
        print(f"VPIN date range: {self.vpin_data['timestamp'].min()} to {self.vpin_data['timestamp'].max()}")
        
        # Print VPIN statistics
        for col in ['vpin_daily', 'vpin_5day', 'vpin_7day']:
            if col in self.vpin_data.columns:
                print(f"{col}: mean={self.vpin_data[col].mean():.6f}, "
                      f"min={self.vpin_data[col].min():.6f}, "
                      f"max={self.vpin_data[col].max():.6f}")
    
    def analyze_price_range(self) -> Dict[str, float]:
        """
        Analyze the price range in the data
        Returns:
            Dictionary with price statistics
        """
        price_stats = {
            'min_price': self.data['price'].min(),
            'max_price': self.data['price'].max(),
            'initial_price': self.data.iloc[0]['price'],
            'mean_price': self.data['price'].mean(),
            'std_price': self.data['price'].std()
        }
        
        print("\n=== Price Range Analysis ===")
        print(f"Initial Price: {price_stats['initial_price']:.6f}")
        print(f"Min Price: {price_stats['min_price']:.6f}")
        print(f"Max Price: {price_stats['max_price']:.6f}")
        print(f"Mean Price: {price_stats['mean_price']:.6f}")
        print(f"Price Std Dev: {price_stats['std_price']:.6f}")
        print(f"Price Range: {price_stats['max_price'] - price_stats['min_price']:.6f}")
        
        return price_stats
    
    def calculate_position_parameters(self, price_stats: Dict[str, float], 
                                    token0_amount: float = 10.0,
                                    buffer_factor: float = 0.15) -> Dict[str, float]:
        """
        Calculate LP position parameters to cover the entire price range
        Args:
            price_stats: Price statistics from analyze_price_range
            token0_amount: Amount of token0 to deploy
            buffer_factor: Buffer factor to extend range beyond min/max (15% default)
        Returns:
            Dictionary with position parameters
        """
        initial_price = price_stats['initial_price']
        min_price = price_stats['min_price']
        max_price = price_stats['max_price']
        
        # Add buffer to ensure position stays in range
        lower_price = min_price * (1 - buffer_factor)
        upper_price = max_price * (1 + buffer_factor)
        
        # Calculate r_factor
        r_factor = math.sqrt(upper_price / lower_price)
        
        # Calculate sqrt prices
        sqrt_lower = math.sqrt(lower_price)
        sqrt_upper = math.sqrt(upper_price)
        sqrt_current = math.sqrt(initial_price)
        
        # Calculate liquidity using token0 formula (same as inv_exposure_sim)
        liquidity = token0_amount * (sqrt_upper * sqrt_current) / (sqrt_upper - sqrt_current)
        
        # Calculate token1 amount required
        token1_amount = liquidity * (sqrt_current - sqrt_lower)
        
        # Calculate total position value in token1 terms
        total_value = token0_amount * initial_price + token1_amount
        
        # Calculate inventory exposure (token0 share as absolute value, not percentage)
        inventory_exposure = token0_amount * initial_price / total_value
        
        position_params = {
            'initial_price': initial_price,
            'lower_price': lower_price,
            'upper_price': upper_price,
            'r_factor': r_factor,
            'token0_amount': token0_amount,
            'liquidity': liquidity,
            'token1_amount': token1_amount,
            'total_value': total_value,
            'inventory_exposure': inventory_exposure,
            'sqrt_lower': sqrt_lower,
            'sqrt_upper': sqrt_upper,
            'sqrt_current': sqrt_current
        }
        
        print("\n=== Position Parameters ===")
        print(f"Initial Price: {initial_price:.6f}")
        print(f"Lower Price: {lower_price:.6f}")
        print(f"Upper Price: {upper_price:.6f}")
        print(f"R Factor: {r_factor:.6f}")
        print(f"Token0 Amount: {token0_amount:.4f}")
        print(f"Liquidity (L): {liquidity:.6f}")
        print(f"Token1 Amount: {token1_amount:.2f}")
        print(f"Total Position Value: {total_value:.2f}")
        print(f"Inventory Exposure: {inventory_exposure:.4f}")
        
        return position_params
    
    def verify_position_calculations(self, position_params: Dict[str, float]) -> bool:
        """
        Verify that our calculations match the logic from inv_exposure_sim
        Returns:
            True if calculations are consistent
        """
        print("\n=== Verification Against inv_exposure_sim Logic ===")
        
        # Extract parameters
        initial_price = position_params['initial_price']
        r_factor = position_params['r_factor']
        token0_amount = position_params['token0_amount']
        lower_price = position_params['lower_price']
        upper_price = position_params['upper_price']
        liquidity = position_params['liquidity']
        token1_amount = position_params['token1_amount']
        total_value = position_params['total_value']
        inventory_exposure = position_params['inventory_exposure']
        
        # Recalculate using inv_exposure_sim logic
        sqrt_lower = math.sqrt(lower_price)
        sqrt_upper = math.sqrt(upper_price)
        sqrt_current = math.sqrt(initial_price)
        
        # Calculate L using token0 formula
        L_calculated = token0_amount * (sqrt_upper * sqrt_current) / (sqrt_upper - sqrt_current)
        
        # Calculate token1 amount
        token1_calculated = L_calculated * (sqrt_current - sqrt_lower)
        
        # Calculate total value
        total_value_calculated = token0_amount * initial_price + token1_calculated
        
        # Calculate inventory exposure
        inventory_exposure_calculated = token0_amount * initial_price / total_value_calculated
        
        # Verify calculations
        l_diff = abs(liquidity - L_calculated)
        token1_diff = abs(token1_amount - token1_calculated)
        value_diff = abs(total_value - total_value_calculated)
        exposure_diff = abs(inventory_exposure - inventory_exposure_calculated)
        
        print(f"Liquidity difference: {l_diff:.10f}")
        print(f"Token1 amount difference: {token1_diff:.10f}")
        print(f"Total value difference: {value_diff:.10f}")
        print(f"Inventory exposure difference: {exposure_diff:.10f}")
        
        # Check if differences are negligible
        tolerance = 1e-10
        is_consistent = (l_diff < tolerance and 
                        token1_diff < tolerance and 
                        value_diff < tolerance and 
                        exposure_diff < tolerance)
        
        if is_consistent:
            print("✓ All calculations are consistent with inv_exposure_sim logic")
        else:
            print("✗ Calculations are NOT consistent with inv_exposure_sim logic")
            
        return is_consistent
    
    def calculate_token_amounts_at_price(self, price: float, position_params: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate token amounts at a specific price (same logic as inv_exposure_sim)
        Args:
            price: Price to calculate amounts at
            position_params: Position parameters
        Returns:
            Dictionary with token amounts and metrics
        """
        liquidity = position_params['liquidity']
        sqrt_lower = position_params['sqrt_lower']
        sqrt_upper = position_params['sqrt_upper']
        
        sqrt_price = math.sqrt(price)
        
        if price <= position_params['lower_price']:
            token0 = liquidity * (sqrt_upper - sqrt_lower) / (sqrt_lower * sqrt_upper)
            token1 = 0
        elif price >= position_params['upper_price']:
            token0 = 0
            token1 = liquidity * (sqrt_upper - sqrt_lower)
        else:
            token0 = liquidity * (sqrt_upper - sqrt_price) / (sqrt_price * sqrt_upper)
            token1 = liquidity * (sqrt_price - sqrt_lower)
        
        total_value = token0 * price + token1
        inventory_exposure = (token0 * price / total_value) if total_value > 0 else 0
        
        return {
            'price': price,
            'token0': token0,
            'token1': token1,
            'total_value': total_value,
            'inventory_exposure': inventory_exposure
        }
    
    def test_position_at_extreme_prices(self, position_params: Dict[str, float]) -> bool:
        """
        Test position calculations at extreme prices to ensure it stays in range
        Returns:
            True if position behaves correctly at extremes
        """
        print("\n=== Testing Position at Extreme Prices ===")
        
        # Test at observed min price (not position lower bound)
        observed_min_price = self.data['price'].min()
        min_test = self.calculate_token_amounts_at_price(observed_min_price, position_params)
        print(f"At observed min price ({observed_min_price:.6f}):")
        print(f"  Token0: {min_test['token0']:.6f}")
        print(f"  Token1: {min_test['token1']:.2f}")
        print(f"  Total Value: {min_test['total_value']:.2f}")
        print(f"  Inventory Exposure: {min_test['inventory_exposure']:.4f}")
        
        # Test at observed max price (not position upper bound)
        observed_max_price = self.data['price'].max()
        max_test = self.calculate_token_amounts_at_price(observed_max_price, position_params)
        print(f"At observed max price ({observed_max_price:.6f}):")
        print(f"  Token0: {max_test['token0']:.6f}")
        print(f"  Token1: {max_test['token1']:.2f}")
        print(f"  Total Value: {max_test['total_value']:.2f}")
        print(f"  Inventory Exposure: {max_test['inventory_exposure']:.4f}")
        
        # Test at initial price
        initial_test = self.calculate_token_amounts_at_price(position_params['initial_price'], position_params)
        print(f"At initial price ({position_params['initial_price']:.6f}):")
        print(f"  Token0: {initial_test['token0']:.6f}")
        print(f"  Token1: {initial_test['token1']:.2f}")
        print(f"  Total Value: {initial_test['total_value']:.2f}")
        print(f"  Inventory Exposure: {initial_test['inventory_exposure']:.4f}")
        
        # Test at position bounds (should be at edge of range)
        lower_bound_test = self.calculate_token_amounts_at_price(position_params['lower_price'], position_params)
        upper_bound_test = self.calculate_token_amounts_at_price(position_params['upper_price'], position_params)
        print(f"\nAt position lower bound ({position_params['lower_price']:.6f}):")
        print(f"  Token0: {lower_bound_test['token0']:.6f}")
        print(f"  Token1: {lower_bound_test['token1']:.2f}")
        print(f"  Inventory Exposure: {lower_bound_test['inventory_exposure']:.4f}")
        print(f"At position upper bound ({position_params['upper_price']:.6f}):")
        print(f"  Token0: {upper_bound_test['token0']:.6f}")
        print(f"  Token1: {upper_bound_test['token1']:.2f}")
        print(f"  Inventory Exposure: {upper_bound_test['inventory_exposure']:.4f}")
        
        # Verify that position is in range for observed prices (has both tokens)
        is_in_range_min = min_test['token0'] > 0 and min_test['token1'] > 0
        is_in_range_max = max_test['token0'] > 0 and max_test['token1'] > 0
        is_in_range_initial = initial_test['token0'] > 0 and initial_test['token1'] > 0
        
        print(f"\nPosition in range at observed min price: {'✓' if is_in_range_min else '✗'}")
        print(f"Position in range at observed max price: {'✓' if is_in_range_max else '✗'}")
        print(f"Position in range at initial price: {'✓' if is_in_range_initial else '✗'}")
        
        return is_in_range_min and is_in_range_max and is_in_range_initial
    
    def calculate_fees_with_vpin_full_timeseries(self, position_params: Dict[str, float], vpin_type: str = 'vpin_daily', base_fee_pct: float = 0.05) -> pd.DataFrame:
        """
        Calculate fees using VPIN * expected impermanent loss for every row in the minute/trade data.
        Args:
            position_params: The LP position parameters
            vpin_type: Type of VPIN to use ('vpin_daily', 'vpin_5day', 'vpin_7day')
            base_fee_pct: Base fee percentage (default 0.05%)
        Returns:
            DataFrame with fee calculations for every row in the minute/trade data
        """
        print(f"\n=== Full Timeseries Fee Calculation with VPIN ===")
        print(f"Using VPIN type: {vpin_type}")
        print(f"Base fee: {base_fee_pct}%")
        
        if self.vpin_data is None:
            print("Error: VPIN data not loaded. Please provide VPIN file path.")
            return pd.DataFrame()
        
        if vpin_type not in self.vpin_data.columns:
            print(f"Error: VPIN type '{vpin_type}' not found in VPIN data.")
            print(f"Available VPIN types: {[col for col in self.vpin_data.columns if col.startswith('vpin_')]}")
            return pd.DataFrame()
        
        # Iterate over every row in the minute/trade data (use all trades, both positive and negative tradevolume)
        results = []
        vpin_idx = 0
        vpin_timestamps = self.vpin_data['timestamp'].values
        vpin_values = self.vpin_data[vpin_type].values
        n_vpin = len(self.vpin_data)
        latest_vpin = vpin_values[0] if n_vpin > 0 else None
        
        # Track latest valid ILLIQ for fallback
        latest_illiq = None
        
        for idx, row in self.data.iterrows():
            timestamp = row['timestamp']
            price = row['price']
            trade_volume = row['tradevolume'] if 'tradevolume' in row else row.get('trade_volume', 0)
            abs_trade_volume = abs(trade_volume)
            
            # Move VPIN index forward if needed
            while vpin_idx + 1 < n_vpin and vpin_timestamps[vpin_idx + 1] <= timestamp:
                vpin_idx += 1
                latest_vpin = vpin_values[vpin_idx]
            vpin_at_time = latest_vpin
            
            # Calculate expected impermanent loss (if abs(trade_volume) > 0 and ILLIQ available)
            expected_impermanent_loss = None
            current_illiq = row['ILLIQ'] if 'ILLIQ' in row and pd.notna(row['ILLIQ']) else None
            
            # Fix: Ignore ILLIQ = 0.0 as it's likely invalid
            if current_illiq == 0.0:
                current_illiq = None
            
            if abs_trade_volume > 0:
                position_state = self.calculate_token_amounts_at_price(price, position_params)
                inventory_exposure = position_state['inventory_exposure']
                
                # Always use latest prior ILLIQ for estimation (not current ILLIQ)
                if latest_illiq is not None:
                    # Calculate estimated price impact as absolute number
                    # estimated_price_impact = trade_volume * illiq / 1000000
                    estimated_price_impact = (latest_illiq * abs_trade_volume) / 1_000_000
                    # Expected impermanent loss = estimated price impact * inventory_exposure (absolute)
                    expected_impermanent_loss = estimated_price_impact * inventory_exposure
                else:
                    estimated_price_impact = 0.0
                    expected_impermanent_loss = 0.0
            else:
                estimated_price_impact = 0.0
                expected_impermanent_loss = 0.0
            
            # Update latest_illiq for next row (only if current_illiq is valid)
            if current_illiq is not None:
                latest_illiq = current_illiq
            
            # Calculate base fee component
            base_fee = (base_fee_pct / 100) * abs_trade_volume if abs_trade_volume > 0 else 0.0
            
            # Calculate VPIN-based fee component (as percentage of trade volume)
            # VPIN fee % = Expected IL * VPIN (this is the percentage of trade volume)
            vpin_fee_pct_of_volume = expected_impermanent_loss * vpin_at_time if vpin_at_time is not None else 0.0
            
            # Calculate absolute VPIN fee amount
            vpin_fee_absolute = vpin_fee_pct_of_volume * abs_trade_volume if abs_trade_volume > 0 else 0.0
            
            # Total fee = base fee + absolute VPIN fee
            total_fee = base_fee + vpin_fee_absolute
            
            # Calculate fee as percentage of trade volume (use abs value)
            fee_pct = (total_fee / abs_trade_volume) if abs_trade_volume > 0 else 0.0
            
            # Debug output for first few rows
            if idx < 5 and abs_trade_volume > 0:
                print(f"Row {idx}: Trade volume={abs_trade_volume:.2f}, Base fee={base_fee:.6f}, VPIN fee %={vpin_fee_pct_of_volume:.6f}%, VPIN fee abs={vpin_fee_absolute:.6f}, Total fee={total_fee:.6f} ({fee_pct:.4f}%)")
            
            results.append({
                'timestamp': timestamp,
                'price': price,
                'trade_volume': trade_volume,
                'abs_trade_volume': abs_trade_volume,
                'ILLIQ': current_illiq,
                'vpin_used': vpin_at_time,
                'estimated_price_impact': estimated_price_impact,
                'expected_impermanent_loss': expected_impermanent_loss,
                'base_fee': base_fee,
                'vpin_fee_pct_of_volume': vpin_fee_pct_of_volume,
                'vpin_fee_absolute': vpin_fee_absolute,
                'total_fee': total_fee,
                'fee_pct_of_volume': fee_pct,
                'inventory_exposure': inventory_exposure
            })
        results_df = pd.DataFrame(results)
        print(f"Full timeseries fee calculation complete. Rows: {len(results_df)}")
        return results_df

    def combine_position_and_fee_timeseries(self, position_params: Dict[str, float], vpin_type: str = 'vpin_daily', base_fee_pct: float = 0.05, output_path: str = None, pool_address: str = None):
        """
        Combine position timeseries and full timeseries fee calculation, removing duplicate columns.
        Also add real and estimated price impact columns.
        """
        # Position timeseries
        pos_records = []
        latest_illiq = None
        for idx, row in self.data.iterrows():
            price = row['price']
            ts = row['timestamp']
            metrics = self.calculate_token_amounts_at_price(price, position_params)
            real_price_impact = row['last_price_impact'] if 'last_price_impact' in row and pd.notna(row['last_price_impact']) else 0.0
            abs_trade_volume = abs(row['tradevolume']) if 'tradevolume' in row else abs(row.get('trade_volume', 0))
            current_illiq = row['ILLIQ'] if 'ILLIQ' in row and pd.notna(row['ILLIQ']) else None
            
            # Fix: Ignore ILLIQ = 0.0 as it's likely invalid
            if current_illiq == 0.0:
                current_illiq = None
            
            # Always use latest prior ILLIQ for estimation (not current ILLIQ)
            estimated_price_impact = None
            if abs_trade_volume > 0:
                if latest_illiq is not None:
                    # Use latest prior ILLIQ for estimation
                    estimated_price_impact = (latest_illiq * abs_trade_volume) / 1_000_000
                else:
                    # No prior ILLIQ available
                    estimated_price_impact = 0.0
            else:
                estimated_price_impact = 0.0
            
            # Update latest_illiq for next row (only if current_illiq is valid)
            if current_illiq is not None:
                latest_illiq = current_illiq
                
            pos_records.append({
                'timestamp': ts,
                'price': price,
                'token0': metrics['token0'],
                'token1': metrics['token1'],
                'total_value': metrics['total_value'],
                'inventory_exposure': metrics['inventory_exposure'],
                'real_price_impact': real_price_impact,
                'estimated_price_impact': estimated_price_impact
            })
        pos_df = pd.DataFrame(pos_records)
        # Full timeseries fee calculation
        fee_df = self.calculate_fees_with_vpin_full_timeseries(position_params, vpin_type, base_fee_pct)
        # Merge on timestamp and price
        merged = pd.merge(pos_df, fee_df, on=['timestamp', 'price'], suffixes=('_pos', '_fee'))
        # Remove duplicate columns (keep only one copy)
        for col in ['inventory_exposure', 'total_value']:
            if f'{col}_fee' in merged.columns:
                merged.drop(columns=[f'{col}_fee'], inplace=True)
        if output_path is None:
            # Get the project root directory (one level up from scripts/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            if pool_address:
                output_path = os.path.join(project_root, f'data/{pool_address}/fee_sim_position_and_fee_timeseries.csv')
            else:
                output_path = os.path.join(project_root, 'data/fee_sim_position_and_fee_timeseries.csv')
        merged.to_csv(output_path, index=False)
        print(f"Combined position and fee timeseries saved to {output_path}")

    def run_combined_outputs(self, position_params: Dict[str, float], base_fee_pct: float = 0.05, pool_address: str = None):
        self.combine_position_and_fee_timeseries(position_params, vpin_type='vpin_daily', base_fee_pct=base_fee_pct, pool_address=pool_address)

def main():
    """
    Main function to run the complete fee calculation simulation
    """
    print("=" * 80)
    print("FEE CALCULATION SIMULATION - COMPLETE")
    print("=" * 80)
    
    # ===== CONFIGURATION =====
    # Change this pool address to run simulation for different pools
    POOL_ADDRESS = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
    # ========================
    
    # Get the project root directory (one level up from scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Initialize simulator with the pool data
    data_file = os.path.join(project_root, f"data/{POOL_ADDRESS}/all_days_combined_{POOL_ADDRESS}.csv")
    vpin_file = os.path.join(project_root, f"data/{POOL_ADDRESS}/all_days_combined_{POOL_ADDRESS}_vpin_analysis.csv")
    
    if not os.path.exists(data_file):
        print(f"Error: Data file not found: {data_file}")
        return
    
    simulator = FeeCalculationSimulator(data_file, vpin_file)
    
    # Step 1: Analyze price range
    price_stats = simulator.analyze_price_range()
    
    # Step 2: Calculate position parameters
    position_params = simulator.calculate_position_parameters(price_stats, token0_amount=10.0)
    
    # Step 3: Verify calculations against inv_exposure_sim logic
    verification_passed = simulator.verify_position_calculations(position_params)
    
    # Step 4: Test position at extreme prices
    extreme_test_passed = simulator.test_position_at_extreme_prices(position_params)
    
    # Step 5: Full timeseries fee calculation with VPIN
    fee_results_full = simulator.calculate_fees_with_vpin_full_timeseries(position_params, vpin_type='vpin_daily', base_fee_pct=0.05)
    # Fee results are saved in the combined output method below
    
    # Step 6: Combined outputs
    simulator.run_combined_outputs(position_params, base_fee_pct=0.05, pool_address=POOL_ADDRESS)
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE SIMULATION SUMMARY")
    print("=" * 80)
    print(f"Data loaded successfully: ✓")
    print(f"VPIN data loaded: {'✓' if simulator.vpin_data is not None else '✗'}")
    print(f"Price range analysis completed: ✓")
    print(f"Position parameters calculated: ✓")
    print(f"Verification against inv_exposure_sim: {'✓' if verification_passed else '✗'}")
    print(f"Extreme price testing: {'✓' if extreme_test_passed else '✗'}")
    
    if verification_passed and extreme_test_passed:
        print("\n✓ Complete simulation completed successfully!")
        return position_params, simulator
    else:
        print("\n✗ Simulation failed. Please review the issues above.")
        return None, None

if __name__ == "__main__":
    main() 