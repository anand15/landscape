while total_defined_area < TOTAL_AREA:
    st.subheader("Define a New Patch")
    patch_type = st.selectbox(
        "Select Patch Type:", 
        ["Forest", "Grassland", "Urban", "Water Body", "Wetland", "Agricultural", "Shrubland"], 
        key=f"patch_type_{len(defined_patches)}"
    )
    patch_area = st.number_input(
        f"Enter Area for {patch_type} (remaining area: {TOTAL_AREA - total_defined_area:.2f} sq m):",
        min_value=0.0,  # Ensure float
        max_value=float(TOTAL_AREA - total_defined_area),  # Convert to float
        step=0.1,  # Float step
        key=f"patch_area_{len(defined_patches)}"
    )
    shape_irregularity = st.slider(
        f"Set Shape Irregularity for {patch_type} (0: Perfect, 1: Highly Irregular):",
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        key=f"shape_irregularity_{len(defined_patches)}"
    )
    if st.button("Add Patch", key=f"add_patch_{len(defined_patches)}") and patch_area > 0:
        defined_patches.append({
            "Patch Type": patch_type,
            "Area": patch_area,
            "Shape Irregularity": shape_irregularity
        })
        total_defined_area += patch_area
        st.session_state["user_defined_patches"] = defined_patches
