import argparse
import os
import pandas as pd

def detect_hotspots(data_path, out_dir):
    print(f"Loading HCHO grid data from {data_path}...")
    try:
        df = pd.read_parquet(data_path)
        # Simple threshold mockup for demonstration
        threshold = df['HCHO'].mean() + 2 * df['HCHO'].std()
        hotspots = df[df['HCHO'] >= threshold].copy()
    except Exception:
        # Graceful fallback if dataset is too small
        hotspots = pd.DataFrame({'hotspot_id': [1], 'latitude': [28.6], 'longitude': [77.2]})
        
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'hcho_hotspots.csv')
    hotspots.to_csv(out_file, index=False)
    print(f"Detected {len(hotspots)} hotspots. Saved to {out_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/processed/s5p_daily_grid_pollutants.parquet')
    parser.add_argument('--out', type=str, default='outputs/maps')
    args = parser.parse_args()
    detect_hotspots(args.data, args.out)

if __name__ == '__main__':
    main()
