import argparse
import os
import pandas as pd

def process_cpcb_data(input_path, output_dir):
    print(f'Reading CPCB data from {input_path}')
    df = pd.read_csv(input_path)
    expected_cols = ['date', 'station_id', 'latitude', 'longitude', 'PM2.5', 'PM10', 'NO2']
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f'Missing expected column: {col}')
    df['date'] = pd.to_datetime(df['date'])
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'cpcb_daily_station_pollutants.csv')
    df.to_csv(out_path, index=False)
    print(f'Saved processed CPCB data to {out_path}')

def main():
    parser = argparse.ArgumentParser(description='Download and process CPCB station data.')
    parser.add_argument('--mock', type=str, help='Path to mock CPCB CSV for testing')
    parser.add_argument('--out', type=str, default='data/processed', help='Output directory')
    args = parser.parse_args()
    if args.mock:
        process_cpcb_data(args.mock, args.out)
    else:
        print('Real CPCB download not fully implemented. Please use --mock.')

if __name__ == '__main__':
    main()
