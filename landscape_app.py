import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import entropy

# Initialize App
st.title("Landscape Exploration App")
st.sidebar.title("Landscape Settings")

# Step 1: Total Area of Landscape
TOTAL_AREA = 100  # Total area in square meters
st.sidebar.write(f"Total Landscape Area: {TOTAL_AREA} square meters")

# Step 2: Number of Patch Types and Numbers
num_patch_types = st.sidebar.number_input("Enter the number of patch types:", min_value=1, max_value=10, value=3, step=1)
st.sidebar.write(f"You have selected {num_patch_types} patch types.")

# Step 3: Patch Type Selection
available_patch_types = ["Forest", "Grassland", "Urban", "Water Body", "Wetland", "Agricultural", "Shrubland"]
selected_patch_types = st.sidebar.multiselect(
    "Select patch types for the landscape:", available_patch_types, available_patch_types[:num_patch_types]
)

# Validate Patch Types Selection
if len(selected_patch_types) < num_patch_types:
    st.sidebar.warning("You selected fewer patch types than specified. Default types will be used.")
    selected_patch_types = available_patch_types[:num_patch_types]

# Step 4: Shape Adjustment Slider
shape_slider = st.sidebar.slider("Adjust Patch Shape: Perfect (0) to Irregular (1):", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
st.sidebar.write(f"Shape irregularity: {shape_slider}")

# Step 5: Calculate Landscape Metrics
st.header("Landscape Metrics")

# Generate random patch sizes and configurations
patch_areas = np.random.dirichlet(np.ones(len(selected_patch_types))) * TOTAL_AREA

metrics = {
    "Patch Type": selected_patch_types,
    "Area (sq meters)": patch_areas,
    "Proportional Abundance": patch_areas / TOTAL_AREA,
    "Shape Irregularity": [shape_slider] * len(selected_patch_types),
    "Edge-to-Core Ratio": [1 + shape_slider * np.random.random() for _ in selected_patch_types]
}
metrics_df = pd.DataFrame(metrics)

# Calculate Richness
richness = len(selected_patch_types)

# Calculate Evenness and Dominance
proportions = metrics_df["Proportional Abundance"]
evenness = entropy(proportions) / np.log(richness)
dominance = 1 - evenness

# Calculate Diversity (Shannon Diversity Index)
diversity = entropy(proportions)

# Display Metrics
st.write(metrics_df)

# Display Summary Metrics
st.write(f"**Richness:** {richness}")
st.write(f"**Evenness:** {evenness:.2f}")
st.write(f"**Dominance:** {dominance:.2f}")
st.write(f"**Diversity (Shannon Index):** {diversity:.2f}")

# Configuration Metrics
st.write("**Configuration Metrics:**")
patch_areas_list = metrics_df["Area (sq meters)"]

# Patch Area and Edge
radius_of_gyration = np.sqrt(patch_areas_list / np.pi)
edge_lengths = [2 * np.pi * r for r in radius_of_gyration]
metrics_df["Radius of Gyration"] = radius_of_gyration
metrics_df["Edge Length"] = edge_lengths

for i, patch_type in enumerate(selected_patch_types):
    st.write(f"- {patch_type}: Radius of Gyration: {radius_of_gyration[i]:.2f}, Edge Length: {edge_lengths[i]:.2f}")

# Patch Shape Complexity
shape_complexity = metrics_df["Edge Length"] / metrics_df["Area (sq meters)"]
metrics_df["Shape Complexity"] = shape_complexity

# Core Area
buffer_distance = 0.1 * radius_of_gyration
core_area = np.maximum(0, patch_areas_list - 2 * np.pi * buffer_distance**2)
metrics_df["Core Area"] = core_area

# Visualization
st.header("Patch Visualization")

# Generate Visualization
fig, ax = plt.subplots(figsize=(6, 6))

# Assign random positions to patches in a grid
x_positions = np.random.uniform(0, 10, len(selected_patch_types))
y_positions = np.random.uniform(0, 10, len(selected_patch_types))

for i, patch_type in enumerate(selected_patch_types):
    size = metrics_df["Area (sq meters)"][i] / TOTAL_AREA * 100
    ax.scatter(x_positions[i], y_positions[i], s=size * 20, label=f"{patch_type} ({size:.1f}%)")

ax.legend()
ax.set_title("Landscape Patch Visualization")
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")

st.pyplot(fig)

# Display Metrics Table
st.subheader("Complete Metrics Table")
st.dataframe(metrics_df)

# Additional Notes
st.sidebar.info("You can adjust the settings in the sidebar to customize the landscape visualization and metrics.")
