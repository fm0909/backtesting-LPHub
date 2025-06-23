# Research Project

This repository contains research tools and analysis scripts for blockchain data analysis, specifically focused on price impact analysis and VPIN (Volume-synchronized Probability of Informed Trading) calculations.

## Project Structure

- `scripts/` - Directory containing all analysis scripts
  - `run_demeter_fetch.py` - Script to fetch raw blockchain data using Demeter
  - `combine_minute_csvs.py` - Script to combine minute-level CSV data files into consolidated datasets
  - `visualize_Price_impact.py` - Visualization script for price impact analysis
  - `vpin_calculator.py` - VPIN calculation implementation
  - `inv_exposure_sim.py` - Uniswap V3 LP position analysis and inventory exposure simulation
- `config.toml` - Configuration file
- `requirements.txt` - Python dependencies
- `data/` - Directory containing analysis data and results
- `inventory exposure sim/` - Directory containing LP analysis results and plots

## Setup

1. Clone the repository:

```bash
git clone https://github.com/fm0909/research-hookathon.git
cd research-hookathon
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage Workflow

The analysis follows a specific workflow where each script takes a pool address as input and stores data accordingly:

### 1. Fetch Raw Data with Demeter

First, use the Demeter fetch script to collect raw blockchain data for a specific pool:

```bash
python scripts/run_demeter_fetch.py
```

This will fetch raw data and store it in the `data/<pool_address>/` directory based on the configuration in `config.toml`.

### 2. Combine Minute CSV Files

After fetching data, combine the minute-level CSV files into consolidated datasets:

```bash
python scripts/combine_minute_csvs.py
```

This creates consolidated CSV files that contain all the minute-level data for analysis.

### 3. Run Visualization Script

Generate price impact visualizations and analysis:

```bash
python scripts/visualize_Price_impact.py
```

This will create comprehensive price impact analysis charts and store them in the `data/<pool_address>/` directory.

### 4. Calculate VPIN Metrics

Run the VPIN calculator to compute Volume-synchronized Probability of Informed Trading metrics:

```bash
python scripts/vpin_calculator.py
```

This generates VPIN analysis results and stores them in the `data/<pool_address>/` directory.

### 5. Run Inventory Exposure Simulation

Analyze Uniswap V3 LP positions and inventory exposure:

```bash
python scripts/inv_exposure_sim.py
```

This creates comprehensive LP analysis with different range factors and saves results to the `inventory exposure sim/` directory.

## Data Organization

Each pool address gets its own directory under `data/`:

```
data/
├── 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640/
│   ├── ethereum-0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640-*.minute.csv
│   ├── all_days_combined_0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640.csv
│   ├── comprehensive_price_impact_analysis_*.png
│   └── vpin_analysis_*.csv
└── [other_pool_addresses]/
```

LP analysis results are stored in:

```
inventory exposure sim/
├── uniswap_v3_lp_analysis_r*.xlsx
└── presentation_combined_plot.png
```

## Configuration

Edit `config.toml` to customize analysis parameters, date ranges, and other settings.

## License

[Add your license information here]
