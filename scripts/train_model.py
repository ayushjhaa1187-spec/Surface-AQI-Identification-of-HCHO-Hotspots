import argparse
import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
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

def train_model(data_path, out_dir):
    print(f"Loading training data from {data_path}...")
    df = pd.read_parquet(data_path)
    
    features = ['latitude', 'longitude', 'HCHO', 'NO2_column', 'u10', 'v10', 't2m', 'blh', 'AOD']
    available_features = [f for f in features if f in df.columns]
    
    if len(df) < 10:
        print("Not enough data to train. Expanding mock dataset.")
        df = pd.concat([df]*10, ignore_index=True)
        df['PM2.5'] = df['PM2.5'] + np.random.normal(0, 10, len(df))
        
    X = df[available_features].values
    y = df['PM2.5'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32)
    
    dataset = TensorDataset(X_train_t, y_train_t)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)
    
    model = CNN_LSTM(input_dim=len(available_features))
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    print("Training CNN-LSTM model...")
    epochs = 10
    for epoch in range(epochs):
        model.train()
        for batch_X, batch_y in dataloader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            # handle case where batch_size=1 and outputs is 0-dim
            if outputs.dim() == 0:
                outputs = outputs.unsqueeze(0)
            if batch_y.dim() == 0:
                batch_y = batch_y.unsqueeze(0)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
    model.eval()
    with torch.no_grad():
        preds = model(X_test_t)
        if preds.dim() == 0:
            preds = preds.unsqueeze(0)
        preds = preds.numpy()
        
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    if len(y_test) > 1 and np.var(y_test) > 0:
        r2 = r2_score(y_test, preds)
    else:
        r2 = 0.0
        
    print(f"Validation Metrics -> RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
    
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, 'cnn_lstm_model.pt')
    torch.save(model.state_dict(), model_path)
    
    joblib.dump(available_features, os.path.join(out_dir, 'model_features.joblib'))
    
    print(f"Saved model to {model_path}")
    
    metrics_path = os.path.join('outputs', 'reports', 'evaluation_metrics.csv')
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    pd.DataFrame({'Metric': ['RMSE', 'MAE', 'R2'], 'Value': [rmse, mae, r2]}).to_csv(metrics_path, index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/processed/collocated_training_table.parquet')
    parser.add_argument('--out', type=str, default='models')
    args = parser.parse_args()
    train_model(args.data, args.out)

if __name__ == '__main__':
    main()
