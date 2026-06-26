import argparse
import os
import pandas as pd

def build_training_table(processed_dir):
    cpcb_path = os.path.join(processed_dir, 'cpcb_daily_station_pollutants.csv')
    s5p_path = os.path.join(processed_dir, 's5p_daily_grid_pollutants.parquet')
    era5_path = os.path.join(processed_dir, 'era5_daily_meteorology.parquet')
    insat_path = os.path.join(processed_dir, 'insat3d_daily_aod.parquet')
    
    print("Loading processed datasets...")
    cpcb_df = pd.read_csv(cpcb_path)
    cpcb_df['date'] = pd.to_datetime(cpcb_df['date'])
    
    s5p_df = pd.read_parquet(s5p_path)
    era5_df = pd.read_parquet(era5_path)
    insat_df = pd.read_parquet(insat_path)
    
    print("Collocating datasets...")
    merged_df = pd.merge(cpcb_df, s5p_df, on=['date', 'latitude', 'longitude'], how='left')
    merged_df = pd.merge(merged_df, era5_df, on=['date', 'latitude', 'longitude'], how='left')
    merged_df = pd.merge(merged_df, insat_df, on=['date', 'latitude', 'longitude'], how='left')
    
    merged_df.fillna(0, inplace=True)
    
    out_path = os.path.join(processed_dir, 'collocated_training_table.parquet')
    merged_df.to_parquet(out_path, index=False)
    print(f"Saved training table to {out_path} with shape {merged_df.shape}")

def main():
    parser = argparse.ArgumentParser(description='Build collocated training table.')
    parser.add_argument('--dir', type=str, default='data/processed', help='Processed data directory')
    args = parser.parse_args()
    build_training_table(args.dir)

if __name__ == '__main__':
    main()
