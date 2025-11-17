import pandas as pd
import os

# Path to the dataset on Hugging Face
path = "hf://datasets/ctgadget/generated_sales_data/data/train-00000-of-00001.parquet"

# Load only first 1000 rows
df = pd.read_parquet(path, engine="pyarrow").head(1000)

# Ensure output directory exists
output_dir = "test_data"
os.makedirs(output_dir, exist_ok=True)

# Save to CSV
output_path = os.path.join(output_dir, "sample_1000_rows.csv")
df.to_csv(output_path, index=False)

print(f"Saved first 1000 rows to: {output_path}")