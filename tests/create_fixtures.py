import os
import pandas as pd

def create_fixtures():
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    os.makedirs(fixtures_dir, exist_ok=True)
    
    # 1. CPCB CSV
    cpcb_df = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02'],
        'station_id': ['ST01', 'ST02', 'ST01', 'ST02'],
        'latitude': [28.6, 19.0, 28.6, 19.0],
        'longitude': [77.2, 72.8, 77.2, 72.8],
        'PM2.5': [150.0, 80.5, 145.0, 85.0],
        'PM10': [250.0, 150.0, 240.0, 160.0],
        'NO2': [40.0, 35.0, 42.0, 33.0],
    })
    cpcb_df.to_csv(os.path.join(fixtures_dir, 'cpcb_sample.csv'), index=False)
    
    # 2. Sentinel-5P Parquet
    s5p_df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-02']),
        'latitude': [28.6, 19.0, 28.6],
        'longitude': [77.2, 72.8, 77.2],
        'HCHO': [0.0001, 0.0002, 0.00015],
        'NO2_column': [0.001, 0.002, 0.0012],
    })
    s5p_df.to_parquet(os.path.join(fixtures_dir, 's5p_sample.parquet'), index=False)
    
    # 3. FIRMS CSV
    firms_df = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02'],
        'latitude': [28.5, 28.7],
        'longitude': [77.1, 77.3],
        'confidence': ['nominal', 'high'],
        'frp': [12.5, 45.0],
    })
    firms_df.to_csv(os.path.join(fixtures_dir, 'firms_sample.csv'), index=False)
    
    # 4. ERA5 Parquet
    era5_df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-01']),
        'latitude': [28.6, 19.0],
        'longitude': [77.2, 72.8],
        'u10': [1.5, -0.5],
        'v10': [0.5, 2.0],
        't2m': [290.0, 300.0],
        'blh': [1200.0, 1500.0],
    })
    era5_df.to_parquet(os.path.join(fixtures_dir, 'era5_sample.parquet'), index=False)
    
    
    # 5. INSAT-3D Parquet
    insat_df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-02']),
        'latitude': [28.6, 19.0, 28.6],
        'longitude': [77.2, 72.8, 77.2],
        'AOD': [0.5, 0.3, 0.6],
    })
    insat_df.to_parquet(os.path.join(fixtures_dir, 'insat3d_sample.parquet'), index=False)
    print('Sample fixtures created successfully in tests/fixtures/')

if __name__ == '__main__':
    create_fixtures()
