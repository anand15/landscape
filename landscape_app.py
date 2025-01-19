import streamlit as st
import matplotlib.pyplot as plt
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

    st.write(patches_df)
    st.write(f"**Richness:** {richness}")
    st.write(f"**Evenness:** {evenness:.2f}")
    st.write(f"**Dominance:** {dominance:.2f}")
    st.write(f"**Diversity (Shannon Index):** {diversity:.2f}")

  # Visualization
    st.header("Landscape Visualization")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 20)  # Increased visualization area
    ax.set_ylim(0, 20)
    ax.set_title("Landscape Visualization")
    ax.set_xlabel("X Axis (arbitrary units)")
    ax.set_ylabel("Y Axis (arbitrary units)")

    # Define Colors for Each Patch Type
    colors = {
        "Forest": "green",
        "Grassland": "yellow",
        "Urban": "gray",
        "Water Body": "blue",
        "Wetland": "brown",
        "Agricultural": "orange",
        "Shrubland": "purple"
    }

    # Place Patches Randomly Without Overlap
    placed_patches = []

    for _, patch in patches_df.iterrows():
        width = np.sqrt(patch["Area"] / TOTAL_AREA) * 10
        height = width * (1 + patch["Shape Irregularity"] * 0.5)

        # Ensure no overlap
        while True:
            x_position = random.uniform(0 + width / 2, 20 - width / 2)
            y_position = random.uniform(0 + height / 2, 20 - height / 2)
            new_patch = plt.Rectangle(
                (x_position - width / 2, y_position - height / 2), 
                width, 
                height
            )
            if not any(new_patch.get_bbox().overlaps(existing.get_bbox()) for existing in placed_patches):
                break

        rect = plt.Rectangle(
            (x_position - width / 2, y_position - height / 2), 
            width, 
            height, 
            color=colors[patch["Patch Type"]], 
            alpha=0.7, 
            label=f"{patch['Patch Type']} ({patch['Area']} sq m)"
        )
        ax.add_patch(rect)
        placed_patches.append(rect)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    st.pyplot(fig)

# Additional Notes
st.sidebar.info("You can define patches without constraint to a 100 sq m visualization area. Metrics and visualization will update accordingly. Use the 'Remove Selected Patch' option to adjust patches.")
