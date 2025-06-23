import demeter
import toml
import traceback
import sys
import pandas as pd
import os

# Step 1: Define fetch config
config_file = os.path.join("..", "config.toml")  # TOML configuration file

# Step 2: Load and Debug Config
config_data = toml.load(config_file)
print("🔍 Debug: Loaded config.toml content:")
print(config_data)

# Get pool address from config and set output_dir accordingly
pool_address = config_data['from']['uniswap']['pool_address'].lower()
output_dir = os.path.join("..", "data", pool_address)
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# Step 3: Fetch data
print("Fetching Uniswap v3 data...")

try:
    print("✅ Running fetch.download() now...")
    sys.stdout.flush()  # Force output to be printed immediately

    import demeter_fetch.main as fetch
    fetch.download(config_file)

    print("✅ fetch.download() completed successfully!")
except Exception as e:
    print("❌ Error occurred while fetching data:", e)
    print("🔍 Capturing full traceback...")
    traceback.print_exc()

# Step 4: Verify output files
print("📂 Checking if output files exist...")

if not os.path.exists(output_dir):
    print(f"❌ Error: Output directory '{output_dir}' does not exist.")
    sys.exit(1)

output_files = [f for f in os.listdir(output_dir) if f.endswith('.minute.csv')]
if not output_files:
    print(f"❌ Error: No '.minute.csv' files found in '{output_dir}'.")
    sys.exit(1)

print(f"✅ Found {len(output_files)} '.minute.csv' files in '{output_dir}'.")
