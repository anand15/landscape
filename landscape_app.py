import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Initialize App
st.title("Landscape Builder and Metrics Calculator")
st.sidebar.title("Landscape Settings")

# Step 1: Total Area of Landscape
TOTAL_AREA = 100  # Total area in square meters
st.sidebar.write(f"Total Landscape Area: {TOTAL_AREA} square meters")

# Step 2: Initialize Landscape Building
st.header("Build Your Landscape")

# Define patch attributes
available_patch_types = ["Forest", "Grassland", "Urban", "Water Body", "Wetland", "Agricultural", "Shrubland"]
user_defined_patches = []
total_defined_area = 0

# User Input: Add Patches
while total_defined_area < TOTAL_AREA:
    st.subheader("Define a New Patch")
    patch_type = st.selectbox("Select Patch Type:", available_patch_types, key=f"patch_type_{len(user_defined_patches)}")
    patch_area = st.number_input(
        f"Enter Area for {patch_type} (remaining area: {TOTAL_AREA - total_defined_area:.2f} sq m):",
        min_value=0.0,
        max_value=TOTAL_AREA - total_defined_area,
        step=0.1,
        key=f"patch_area_{len(user_defined_patches)}"
    )
    shape_irregularity = st.slider(
        f"Set Shape Irregularity for {patch_type} (0: Perfect, 1: Highly Irregular):",
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        key=f"shape_irregularity_{len(user_defined_patches)}"
    )

    # Add Patch to Landscape
    if st.button("Add Patch", key=f"add_patch_{len(user_defined_patches)}") and patch_area > 0:
        user_defined_patches.append({
            "Patch Type": patch_type,
            "Area": patch_area,
            "Shape Irregularity": shape_irregularity
        })
        total_defined_area += patch_area

# Display Defined Patches
if user_defined_patches:
    st.subheader("Defined Patches")
    patches_df = pd.DataFrame(user_defined_patches)
    st.write(patches_df)

# Step 3: Calculate Metrics
if total_defined_area > 0:
    st.header("Landscape Metrics")

    # Proportional Abundance
    patches_df["Proportional Abundance"] = patches_df["Area"] / total_defined_area

    # Richness
    richness = patches_df["Patch Type"].nunique()

    # Evenness and Dominance
    proportions = patches_df["Proportional Abundance"]
    evenness = entropy(proportions) / np.log(richness) if richness > 1 else 1
    dominance = 1 - evenness

    # Diversity (Shannon Index)
    diversity = entropy(proportions)

    # Patch Area and Edge
    radius_of_gyration = np.sqrt(patches_df["Area"] / np.pi)
    edge_lengths = 2 * np.pi * radius_of_gyration
    patches_df["Radius of Gyration"] = radius_of_gyration
    patches_df["Edge Length"] = edge_lengths

    # Shape Complexity
    patches_df["Shape Complexity"] = patches_df["Edge Length"] / patches_df["Area"]

    # Core Area
    buffer_distance = 0.1 * radius_of_gyration
    core_area = np.maximum(0, patches_df["Area"] - 2 * np.pi * buffer_distance**2)
    patches_df["Core Area"] = core_area

    # Display Metrics
    st.write(patches_df)
    st.write(f"**Richness:** {richness}")
    st.write(f"**Evenness:** {evenness:.2f}")
    st.write(f"**Dominance:** {dominance:.2f}")
    st.write(f"**Diversity (Shannon Index):** {diversity:.2f}")

# Step 4: Visualization
if total_defined_area > 0:
    st.header("Landscape Visualization")

    # Create Visualization Box
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title("Landscape Visualization (100 sq m)")
    ax.set_xlabel("X Axis (m)")
    ax.set_ylabel("Y Axis (m)")

    # Place Patches
    current_x = 0
    current_y = 0
    for index, patch in patches_df.iterrows():
        width = np.sqrt(patch["Area"] / TOTAL_AREA) * 10
        height = width * (1 + patch["Shape Irregularity"] * np.random.random())
        rect = plt.Rectangle((current_x, current_y), width, height, label=f"{patch['Patch Type']} ({patch['Area']} sq m)")
        ax.add_patch(rect)
        current_x += width
        if current_x >= 10:
            current_x = 0
            current_y += height

    ax.legend()
    st.pyplot(fig)

# Additional Notes
st.sidebar.info("You can define patches until the total area matches or is less than 100 sq m. Metrics and visualization will update accordingly.")
