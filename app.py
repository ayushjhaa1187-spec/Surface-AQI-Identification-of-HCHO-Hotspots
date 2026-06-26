import streamlit as st
import pandas as pd
import os
import subprocess
import sys
from PIL import Image

st.set_page_config(page_title="AQI & HCHO Hotspots", layout="wide")

st.title("?? Surface AQI & HCHO Hotspots Pipeline")
st.markdown("This dashboard visualizes the outputs of our remote sensing and **CNN-LSTM deep learning** pipeline over India.")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("??? Daily PM2.5 Surface Map")
    map_path = "outputs/maps/aqi_map_plot.png"
    if os.path.exists(map_path):
        img = Image.open(map_path)
        st.image(img, use_container_width=True)
    else:
        st.info("Map not found. Please run the pipeline.")

with col2:
    st.header("?? HCHO Hotspots (DBSCAN)")
    hotspots_path = "outputs/maps/hcho_hotspots.csv"
    if os.path.exists(hotspots_path):
        df = pd.read_csv(hotspots_path)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hotspots detected yet.")
        
    st.header("?? Transport Analysis")
    transport_path = "outputs/reports/transport_metrics.csv"
    if os.path.exists(transport_path):
        tdf = pd.read_csv(transport_path)
        st.dataframe(tdf, use_container_width=True)
        
st.divider()

st.header("?? Deep Learning Evaluation")
metrics_path = "outputs/reports/evaluation_metrics.csv"
if os.path.exists(metrics_path):
    metrics_df = pd.read_csv(metrics_path)
    cols = st.columns(len(metrics_df))
    for i, row in metrics_df.iterrows():
        cols[i].metric(label=row['Metric'], value=f"{row['Value']:.4f}")
else:
    st.info("No metrics available. Train the model first.")

st.divider()

st.header("?? Pipeline Controls")
if st.button("Run Full Pipeline"):
    with st.spinner("Running deep learning & GIS processing pipeline..."):
        scripts = [
            [sys.executable, "scripts/download_cpcb.py", "--mock", "tests/fixtures/cpcb_sample.csv"],
            [sys.executable, "scripts/prepare_satellite_data.py", "--mock", "tests/fixtures/s5p_sample.parquet"],
            [sys.executable, "scripts/prepare_meteorology.py", "--mock", "tests/fixtures/era5_sample.parquet"],
            [sys.executable, "scripts/download_firms.py", "--mock", "tests/fixtures/firms_sample.csv"],
            [sys.executable, "scripts/prepare_insat3d.py", "--mock", "tests/fixtures/insat3d_sample.parquet"],
            [sys.executable, "scripts/build_training_table.py"],
            [sys.executable, "scripts/train_model.py"],
            [sys.executable, "scripts/generate_aqi_maps.py"],
            [sys.executable, "scripts/plot_aqi_map.py"],
            [sys.executable, "scripts/detect_hcho_hotspots.py"],
            [sys.executable, "scripts/analyze_fire_hcho_transport.py"]
        ]
        
        for script_args in scripts:
            try:
                subprocess.run(script_args, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                st.error(f"Error running {script_args[1]}:\n{e.stderr}")
                st.stop()
            except FileNotFoundError:
                st.error(f"Could not find Python or the script {script_args[1]}")
                st.stop()
                
        st.success("Pipeline executed successfully! Refreshing data...")
        st.rerun()
