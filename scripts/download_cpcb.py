import argparse
import os
import pandas as pd

def process_cpcb_mock(input_path, output_dir):
    print(f'Reading mock CPCB data from {input_path}')
    df = pd.read_csv(input_path)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'cpcb_daily_station_pollutants.csv')
    df.to_csv(out_path, index=False)
    print(f'Saved processed mock CPCB data to {out_path}')

def process_cpcb_real(csv_path, output_dir):
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found. Please provide a path to a downloaded CPCB CSV.")
        return
        
    print(f"Parsing real CPCB ground truth data from {csv_path}...")
    try:
        # Standard CPCB CSV format parsing logic (adapt as needed)
        df = pd.read_csv(csv_path)
        
        # Ensure standard column names
        rename_map = {
            'Date': 'date', 'From Date': 'date',
            'Station': 'station_id',
            'Latitude': 'latitude', 'Longitude': 'longitude'
        }
        df = df.rename(columns=rename_map)
        
        # Coerce date format
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, 'cpcb_daily_station_pollutants.csv')
        df.to_csv(out_path, index=False)
        print(f"Saved {len(df)} parsed CPCB records to {out_path}")
        
    except Exception as e:
        print(f"Failed to parse CPCB data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Process CPCB data.')
    parser.add_argument('--mock', type=str, help='Path to mock CPCB CSV')
    parser.add_argument('--real', type=str, help='Path to real CPCB CSV download')
    parser.add_argument('--out', type=str, default='data/processed', help='Output directory')
    args = parser.parse_args()
    
    if args.mock:
        process_cpcb_mock(args.mock, args.out)
    elif args.real:
        process_cpcb_real(args.real, args.out)
    else:
        print("Please provide either --mock or --real with a path.")

if __name__ == '__main__':
    main()
