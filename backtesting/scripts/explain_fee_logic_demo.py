import pandas as pd
import numpy as np

def explain_fee_logic():
    """
    Demonstrate how the fee calculation logic works with 4 sample swaps
    """
    
    print("="*80)
    print("DYNAMIC FEE CALCULATION LOGIC DEMONSTRATION")
    print("="*80)
    
    # Sample swap data from our analysis
    sample_swaps = [
        {
            'name': 'Scenario 1: All High Risk',
            'timestamp': '2025-05-19 00:29:00',
            'trade_volume': 2.63e-07,
            'vpin': 0.318534,
            'illiq': 1.02e+10,
            'real_price_impact': 0.002696,
            'inventory_exposure': 0.3868,
            'estimated_price_impact': 0.002755,
            'expected_il': 0.00106573,
            'base_fee': 1.32e-10,
            'vpin_fee': 8.94e-11,
            'total_fee': 2.21e-10,
            'fee_pct': 0.0008
        },
        {
            'name': 'Scenario 2: High Impact, Low VPIN',
            'timestamp': '2025-05-20 00:25:00',
            'trade_volume': 2.64e-07,
            'vpin': 0.245102,
            'illiq': 9.87e+09,
            'real_price_impact': 0.002603,
            'inventory_exposure': 0.3438,
            'estimated_price_impact': 0.002363,
            'expected_il': 0.00081257,
            'base_fee': 1.32e-10,
            'vpin_fee': 5.25e-11,
            'total_fee': 1.84e-10,
            'fee_pct': 0.0007
        },
        {
            'name': 'Scenario 3: Balanced Market',
            'timestamp': '2025-06-12 19:44:00',
            'trade_volume': 2.58e-07,
            'vpin': 0.283005,
            'illiq': 3.49e+09,
            'real_price_impact': 0.000900,
            'inventory_exposure': 0.2627,
            'estimated_price_impact': 0.001280,
            'expected_il': 0.00033640,
            'base_fee': 1.29e-10,
            'vpin_fee': 2.46e-11,
            'total_fee': 1.54e-10,
            'fee_pct': 0.0006
        },
        {
            'name': 'Scenario 4: All Low Risk',
            'timestamp': '2025-05-27 09:57:00',
            'trade_volume': 2.43e-07,
            'vpin': 0.240914,
            'illiq': 4.12e+09,
            'real_price_impact': 0.000999,
            'inventory_exposure': 0.3025,
            'estimated_price_impact': 0.001944,
            'expected_il': 0.00058818,
            'base_fee': 1.21e-10,
            'vpin_fee': 3.44e-11,
            'total_fee': 1.56e-10,
            'fee_pct': 0.0006
        }
    ]
    
    print("\nFEE CALCULATION FORMULA:")
    print("Total Fee = Base Fee + VPIN Fee")
    print("Where:")
    print("  Base Fee = 0.05% × Trade Volume")
    print("  VPIN Fee = Expected Impermanent Loss × VPIN × Trade Volume")
    print("  Expected IL = Estimated Price Impact × Inventory Exposure")
    print("  Estimated Price Impact = (ILLIQ × Trade Volume) / 1,000,000")
    print("\n")
    
    for i, swap in enumerate(sample_swaps, 1):
        print(f"{'='*80}")
        print(f"SWAP {i}: {swap['name']}")
        print(f"{'='*80}")
        print(f"Timestamp: {swap['timestamp']}")
        print(f"Trade Volume: {swap['trade_volume']:.2e}")
        print()
        
        print("STEP 1: Calculate Base Fee")
        print(f"  Base Fee = 0.05% × {swap['trade_volume']:.2e}")
        print(f"  Base Fee = {swap['base_fee']:.2e}")
        print()
        
        print("STEP 2: Estimate Price Impact")
        print(f"  Estimated Price Impact = (ILLIQ × Trade Volume) / 1,000,000")
        print(f"  Estimated Price Impact = ({swap['illiq']:.2e} × {swap['trade_volume']:.2e}) / 1,000,000")
        print(f"  Estimated Price Impact = {swap['estimated_price_impact']:.6f}")
        print(f"  (Compare to Real Price Impact: {swap['real_price_impact']:.6f})")
        print()
        
        print("STEP 3: Calculate Expected Impermanent Loss")
        print(f"  Expected IL = Estimated Price Impact × Inventory Exposure")
        print(f"  Expected IL = {swap['estimated_price_impact']:.6f} × {swap['inventory_exposure']:.4f}")
        print(f"  Expected IL = {swap['expected_il']:.8f}")
        print()
        
        print("STEP 4: Calculate VPIN Fee")
        print(f"  VPIN Fee % of Volume = Expected IL × VPIN")
        print(f"  VPIN Fee % of Volume = {swap['expected_il']:.8f} × {swap['vpin']:.6f}")
        vpin_fee_pct = swap['expected_il'] * swap['vpin']
        print(f"  VPIN Fee % of Volume = {vpin_fee_pct:.8f}")
        print(f"  VPIN Fee Absolute = {vpin_fee_pct:.8f} × {swap['trade_volume']:.2e}")
        print(f"  VPIN Fee Absolute = {swap['vpin_fee']:.2e}")
        print()
        
        print("STEP 5: Calculate Total Fee")
        print(f"  Total Fee = Base Fee + VPIN Fee")
        print(f"  Total Fee = {swap['base_fee']:.2e} + {swap['vpin_fee']:.2e}")
        print(f"  Total Fee = {swap['total_fee']:.2e}")
        print(f"  Total Fee % = {swap['fee_pct']:.4f}% of trade volume")
        print()
        
        # Analysis of key factors
        print("KEY INSIGHTS:")
        if swap['vpin'] > 0.30:
            vpin_level = "HIGH"
        elif swap['vpin'] < 0.25:
            vpin_level = "LOW"
        else:
            vpin_level = "BALANCED"
            
        if swap['illiq'] > 8e9:
            illiq_level = "HIGH"
        else:
            illiq_level = "LOW"
            
        if swap['inventory_exposure'] > 0.38:
            exposure_level = "HIGH"
        elif swap['inventory_exposure'] < 0.32:
            exposure_level = "LOW"
        else:
            exposure_level = "BALANCED"
            
        print(f"  • VPIN Level: {vpin_level} ({swap['vpin']:.6f})")
        print(f"  • Market Liquidity (ILLIQ): {illiq_level} ({swap['illiq']:.2e})")
        print(f"  • Inventory Exposure: {exposure_level} ({swap['inventory_exposure']:.4f})")
        print(f"  • Expected vs Real Price Impact: {swap['estimated_price_impact']:.6f} vs {swap['real_price_impact']:.6f}")
        
        base_fee_pct = (swap['base_fee'] / swap['trade_volume']) * 100
        vpin_fee_pct_final = (swap['vpin_fee'] / swap['trade_volume']) * 100
        print(f"  • Base Fee contributes: {base_fee_pct:.4f}% of volume")
        print(f"  • VPIN Fee contributes: {vpin_fee_pct_final:.4f}% of volume")
        print()
    
    # Summary comparison
    print(f"{'='*80}")
    print("SUMMARY: HOW DIFFERENT MARKET CONDITIONS AFFECT FEES")
    print(f"{'='*80}")
    
    print("\nScenario Analysis:")
    print("1. ALL HIGH RISK: Highest fee (0.084% vs 0.05% base) due to:")
    print("   - High VPIN indicates toxic flow")
    print("   - High ILLIQ means large price impact per unit volume")
    print("   - High inventory exposure amplifies IL risk")
    print("   → VPIN fee adds 67.8% premium over base fee")
    
    print("\n2. HIGH IMPACT, LOW VPIN: Moderate fee (0.070% vs 0.05% base) because:")
    print("   - Low VPIN suggests non-toxic flow despite high price impact")
    print("   - High ILLIQ still creates significant price impact")
    print("   - Balanced inventory exposure limits IL risk")
    print("   → VPIN fee adds 39.8% premium over base fee")
    
    print("\n3. BALANCED MARKET: Lower fee (0.060% vs 0.05% base) due to:")
    print("   - Balanced VPIN indicates normal market conditions")
    print("   - Low ILLIQ means smaller price impact")
    print("   - Low inventory exposure reduces IL risk")
    print("   → VPIN fee adds 19.0% premium over base fee")
    
    print("\n4. ALL LOW RISK: Moderate fee (0.064% vs 0.05% base) because:")
    print("   - Low VPIN suggests benign flow")
    print("   - Low ILLIQ creates smaller price impact")
    print("   - But estimated price impact is higher than scenario 3")
    print("   → VPIN fee adds 28.4% premium over base fee")
    
    print("\nKEY TAKEAWAYS:")
    print("• The fee dynamically adjusts based on:")
    print("  1. Order toxicity (VPIN)")
    print("  2. Market liquidity conditions (ILLIQ)")
    print("  3. LP's vulnerability to losses (inventory exposure)")
    print("• Higher risk scenarios charge appropriately higher fees")
    print("• The system protects LPs while maintaining fair pricing")
    print("• Base fee ensures minimum compensation, VPIN fee adds risk premium")

if __name__ == "__main__":
    explain_fee_logic() 