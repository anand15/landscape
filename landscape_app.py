import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import pandas as pd
import numpy as np
from scipy.stats import entropy
import random

# Initialize App
st.title("Landscape Builder and Metrics Calculator")
st.sidebar.title("Landscape Settings")

# Step 1: Total Area of Landscape
TOTAL_AREA = 100  # Total area in square meters
st.sidebar.write(f"Total Landscape Area: {TOTAL_AREA} square meters")

# Initialize session state for patches
if "user_defined_patches" not in st.session_state:
    st.session_state["user_defined_patches"] = []

# Step 2: Landscape Building
st.header("Build Your Landscape")
defined_patches = st.session_state["user_defined_patches"]
total_defined_area = sum([p["Area"] for p in defined_patches])

if total_defined_area < TOTAL_AREA:
    with st.form("patch_form"):
        patch_type = st.selectbox(
            "Select Patch Type:", 
            ["Forest", "Grassland", "Urban", "Water Body", "Wetland", "Agricultural", "Shrubland"]
        )
        patch_area = st.number_input(
            f"Enter Area for {patch_type} (remaining area: {TOTAL_AREA - total_defined_area:.2f} sq m):",
            min_value=0.0,
            max_value=float(TOTAL_AREA - total_defined_area),
            step=0.1,
        )
        shape_irregularity = st.slider(
            f"Set Shape Irregularity for {patch_type} (0: Perfect, 1: Highly Irregular):",
            min_value=0.0,
            max_value=1.0,
            step=0.1
        )
        add_patch = st.form_submit_button("Add Patch")

    if add_patch and patch_area > 0:
        defined_patches.append({
            "Patch Type": patch_type,
            "Area": patch_area,
            "Shape Irregularity": shape_irregularity
        })
        st.session_state["user_defined_patches"] = defined_patches
else:
    st.warning("Total area defined has reached or exceeded the 100 sq m limit.")

# Step 3: Display Defined Patches
if defined_patches:
    st.subheader("Defined Patches")
    patches_df = pd.DataFrame(defined_patches)
    st.write(patches_df)

    # Option to remove patches
    remove_patch_index = st.selectbox("Select a patch to remove:", options=range(len(defined_patches)), format_func=lambda x: f"{defined_patches[x]['Patch Type']} ({defined_patches[x]['Area']} sq m)")
    if st.button("Remove Selected Patch"):
        defined_patches.pop(remove_patch_index)
        st.session_state["user_defined_patches"] = defined_patches

    # Metrics Calculation
    st.header("Landscape Metrics")

    total_patches = len(defined_patches)
    total_patch_area = sum(patches_df["Area"])
    patches_df["Proportional Abundance"] = patches_df["Area"] / TOTAL_AREA
    richness = patches_df["Patch Type"].nunique()
    proportions = patches_df["Proportional Abundance"]
    evenness = entropy(proportions) / np.log(richness) if richness > 1 else 1
    dominance = 1 - evenness
    diversity = entropy(proportions)
    radius_of_gyration = np.sqrt(patches_df["Area"] / np.pi)
    edge_lengths = 2 * np.pi * radius_of_gyration
    patches_df["Radius of Gyration"] = radius_of_gyration
    patches_df["Edge Length"] = edge_lengths
    patches_df["Shape Complexity"] = patches_df["Edge Length"] / patches_df["Area"]
    buffer_distance = 0.1 * radius_of_gyration
    core_area = np.maximum(0, patches_df["Area"] - 2 * np.pi * buffer_distance**2)
    patches_df["Core Area"] = core_area

    st.write(f"**Total Number of Patches:** {total_patches}")
    st.write(f"**Total Area of Patches:** {total_patch_area:.2f} sq m")
    st.write(patches_df)
    st.write(f"**Richness:** {richness}")
    st.write(f"**Evenness:** {evenness:.2f}")
    st.write(f"**Dominance:** {dominance:.2f}")
    st.write(f"**Diversity (Shannon Index):** {diversity:.2f}")
    st.write(f"**Edge Lengths:** {edge_lengths.tolist()}")
    st.write(f"**Shape Complexities:** {patches_df['Shape Complexity'].tolist()}")
    st.write(f"**Core Areas:** {patches_df['Core Area'].tolist()}")

    # Visualization
    st.header("Landscape Visualization")

    def generate_irregular_shape(x_center, y_center, base_size, irregularity):
        angles = np.linspace(0, 2 * np.pi, 20)  # Divide shape into 20 segments
        radii = base_size * (1 + irregularity * (np.random.random(len(angles)) - 0.5))
        x_points = x_center + radii * np.cos(angles)
        y_points = y_center + radii * np.sin(angles)
        vertices = np.column_stack([x_points, y_points])
        vertices = np.vstack([vertices, vertices[0]])  # Close the shape
        codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
        return Path(vertices, codes)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 20)  # Increased visualization area
    ax.set_ylim(0, 20)
    ax.set_title("Landscape Visualization")
    ax.set_xlabel("X Axis (arbitrary units)")
    ax.set_ylabel("Y Axis (arbitrary units)")

    colors = {
        "Forest": "green",
        "Grassland": "yellow",
        "Urban": "gray",
        "Water Body": "blue",
        "Wetland": "brown",
        "Agricultural": "orange",
        "Shrubland": "purple"
    }

    placed_patches = []

    for _, patch in patches_df.iterrows():
        base_size = np.sqrt(patch["Area"] / TOTAL_AREA) * 10
        irregularity = patch["Shape Irregularity"]
        while True:
            x_center = random.uniform(base_size, 20 - base_size)
            y_center = random.uniform(base_size, 20 - base_size)
            path = generate_irregular_shape(x_center, y_center, base_size, irregularity)
            patch_shape = PathPatch(path, facecolor=colors[patch["Patch Type"]], alpha=0.7)
            if not any(patch_shape.get_path().intersects_path(existing.get_path()) for existing in placed_patches):
                break
        ax.add_patch(patch_shape)
        placed_patches.append(patch_shape)

    st.pyplot(fig)

# Additional Notes
st.sidebar.info("You can define patches without constraint to a 100 sq m visualization area. Metrics and visualization will update accordingly. Use the 'Remove Selected Patch' option to adjust patches.")
