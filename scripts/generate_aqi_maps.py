import argparse
import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import joblib

class CNN_LSTM(nn.Module):
    def __init__(self, input_dim):
        super(CNN_LSTM, self).__init__()
        self.cnn = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.lstm = nn.LSTM(input_size=16, hidden_size=32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.relu(self.cnn(x))
        x = x.permute(0, 2, 1)
        out, (hn, cn) = self.lstm(x)
        out = hn[-1]
        out = self.fc(out)
        return out.squeeze()

def generate_aqi_maps(model_path, output_dir):
    print(f"Loading deep learning model from {model_path}...")
    try:
        features = joblib.load(os.path.join(os.path.dirname(model_path), 'model_features.joblib'))
    except FileNotFoundError:
        print("Model features not found. Run train_model.py first.")
        return
        
    model = CNN_LSTM(input_dim=len(features))
    try:
        model.load_state_dict(torch.load(model_path))
        model.eval()
    except Exception as e:
        print(f"Could not load PyTorch model: {e}")
        return
        
    print("Generating mock India grid for mapping...")
    lats = np.linspace(6.0, 38.0, 10)
    lons = np.linspace(68.0, 98.0, 10)
    grid_lats, grid_lons = np.meshgrid(lats, lons)
    
    df_grid = pd.DataFrame({
        'latitude': grid_lats.flatten(),
        'longitude': grid_lons.flatten()
    })
    
    # Fill in the features based on what the model expects
    for f in features:
        if f not in df_grid.columns:
            df_grid[f] = np.random.rand(len(df_grid))
            
    print("Predicting PM2.5 for grid using CNN-LSTM...")
    
    X_t = torch.tensor(df_grid[features].values, dtype=torch.float32)
    with torch.no_grad():
        preds = model(X_t)
        if preds.dim() == 0:
            preds = preds.unsqueeze(0)
        preds = preds.numpy()
        
    df_grid['predicted_PM2.5'] = preds
    
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'daily_aqi_map_20230101.csv')
    df_grid.to_csv(out_path, index=False)
    print(f"Saved AQI map data to {out_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate AQI Maps.')
    parser.add_argument('--model', type=str, default='models/cnn_lstm_model.pt')
    parser.add_argument('--out', type=str, default='outputs/maps')
    args = parser.parse_args()
    generate_aqi_maps(args.model, args.out)

if __name__ == '__main__':
    main()
