import argparse
import os
import pandas as pd
import numpy as np
import joblib

def generate_aqi_maps(model_path, output_dir):
    print(f"Loading model from {model_path}...")
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        print("Model not found. Run train_model.py first.")
        return
        
    print("Generating mock India grid for mapping...")
    lats = np.linspace(6.0, 38.0, 10)
    lons = np.linspace(68.0, 98.0, 10)
    grid_lats, grid_lons = np.meshgrid(lats, lons)
    
    df_grid = pd.DataFrame({
        'latitude': grid_lats.flatten(),
        'longitude': grid_lons.flatten()
    })
    
    df_grid['HCHO'] = np.random.rand(len(df_grid)) * 0.001
    df_grid['NO2_column'] = np.random.rand(len(df_grid)) * 0.005
    df_grid['u10'] = np.random.rand(len(df_grid)) * 2
    df_grid['v10'] = np.random.rand(len(df_grid)) * 2
    df_grid['t2m'] = 290.0
    df_grid['blh'] = 1000.0
    
    print("Predicting PM2.5 for grid...")
    features = ['latitude', 'longitude', 'HCHO', 'NO2_column', 'u10', 'v10', 't2m', 'blh']
    preds = model.predict(df_grid[features])
    df_grid['predicted_PM2.5'] = preds
    
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'daily_aqi_map_20230101.csv')
    df_grid.to_csv(out_path, index=False)
    print(f"Saved AQI map data to {out_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate AQI Maps.')
    parser.add_argument('--model', type=str, default='models/rf_baseline_model.joblib')
    parser.add_argument('--out', type=str, default='outputs/maps')
    args = parser.parse_args()
    generate_aqi_maps(args.model, args.out)

if __name__ == '__main__':
    main()
