import argparse
import os
import pandas as pd
import requests

def process_firms_mock(input_path, output_dir):
    print(f'Reading mock FIRMS data from {input_path}')
    df = pd.read_csv(input_path)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'firms_daily_fire_counts.csv')
    df.to_csv(out_path, index=False)
    print(f'Saved processed mock FIRMS data to {out_path}')

def fetch_firms_real(date_str, output_dir):
    # This requires a free NASA FIRMS API Map Key
    # https://firms.modaps.eosdis.nasa.gov/api/
    api_key = os.environ.get('FIRMS_API_KEY')
    if not api_key:
        print("FIRMS_API_KEY environment variable not found. Fallback to mock behavior or provide key.")
        return
        
    print(f"Fetching real FIRMS active fire data for {date_str}...")
    
    # Area for India (approx): South, West, North, East (minX, minY, maxX, maxY)
    # FIRMS uses: xmin, ymin, xmax, ymax
    area = "68.0,6.0,98.0,38.0"
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{area}/1/{date_str}"
    
    try:
        df = pd.read_csv(url)
        if len(df) > 0:
            df['date'] = pd.to_datetime(df['acq_date'])
            df = df[['date', 'latitude', 'longitude', 'confidence', 'frp']]
            
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, 'firms_daily_fire_counts.csv')
            df.to_csv(out_path, index=False)
            print(f"Saved {len(df)} real fire points to {out_path}")
        else:
            print("No fire data found for the specified region and date.")
    except Exception as e:
        print(f"Failed to fetch real FIRMS data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Download FIRMS data.')
    parser.add_argument('--mock', type=str, help='Path to mock FIRMS CSV')
    parser.add_argument('--date', type=str, default='2023-01-01', help='Date for real API fetch')
    parser.add_argument('--out', type=str, default='data/processed', help='Output directory')
    args = parser.parse_args()
    
    if args.mock:
        process_firms_mock(args.mock, args.out)
    else:
        fetch_firms_real(args.date, args.out)

if __name__ == '__main__':
    main()
