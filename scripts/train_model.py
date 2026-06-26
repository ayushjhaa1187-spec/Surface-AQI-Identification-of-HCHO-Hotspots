import argparse
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

def train_baseline_model(data_path, models_dir):
    print(f"Loading training data from {data_path}...")
    if not os.path.exists(data_path):
        print(f"Data file {data_path} not found.")
        return
    df = pd.read_parquet(data_path)
    
    features = ['latitude', 'longitude', 'HCHO', 'NO2_column', 'u10', 'v10', 't2m', 'blh']
    target = 'PM2.5'
    
    features = [f for f in features if f in df.columns]
    
    if target not in df.columns or len(features) == 0:
        print("Required columns missing for training.")
        return
        
    X = df[features]
    y = df[target]
    
    # Fill any remaining NaNs
    X = X.fillna(0)
    
    # Handle small datasets gracefully
    if len(df) < 5:
        X_train, X_test, y_train, y_test = X, X, y, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training RandomForestRegressor baseline...")
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    print(f"Validation MSE: {mse:.4f}")
    
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'rf_baseline_model.joblib')
    joblib.dump(model, model_path)
    print(f"Saved baseline model to {model_path}")

def main():
    parser = argparse.ArgumentParser(description='Train baseline ML model.')
    parser.add_argument('--data', type=str, default='data/processed/collocated_training_table.parquet')
    parser.add_argument('--out', type=str, default='models')
    args = parser.parse_args()
    train_baseline_model(args.data, args.out)

if __name__ == '__main__':
    main()
