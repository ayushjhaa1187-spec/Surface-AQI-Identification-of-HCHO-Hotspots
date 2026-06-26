import streamlit as st
import pandas as pd
import os
import subprocess
from PIL import Image

st.set_page_config(page_title="AQI & HCHO Hotspots", layout="wide")

st.title("🌍 Surface AQI & HCHO Hotspots Pipeline")
st.markdown("This dashboard visualizes the outputs of our remote sensing and deep learning pipeline over India.")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("🗺️ Daily PM2.5 Surface Map")
    map_path = "outputs/maps/aqi_map_plot.png"
    if os.path.exists(map_path):
        img = Image.open(map_path)
        st.image(img, use_container_width=True)
    else:
        st.info("Map not found. Please run the pipeline.")

with col2:
    st.header("🔥 HCHO Hotspots")
    hotspots_path = "outputs/maps/hcho_hotspots.csv"
    if os.path.exists(hotspots_path):
        df = pd.read_csv(hotspots_path)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hotspots detected yet.")
        
st.divider()

st.header("⚙️ Pipeline Controls")
if st.button("Run Full Pipeline"):
    with st.spinner("Running full processing pipeline..."):
        scripts = [
            "scripts/download_cpcb.py",
            "scripts/prepare_satellite_data.py",
            "scripts/prepare_meteorology.py",
            "scripts/download_firms.py",
            "scripts/build_training_table.py",
            "scripts/train_model.py",
            "scripts/generate_aqi_maps.py",
            "scripts/plot_aqi_map.py",
            "scripts/detect_hcho_hotspots.py",
            "scripts/analyze_fire_hcho_transport.py"
        ]
        
        for script in scripts:
            try:
                subprocess.run(["python", script], check=True)
            except subprocess.CalledProcessError as e:
                st.error(f"Error running {script}")
                st.stop()
        st.success("Pipeline executed successfully! Refreshing data...")
        st.rerun()
