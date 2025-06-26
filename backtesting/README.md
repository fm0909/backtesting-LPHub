# Uniswap V3 Research Project: Price Impact, VPIN Analysis, and LP Position Modeling

This comprehensive research project analyzes Uniswap V3 liquidity pools to understand price impact dynamics, market microstructure, and liquidity provider (LP) position behavior. The project combines blockchain data analysis, market microstructure theory, and quantitative modeling to provide insights into DeFi market dynamics.

## 🎯 Research Objectives

1. **Price Impact Analysis**: Quantify the relationship between trade volume and price impact in Uniswap V3 pools
2. **VPIN (Volume-synchronized Probability of Informed Trading)**: Measure market microstructure and information asymmetry
3. **LP Position Modeling**: Analyze inventory exposure and impermanent loss for different position ranges
4. **Fee Calculation Simulation**: Model dynamic fee structures based on market conditions and VPIN metrics
5. **Market Efficiency Analysis**: Evaluate liquidity provision strategies and market impact

## 📊 Project Structure

```
Research/
├── scripts/                          # Analysis and processing scripts
│   ├── run_demeter_fetch.py         # Blockchain data fetching
│   ├── combine_minute_csvs.py       # Data consolidation and preprocessing
│   ├── visualize_Price_impact.py    # Price impact visualization and analysis
│   ├── vpin_calculator.py           # VPIN calculation implementation
│   ├── vpin_price_visualization.py  # VPIN visualization and analysis
│   ├── inv_exposure_sim.py          # LP position modeling and inventory exposure
│   ├── fee_calculation_sim.py       # Dynamic fee calculation simulation
│   ├── calculate_total_fees.py      # Fee aggregation and analysis
│   ├── plot_fee_percentages.py      # Fee percentage visualization
│   ├── find_sample_swaps.py         # Sample trade identification
│   ├── visualize_sample_cases.py    # Sample case visualization
│   └── explain_fee_logic_demo.py    # Fee logic demonstration
├── data/                            # Analysis data and results
│   ├── 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640/  # USDC/ETH pool data
│   ├── 0x5ab53ee1d50eef2c1dd3d5402789cd27bb52c1bb/  # Additional pool data
│   └── 0xfcfdfc98062d13a11cec48c44e4613eb26a34293/  # Additional pool data
├── inventory exposure sim/          # LP analysis results and visualizations
├── config.toml                      # Configuration settings
├── requirements.txt                 # Python dependencies
└── README.md                       # This file
```

## 🔧 Scripts Overview

### Data Collection and Processing

#### `run_demeter_fetch.py`

- **Purpose**: Fetches raw blockchain data using the Demeter framework
- **Functionality**: Downloads minute-level trading data from Uniswap V3 pools
- **Output**: Daily CSV files with trade data, prices, and volumes
- **Configuration**: Uses `config.toml` for pool addresses and date ranges

#### `combine_minute_csvs.py`

- **Purpose**: Consolidates daily CSV files into comprehensive datasets
- **Functionality**:
  - Combines multiple daily files into single consolidated datasets
  - Calculates price impact metrics and ILLIQ (Amihud illiquidity measure)
  - Creates volume bins for analysis
  - Generates filtered impact metrics datasets
- **Key Metrics**: Price impact, trade volume, ILLIQ, volume bin analysis

### Price Impact Analysis

#### `visualize_Price_impact.py`

- **Purpose**: Comprehensive price impact analysis and visualization
- **Functionality**:
  - Power law validation (price impact vs volume relationship)
  - Volume bin analysis with efficiency metrics
  - ILLIQ analysis across different volume ranges
  - Multi-panel visualizations for comprehensive analysis
- **Output**: PNG files with detailed price impact analysis charts

#### `visualize_sample_cases.py`

- **Purpose**: Detailed analysis of specific trading cases
- **Functionality**: Identifies and visualizes interesting trading patterns and anomalies

### Market Microstructure Analysis

#### `vpin_calculator.py`

- **Purpose**: Implements VPIN (Volume-synchronized Probability of Informed Trading)
- **Functionality**:
  - Calculates order imbalances using volume-synchronized buckets
  - Computes VPIN for different time horizons (daily, 5-day, 7-day)
  - Tracks bucket-level metrics and order flow imbalances
- **Key Metrics**: VPIN daily, VPIN 5-day, VPIN 7-day, order imbalances

#### `vpin_price_visualization.py`

- **Purpose**: Visualizes VPIN metrics and their relationship with price movements
- **Functionality**: Creates time series plots and correlation analysis for VPIN metrics

### LP Position Modeling

#### `inv_exposure_sim.py`

- **Purpose**: Comprehensive Uniswap V3 LP position analysis
- **Functionality**:
  - Models LP positions with different range factors (r=1.0001, 1.1, 1.5, 2.0, 5.0)
  - Calculates liquidity (L), token amounts, and position values
  - Analyzes inventory exposure and impermanent loss across price ranges
  - Generates Excel reports with detailed position metrics
