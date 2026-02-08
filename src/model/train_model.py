import pandas as pd
import numpy as np
import re
import os
import joblib
import json
from sklearn.ensemble import RandomForestRegressor

# Increase recursion depth just in case, though usually not needed for simple RF
import sys
sys.setrecursionlimit(2000)

# --- CONFIG ---
RAW_DATA_PATH = 'data/raw/sauto_raw_data.csv'
MODEL_PATH = 'src/model/car_price_model.pkl'
COLUMNS_PATH = 'src/model/model_columns.pkl'
METADATA_PATH = 'src/model/model_metadata.json'

def parse_year(text):
    # Try finding 4 digits at start of string (e.g. "2022, ...")
    match_start = re.match(r'^\s*(\d{4})', str(text))
    if match_start:
        return int(match_start.group(1))
    
    # Fallback: look for "Rok výroby: 2022"
    match = re.search(r'Rok výroby:\s*(\d{4})', str(text))
    if match:
        return int(match.group(1))
        
    return None

def parse_mileage(text):
    # Try finding "XX XXX km" anywhere
    # Matches "18 455 km", "146 589 km"
    # Remove spaces inside the number group
    match = re.search(r'(\d[\d\s]*)\s*km', str(text))
    if match:
        clean_num = match.group(1).replace(' ', '').replace('\xa0', '')
        try:
            return int(clean_num)
        except:
            return None
    return None

def parse_fuel(text):
    fuels = ['Benzín', 'Nafta', 'Elektro', 'LPG', 'Hybridní', 'CNG']
    for f in fuels:
        if f in str(text):
            return f
    return 'Other'

def parse_transmission(text):
    if 'Automatická' in str(text):
        return 'Automatická'
    return 'Manuální'

def clean_brand(title):
    brand = None
    
    # Filter garbage (URLs, etc)
    if 'http' in str(title) or 'www' in str(title) or '.cz' in str(title):
        # Try to extract brand from URL structure: .../detail/brand/model/...
        try:
            parts = str(title).split('/')
            if 'detail' in parts:
                idx = parts.index('detail')
                if len(parts) > idx + 1:
                    brand = parts[idx + 1]
        except:
            pass
    else:
        # Normal case: split by newline/space
        if pd.isna(title):
             return 'Unknown'
        first_line = str(title).split('\n')[0]
        brand = first_line.split()[0].replace(',', '').strip()

    if not brand: return None

    # Normalize
    brand = brand.capitalize()
    if brand.lower() == 'bmw': return 'BMW'
    if brand.lower() == 'mercedes-benz': return 'Mercedes-Benz'
    if brand.lower() == 'vw' or brand.lower() == 'volkswagen': return 'Volkswagen'
    if brand.lower() == 'skoda' or brand.lower() == 'škoda': return 'Škoda'
    
    return brand

def train():
    print("Loading data...")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Error: {RAW_DATA_PATH} not found.")
        return

    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Loaded {len(df)} rows.")

    # 1. Feature Extraction
    print("Extracting features...")
    df['year'] = df['description'].apply(parse_year)
    df['mileage'] = df['description'].apply(parse_mileage)
    df['fuel'] = df['description'].apply(parse_fuel)
    df['transmission'] = df['description'].apply(parse_transmission)
    df['brand'] = df['title'].apply(clean_brand)

    # 2. Cleaning
    print("Cleaning data...")
    
    # Parse Price first
    df['price'] = df['raw_price'].astype(str).str.replace(r'[^\d]', '', regex=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    print("\n--- Missing Values Check ---")
    print(df[['year', 'mileage', 'price', 'brand']].isnull().sum())
    
    # Remove rows with missing essential data
    df = df.dropna(subset=['year', 'mileage', 'price', 'brand'])
    
    df = df[df['price'] > 1000] # Remove placeholders

    # Filter Brands (Keep top 30)
    top_brands = df['brand'].value_counts().head(30).index.tolist()
    df = df[df['brand'].isin(top_brands)]

    print(f"Data after cleaning: {len(df)} rows.")
    print("Top Brands:", top_brands)

    # 3. Generate Metadata (Valid Combinations)
    print("Generating metadata...")
    metadata = {}
    for brand in df['brand'].unique():
        brand_df = df[df['brand'] == brand]
        metadata[brand] = {
            'fuels': sorted(brand_df['fuel'].unique().tolist()),
            'transmissions': sorted(brand_df['transmission'].unique().tolist()),
            'min_year': int(brand_df['year'].min()),
            'max_year': int(brand_df['year'].max())
        }

    with open(METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved to {METADATA_PATH}")

    # 4. Prepare for Training
    features = ['year', 'mileage', 'brand', 'fuel', 'transmission']
    X = df[features]
    y = df['price']

    # One-Hot Encoding
    # Ensure consistent handling of categorical variables
    # We use pd.get_dummies
    X = pd.get_dummies(X, columns=['brand', 'fuel', 'transmission'], drop_first=False)
    # Note: drop_first=False ensures we have explicit columns for all values, 
    # which is safer for our inference mapping logic (we look for brand_BMW, not absence of others)
    
    # Calculate average price per brand for sanity check
    print("\n--- Average Price per Brand (Sample) ---")
    print(df.groupby('brand')['price'].mean().head(5))

    # 5. Train Model
    print("\nTraining Random Forest...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("Model training complete.")

    # 6. Save Artifacts
    joblib.dump(model, MODEL_PATH)
    joblib.dump(list(X.columns), COLUMNS_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Columns saved to {COLUMNS_PATH}")

if __name__ == "__main__":
    train()
