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
if "guided_mode" not in st.session_state:
    st.session_state["guided_mode"] = True
if "temporal_landscapes" not in st.session_state:
    st.session_state["temporal_landscapes"] = []  # To store landscapes over time
if "comparison_landscapes" not in st.session_state:
    st.session_state["comparison_landscapes"] = []  # For dynamic comparisons

# Step 2: Guided Mode
if st.session_state["guided_mode"]:
    st.sidebar.subheader("Guided Mode Enabled")
    st.sidebar.info("Guided mode provides step-by-step instructions to help you build and understand your landscape.")
    if st.sidebar.button("Disable Guided Mode"):
        st.session_state["guided_mode"] = False
else:
    st.sidebar.subheader("Guided Mode Disabled")
    if st.sidebar.button("Enable Guided Mode"):
        st.session_state["guided_mode"] = True

# Step 3: Landscape Building
st.header("Build Your Landscape")
defined_patches = st.session_state["user_defined_patches"]
total_defined_area = sum([p["Area"] for p in defined_patches])

if total_defined_area < TOTAL_AREA:
    if st.session_state["guided_mode"]:
        st.markdown("### Step 1: Select Patch Type")
        st.markdown("Choose the type of patch you want to add to the landscape. Each patch type represents a specific land cover or land use category.")
    
    with st.form("patch_form"):
        patch_type = st.selectbox(
            "Select Patch Type:", 
            ["Forest", "Grassland", "Urban", "Water Body", "Wetland", "Agricultural", "Shrubland"]
        )

        if st.session_state["guided_mode"]:
            st.markdown("### Step 2: Define Patch Area")
            st.markdown("Specify the size of the patch in square meters. The remaining area will be displayed to guide your choices.")

        patch_area = st.number_input(
            f"Enter Area for {patch_type} (remaining area: {TOTAL_AREA - total_defined_area:.2f} sq m):",
            min_value=0.0,
            max_value=float(TOTAL_AREA - total_defined_area),
            step=0.1,
        )

        if st.session_state["guided_mode"]:
            st.markdown("### Step 3: Set Shape Irregularity")
            st.markdown("Adjust the shape irregularity of the patch. A value of 0 represents a perfect shape (e.g., circle), while a value of 1 represents a highly irregular shape.")

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

# Step 4: Display Defined Patches
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

    if st.session_state["guided_mode"]:
        st.markdown("### Metrics Explanation")
        st.markdown("The following metrics provide insights into the composition and configuration of your landscape:")
        st.markdown("- **Richness**: The number of unique patch types.")
        st.markdown("- **Evenness**: How evenly distributed the patch types are.")
        st.markdown("- **Diversity**: A composite measure of richness and evenness.")
        st.markdown("- **Edge Length**: The total perimeter of patches.")
        st.markdown("- **Core Area**: The interior area unaffected by edge effects.")

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

    # Save Current Landscape for Comparison
    if st.button("Save Current Landscape for Comparison"):
        st.session_state["comparison_landscapes"].append(patches_df.copy())
        st.success("Landscape saved for comparison!")

    # Dynamic Comparison
    if len(st.session_state["comparison_landscapes"]) > 1:
        st.header("Dynamic Landscape Comparison")
        st.markdown("Compare metrics and visualizations of multiple saved landscapes side by side.")

        cols = st.columns(len(st.session_state["comparison_landscapes"]))
        for i, (col, landscape) in enumerate(zip(cols, st.session_state["comparison_landscapes"])):
            col.markdown(f"### Landscape {i + 1}")
            col.dataframe(landscape)

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
