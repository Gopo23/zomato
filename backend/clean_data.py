import sys
import os

# Add backend to path to import DataService
sys.path.append(os.path.abspath('backend'))

import pandas as pd
from services.data_service import DataService

cache_path = 'backend/data/zomato_dataset.csv'
cleaned_path = 'backend/data/zomato_cleaned.csv'

print(f"Loading raw dataset from {cache_path}...")
df = pd.read_csv(cache_path)
print(f"Raw shape: {df.shape}")

print("Cleaning...")
df_cleaned = DataService._clean(df)
print(f"Cleaned shape: {df_cleaned.shape}")

df_cleaned.to_csv(cleaned_path, index=False)
print(f"Saved cleaned dataset to {cleaned_path}")
print(f"Size: {os.path.getsize(cleaned_path) / 1024 / 1024:.2f} MB")
