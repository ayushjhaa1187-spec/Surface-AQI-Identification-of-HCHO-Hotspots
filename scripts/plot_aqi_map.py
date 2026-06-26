import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_map(data_path, out_dir):
    print(f"Plotting AQI map from {data_path}...")
    df = pd.read_csv(data_path)
    plt.figure(figsize=(8,6))
    plt.scatter(df['longitude'], df['latitude'], c=df['predicted_PM2.5'], cmap='Reds', s=100)
    plt.colorbar(label='Predicted PM2.5 AQI')
    plt.title('Daily PM2.5 Surface Map')
    
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'aqi_map_plot.png')
    plt.savefig(out_file)
    print(f"Saved plot to {out_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='outputs/maps/daily_aqi_map_20230101.csv')
    parser.add_argument('--out', type=str, default='outputs/maps')
    args = parser.parse_args()
    plot_map(args.data, args.out)

if __name__ == '__main__':
    main()
