import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Sample Data for Visualization
def generate_sample_data():
    data = {
        'Patch Type': ['Forest', 'Grassland', 'Urban', 'Water Body'],
        'Average Size (ha)': [120, 80, 50, 30],
        'Edge-to-Core Ratio': [1.2, 1.5, 2.0, 0.8],
        'Number of Patches': [20, 35, 15, 10]
    }
    return pd.DataFrame(data)

# Initialize Data
data = generate_sample_data()

# Streamlit App
st.title("Landscape Exploration App")
st.sidebar.title("Select Metrics")

# Sidebar for Selecting Metrics
selected_patch_type = st.sidebar.selectbox("Choose Patch Type", data['Patch Type'].unique())

metrics = ["Average Size (ha)", "Edge-to-Core Ratio", "Number of Patches"]
selected_metric = st.sidebar.selectbox("Choose Metric", metrics)

# Filter Data Based on Selection
filtered_data = data[data['Patch Type'] == selected_patch_type]

# Main Display
st.header(f"Visualizing Metrics for {selected_patch_type}")

# Display Data
st.write(f"**{selected_patch_type} Metrics:**")
st.write(filtered_data)

# Visualization
if selected_metric:
    st.subheader(f"Visualization: {selected_metric} for {selected_patch_type}")

    # Create Bar Chart
    fig, ax = plt.subplots()
    ax.bar(selected_patch_type, filtered_data[selected_metric].values, color='green')
    ax.set_ylabel(selected_metric)
    ax.set_title(f"{selected_metric} of {selected_patch_type}")

    st.pyplot(fig)

# Additional Functionality: Map or Metrics Exploration
st.sidebar.title("Advanced Options")
if st.sidebar.checkbox("Show All Patch Types Data"):
    st.subheader("Complete Patch Data")
    st.dataframe(data)

if st.sidebar.checkbox("Show Distribution of Metrics"):
    st.subheader("Distribution of Metrics")

    # Create Subplots for Each Metric
    fig, axs = plt.subplots(1, len(metrics), figsize=(15, 5))
    for i, metric in enumerate(metrics):
        axs[i].bar(data['Patch Type'], data[metric], color='blue')
        axs[i].set_title(metric)
        axs[i].set_xticklabels(data['Patch Type'], rotation=45)

    st.pyplot(fig)

# Note: Extend with geospatial features using libraries like Folium for map-based visualization or more dynamic user interactions.
