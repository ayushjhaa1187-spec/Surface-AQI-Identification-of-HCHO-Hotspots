import argparse
import os
import pandas as pd
import numpy as np

def calculate_transport(firms, era5):
    """Calculate basic wind transport vector from fire locations"""
    # Merge fires with meteorology to get wind vectors
    # Simplified mock approach: map nearest wind vector to fire
    # Assumes lat/lon columns exist
    firms['date'] = pd.to_datetime(firms['date'])
    era5['date'] = pd.to_datetime(era5['date'])
    df = pd.merge(firms, era5, on=['date'], how='left')
    df = df.dropna(subset=['u10', 'v10'])
    
    if len(df) == 0:
        return firms, 0.0, 0.0
        
    # Average wind vector over the fires for the day
    mean_u = df['u10'].mean()
    mean_v = df['v10'].mean()
    
    # Simple displacement approximation (degrees per day)
    # 1 m/s is roughly 0.009 degrees per hour, ~0.2 degrees per day
    deg_per_ms = 0.2
    disp_lon = mean_u * deg_per_ms
    disp_lat = mean_v * deg_per_ms
    
    return df, disp_lon, disp_lat

def analyze_transport(hotspots_path, firms_path, era5_path, out_dir):
    print("Analyzing fire-HCHO transport using wind vectors...")
    try:
        hotspots = pd.read_csv(hotspots_path)
        firms = pd.read_csv(firms_path)
        era5 = pd.read_parquet(era5_path)
        
        # We need a date column for matching.
        # If mock missing, fallback
        if 'date' not in hotspots.columns:
            hotspots['date'] = '2023-01-01'
            
        print(f"Found {len(hotspots)} hotspots and {len(firms)} fire points.")
        
        _, disp_lon, disp_lat = calculate_transport(firms, era5)
        
        # Shift fire centroids by wind transport
        fire_centroid_lon = firms['longitude'].mean() + disp_lon
        fire_centroid_lat = firms['latitude'].mean() + disp_lat
        
        # Calculate distance from wind-displaced fire centroid to HCHO hotspots
        hotspots['dist_to_plume'] = np.sqrt(
            (hotspots['longitude'] - fire_centroid_lon)**2 + 
            (hotspots['latitude'] - fire_centroid_lat)**2
        )
        
        # Simple correlation/alignment check
        aligned_hotspots = len(hotspots[hotspots['dist_to_plume'] < 1.0])
        alignment_score = aligned_hotspots / len(hotspots) if len(hotspots) > 0 else 0
        
        print(f"Wind Displacement Vector -> dLon: {disp_lon:.2f}, dLat: {disp_lat:.2f}")
        print(f"Hotspot Plume Alignment Score: {alignment_score:.2f}")
        
        os.makedirs(out_dir, exist_ok=True)
        metrics_file = os.path.join(out_dir, 'transport_metrics.csv')
        pd.DataFrame({
            'Wind_U_Disp': [disp_lon],
            'Wind_V_Disp': [disp_lat],
            'Alignment_Score': [alignment_score]
        }).to_csv(metrics_file, index=False)
        print(f"Saved transport metrics to {metrics_file}")
        
    except Exception as e:
        print(f"Error during transport analysis: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hotspots', type=str, default='outputs/maps/hcho_hotspots.csv')
    parser.add_argument('--firms', type=str, default='data/processed/firms_daily_fire_counts.csv')
    parser.add_argument('--era5', type=str, default='data/processed/era5_daily_meteorology.parquet')
    parser.add_argument('--out', type=str, default='outputs/reports')
    args = parser.parse_args()
    analyze_transport(args.hotspots, args.firms, args.era5, args.out)

if __name__ == '__main__':
    main()
