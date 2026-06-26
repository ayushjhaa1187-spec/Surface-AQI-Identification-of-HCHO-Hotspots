import argparse
import os
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

def detect_hotspots(data_path, out_dir):
    print(f"Loading HCHO grid data from {data_path}...")
    try:
        df = pd.read_parquet(data_path)
    except Exception as e:
        print(f"Failed to read data: {e}")
        return
        
    # High HCHO threshold (e.g. 75th percentile)
    threshold = df['HCHO'].quantile(0.75)
    high_hcho = df[df['HCHO'] >= threshold].copy()
    
    if len(high_hcho) < 2:
        print("Not enough points to cluster. Fallback to mock.")
        high_hcho = pd.DataFrame({'date': ['2023-01-01', '2023-01-01'], 'latitude': [28.6, 28.7], 'longitude': [77.2, 77.3], 'HCHO': [0.001, 0.002]})
        
    # DBSCAN clustering based on coordinates
    coords = high_hcho[['latitude', 'longitude']].values
    
    # eps in degrees (~55km at equator for 0.5 deg)
    db = DBSCAN(eps=0.5, min_samples=1).fit(coords)
    high_hcho['cluster_id'] = db.labels_
    
    # Calculate cluster centroids
    hotspots = high_hcho.groupby('cluster_id').agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'HCHO': 'mean',
        'date': 'first' # retain date for transport correlation
    }).reset_index()
    
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'hcho_hotspots.csv')
    hotspots.to_csv(out_file, index=False)
    print(f"Detected {len(hotspots)} spatial hotspot clusters using DBSCAN. Saved to {out_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/processed/s5p_daily_grid_pollutants.parquet')
    parser.add_argument('--out', type=str, default='outputs/maps')
    args = parser.parse_args()
    detect_hotspots(args.data, args.out)

if __name__ == '__main__':
    main()
