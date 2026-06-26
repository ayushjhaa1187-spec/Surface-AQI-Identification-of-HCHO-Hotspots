import argparse
import os
import pandas as pd
try:
    import ee
except ImportError:
    ee = None

def process_era5_mock(input_path, output_dir):
    print(f'Reading mock ERA5 data from {input_path}')
    df = pd.read_parquet(input_path)
    df['date'] = pd.to_datetime(df['date'])
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'era5_daily_meteorology.parquet')
    df.to_parquet(out_path, index=False)
    print(f'Saved processed mock ERA5 data to {out_path}')

def fetch_era5_real(date_str, output_dir):
    if ee is None:
        print("Please install earthengine-api (pip install earthengine-api)")
        return
        
    try:
        ee.Initialize()
    except Exception as e:
        print("Earth Engine not initialized. Run `earthengine authenticate` in your terminal.")
        return
        
    print(f"Fetching real ERA5 Meteorology data for {date_str} from Google Earth Engine...")
    
    india_bounds = ee.Geometry.Rectangle([68.0, 6.0, 98.0, 38.0])
    
    # ERA5 Daily Aggregates collection
    era5_coll = ee.ImageCollection("ECMWF/ERA5/DAILY") \
        .select(['u_component_of_wind_10m', 'v_component_of_wind_10m', 'mean_2m_air_temperature']) \
        .filterDate(f'{date_str}', pd.to_datetime(date_str).strftime('%Y-%m-%d')) \
        .mean()
        
    print("Sampling meteorology regions (this may take a moment)...")
    try:
        samples = era5_coll.sample(
            region=india_bounds,
            scale=25000, # 25km resolution
            numPixels=1000,
            geometries=True
        ).getInfo()
        
        records = []
        for feat in samples['features']:
            coords = feat['geometry']['coordinates']
            props = feat['properties']
            records.append({
                'date': pd.to_datetime(date_str),
                'longitude': coords[0],
                'latitude': coords[1],
                'u10': props.get('u_component_of_wind_10m', 0),
                'v10': props.get('v_component_of_wind_10m', 0),
                't2m': props.get('mean_2m_air_temperature', 290.0),
                'blh': 1000.0 # BLH might not be in daily, defaulting
            })
            
        df = pd.DataFrame(records)
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, 'era5_daily_meteorology.parquet')
        df.to_parquet(out_path, index=False)
        print(f"Saved real ERA5 data to {out_path} with {len(df)} points.")
        
    except Exception as e:
        print(f"Failed to sample Earth Engine data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Prepare ERA5 data.')
    parser.add_argument('--mock', type=str, help='Path to mock ERA5 Parquet')
    parser.add_argument('--date', type=str, default='2023-01-01', help='Date for real API fetch')
    parser.add_argument('--out', type=str, default='data/processed', help='Output directory')
    args = parser.parse_args()
    
    if args.mock:
        process_era5_mock(args.mock, args.out)
    else:
        fetch_era5_real(args.date, args.out)

if __name__ == '__main__':
    main()