- **Key Features**:
  - Price range analysis with 52 data points per position
  - Impermanent loss calculations
  - Inventory exposure tracking
  - Presentation-ready visualizations

### Fee Analysis and Simulation

#### `fee_calculation_sim.py`

- **Purpose**: Dynamic fee calculation based on market conditions and VPIN
- **Functionality**:
  - Simulates fee structures based on VPIN metrics
  - Analyzes fee revenue across different market conditions
  - Models LP performance with dynamic fee adjustments
  - Combines position data with fee calculations
- **Key Features**: VPIN-based fee adjustments, revenue optimization

#### `calculate_total_fees.py`

- **Purpose**: Aggregates and analyzes fee data across different scenarios
- **Functionality**: Calculates total fees, fee percentages, and revenue metrics

#### `plot_fee_percentages.py`

- **Purpose**: Visualizes fee structures and percentages
- **Functionality**: Creates charts showing fee distributions and trends

#### `explain_fee_logic_demo.py`

- **Purpose**: Demonstrates and explains the fee calculation logic
- **Functionality**: Provides educational examples of fee calculations

#### `find_sample_swaps.py`

- **Purpose**: Identifies interesting trading patterns for analysis
- **Functionality**: Finds sample swaps that demonstrate key concepts

## 📈 Key Research Findings

### 1. Price Impact Analysis

- **Power Law Relationship**: Confirmed power law relationship between trade volume and price impact
- **Volume Efficiency**: Larger trades show lower price impact per unit volume
- **ILLIQ Patterns**: Amihud illiquidity measure varies significantly across volume bins

### 2. VPIN Analysis

- **Market Microstructure**: VPIN metrics reveal information asymmetry patterns
- **Time Horizons**: Different VPIN timeframes (daily, 5-day, 7-day) show varying sensitivity
- **Order Imbalances**: Volume-synchronized buckets reveal systematic order flow patterns

### 3. LP Position Modeling

- **Range Factor Impact**: Different range factors (r) significantly affect position performance
- **Inventory Exposure**: Token composition varies dramatically across price ranges
- **Impermanent Loss**: Quantified IL for different position configurations

### 4. Fee Optimization

- **VPIN-Based Fees**: Dynamic fee structures based on market microstructure
- **Revenue Optimization**: Fee adjustments based on information asymmetry
- **Performance Metrics**: Comprehensive analysis of fee revenue across scenarios

## 🚀 Usage Workflow

### 1. Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd Research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Analysis

Edit `config.toml` to specify:

- Pool addresses to analyze
- Date ranges for data collection
- RPC endpoints and API keys

### 3. Data Collection Pipeline

```bash
# Fetch raw blockchain data
python scripts/run_demeter_fetch.py

# Combine and preprocess data
python scripts/combine_minute_csvs.py
```

### 4. Analysis Pipeline

```bash
# Price impact analysis
python scripts/visualize_Price_impact.py

# VPIN calculation
python scripts/vpin_calculator.py

# LP position modeling
python scripts/inv_exposure_sim.py

# Fee simulation
python scripts/fee_calculation_sim.py
```

## 📊 Data Organization

### Pool-Specific Data

Each pool address gets its own directory under `data/`:

```
data/
├── 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640/  # USDC/ETH pool
│   ├── ethereum-0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640-*.minute.csv
│   ├── all_days_combined_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640.csv
│   ├── all_days_combined_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640_vpin_analysis.csv
│   ├── comprehensive_price_impact_analysis_*.png
│   └── comprehensive_raw_data_analysis_*.png
```

### LP Analysis Results

```
inventory exposure sim/
├── uniswap_v3_lp_analysis_r*.xlsx  # Excel reports for different range factors
├── presentation_combined_plot.png   # Combined visualization
└── r2_price_impact_il_bar_chart.png # R² analysis chart
```

## 🔧 Configuration

The `config.toml` file controls:

- **Pool Addresses**: Uniswap V3 pool addresses to analyze
- **Date Ranges**: Start and end dates for data collection
- **RPC Settings**: Ethereum node endpoints and API keys
- **Output Settings**: Data storage locations and formats

## 📋 Dependencies

Key Python packages:

- `pandas`, `numpy`: Data manipulation and analysis
- `matplotlib`, `seaborn`: Visualization
- `zelos-demeter`: Blockchain data fetching
- `toml`: Configuration management
- `python-dotenv`: Environment variable management

## 🎓 Research Applications

This research has applications in:

- **DeFi Protocol Design**: Optimizing fee structures and liquidity provision
- **Market Making**: Understanding price impact and market microstructure
- **Risk Management**: Quantifying impermanent loss and inventory exposure
- **Academic Research**: Market microstructure analysis in decentralized markets

## 📄 License

[Add your license information here]

## 🤝 Contributing

This research project provides a comprehensive framework for analyzing Uniswap V3 pools. Contributions are welcome for:

- Additional analysis methods
- New visualization techniques
- Extended market microstructure metrics
- Performance optimizations

---

_This research project combines blockchain data analysis, market microstructure theory, and quantitative modeling to provide deep insights into DeFi market dynamics and liquidity provision strategies._
