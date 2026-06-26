import argparse
import os
import pandas as pd
try:
    import ee
except ImportError:
    ee = None

def process_s5p_mock(input_path, output_dir):
    print(f'Reading mock Sentinel-5P data from {input_path}')
    df = pd.read_parquet(input_path)
    df['date'] = pd.to_datetime(df['date'])
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 's5p_daily_grid_pollutants.parquet')
    df.to_parquet(out_path, index=False)
    print(f'Saved processed mock S5P data to {out_path}')

def fetch_s5p_real(date_str, output_dir):
    if ee is None:
        print("Please install earthengine-api (pip install earthengine-api)")
        return
        
    try:
        ee.Initialize()
    except Exception as e:
        print("Earth Engine not initialized. Run `earthengine authenticate` in your terminal.")
        return
        
    print(f"Fetching real Sentinel-5P TROPOMI data for {date_str} from Google Earth Engine...")
    
    # Define India bounds roughly
    india_bounds = ee.Geometry.Rectangle([68.0, 6.0, 98.0, 38.0])
    
    # HCHO collection
    hcho_coll = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_HCHO") \
        .select('tropospheric_HCHO_column_number_density') \
        .filterDate(f'{date_str}', pd.to_datetime(date_str).strftime('%Y-%m-%d')) \
        .mean()
        
    # NO2 collection
    no2_coll = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2") \
        .select('tropospheric_NO2_column_number_density') \
        .filterDate(f'{date_str}', pd.to_datetime(date_str).strftime('%Y-%m-%d')) \
        .mean()
        
    # Combine
    combined = hcho_coll.addBands(no2_coll)
    
    # Sample regions to get a dataframe
    print("Sampling regions to create spatial grid (this may take a moment)...")
    try:
        samples = combined.sample(
            region=india_bounds,
            scale=10000, # 10km resolution for manageable size
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
                'HCHO': props.get('tropospheric_HCHO_column_number_density', 0),
                'NO2_column': props.get('tropospheric_NO2_column_number_density', 0)
            })
            
        df = pd.DataFrame(records)
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, 's5p_daily_grid_pollutants.parquet')
        df.to_parquet(out_path, index=False)
        print(f"Saved real S5P data to {out_path} with {len(df)} points.")
        
    except Exception as e:
        print(f"Failed to sample Earth Engine data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Prepare Sentinel-5P data.')
    parser.add_argument('--mock', type=str, help='Path to mock S5P Parquet')
    parser.add_argument('--date', type=str, default='2023-01-01', help='Date for real API fetch')
    parser.add_argument('--out', type=str, default='data/processed', help='Output directory')
    args = parser.parse_args()
    
    if args.mock:
        process_s5p_mock(args.mock, args.out)
    else:
        fetch_s5p_real(args.date, args.out)

if __name__ == '__main__':
    main()
