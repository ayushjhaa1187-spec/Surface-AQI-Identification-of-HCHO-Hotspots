import argparse
import os
import pandas as pd

def process_firms_data(input_path, output_dir):
    print(f'Reading FIRMS data from {input_path}')
    df = pd.read_csv(input_path)
    df['date'] = pd.to_datetime(df['date'])
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'firms_daily_fire_counts.csv')
    df.to_csv(out_path, index=False)
    print(f'Saved processed FIRMS data to {out_path}')

def main():
    parser = argparse.ArgumentParser(description='Download and process FIRMS data.')
    parser.add_argument('--mock', type=str, help='Path to mock FIRMS CSV')
    parser.add_argument('--out', type=str, default='data/processed', help='Output directory')
    args = parser.parse_args()
    if args.mock:
        process_firms_data(args.mock, args.out)
    else:
        print('Real FIRMS download not fully implemented. Please use --mock.')

if __name__ == '__main__':
    main()
