import argparse
import os
import pandas as pd

def process_insat3d(mock_path, out_dir):
    print(f"Reading INSAT-3D data from {mock_path}")
    df = pd.read_parquet(mock_path)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'insat3d_daily_aod.parquet')
    df.to_parquet(out_file, index=False)
    print(f"Saved processed INSAT-3D data to {out_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', type=str, help='Path to mock INSAT-3D Parquet')
    parser.add_argument('--out', type=str, default='data/processed')
    args = parser.parse_args()
    
    if args.mock:
        process_insat3d(args.mock, args.out)
    else:
        print('Real INSAT-3D download not fully implemented. Please use --mock.')

if __name__ == '__main__':
    main()
