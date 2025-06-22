# Research Project

This repository contains research tools and analysis scripts for blockchain data analysis, specifically focused on price impact analysis and VPIN (Volume-synchronized Probability of Informed Trading) calculations.

## Project Structure

- `combine_minute_csvs.py` - Script to combine minute-level CSV data files
- `run_demeter_fetch.py` - Script to fetch data using Demeter
- `visualize_Price_impact.py` - Visualization script for price impact analysis
- `vpin_calculator.py` - VPIN calculation implementation
- `config.toml` - Configuration file
- `requirements.txt` - Python dependencies
- `data/` - Directory containing analysis data and results

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd Research
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

## Usage

The project contains several analysis scripts for blockchain data processing and visualization. Each script can be run independently based on your analysis needs.

## Data

The `data/` directory contains processed CSV files and analysis results for different blockchain addresses and time periods.

## License

[Add your license information here]
