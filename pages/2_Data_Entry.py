import streamlit as st
import pandas as pd
import emission_factors as ef
import data_store as ds
import ui_components as ui  

ds.init_session_state()
ui.load_css()
st.set_page_config(page_title="GreenOps | ESG Analytics", page_icon="🌱", layout="wide")

st.markdown("<h1>Add New Sustainability Entry</h1>", unsafe_allow_html=True)

# Inherit context from Settings; no more local region overrides
cs = st.session_state.get("company_settings", {})
defaults = {
    "business_unit": cs.get("company_name", "Main Office"),
    "country": cs.get("location", "Not Specified"),
    "facility": cs.get("location", "HQ"),
    "responsible_person": cs.get("contact_person", "Admin"),
}

if defaults["country"] == "Not Specified":
    st.warning("⚠️ Warning: Your operating region is not set. Go to **Settings** to configure your enterprise profile so emission factors are regionally accurate.")

tabs = st.tabs(["⚡ Energy", "🗑️ Waste", "💨 Direct Carbon / Travel", "📂 CSV Upload"])

# Helper to fetch activities from the physics engine dynamically
def get_activities(category):
    return list(ef.EMISSION_FACTORS.get(category, {}).keys())

# ── Tab: Energy ──
with tabs[0]:
    st.markdown("### Log Energy Consumption")
    e_date = st.date_input("Date", key="e_date")
    
    e_type = st.radio("Energy Type", ["Purchased Electricity (Scope 2)", "Stationary Combustion / Generators (Scope 1)"])
    e_cat = "Electricity" if "Electricity" in e_type else "Stationary Combustion"
    
    if e_cat == "Electricity":
        # Pull grid from settings
        saved_grid = cs.get("grid_selection", "India Grid")
        
        # User still needs to select if they used Grid, Solar, or Wind today
        power_source = st.selectbox("Power Source", ["Grid Electricity", "Solar Power", "Wind Power"])
        
        if power_source == "Grid Electricity":
            if saved_grid == "Custom / Manual Entry":
                e_activity = cs.get("custom_grid_name", "Custom Grid")
                e_unit = "kWh"
                e_factor = cs.get("custom_grid_factor", 0.0)
            else:
                e_activity = saved_grid
                e_data = ef.get_emission_factor(e_cat, e_activity)
                e_unit = e_data["unit"] if e_data else "kWh"
                e_factor = e_data["factor"] if e_data else 0.0
        else:
            # Solar or Wind
            e_activity = power_source
            e_data = ef.get_emission_factor(e_cat, e_activity)
            e_unit = e_data["unit"] if e_data else "kWh"
            e_factor = e_data["factor"] if e_data else 0.0
            
    else:
        # Stationary Combustion (Diesel, Gas, etc.)
        e_activity = st.selectbox("Fuel Source", get_activities(e_cat))
        e_data = ef.get_emission_factor(e_cat, e_activity)
        e_unit = e_data["unit"] if e_data else "unit"
        e_factor = e_data["factor"] if e_data else 0.0

    e_qty = st.number_input(f"Quantity ({e_unit})", min_value=0.0, format="%.2f", key="e_qty")
    
    if e_cat == "Electricity" and power_source == "Grid Electricity" and saved_grid == "Custom / Manual Entry":
        st.info(f"**Custom Configured Factor:** {e_factor} kgCO2e / {e_unit}")
    else:
        st.info(f"**GHG Protocol Factor:** {e_factor} kgCO2e / {e_unit}")

    if st.button("Log Energy Data", type="primary"):
        if e_qty <= 0:
            st.error("❌ Quantity must be greater than 0. Ghost entries are not allowed.")
        else:
            if ds.add_emission_entry(e_date, defaults["business_unit"], "Energy Consumption", e_cat, e_activity, defaults["country"], defaults["facility"], defaults["responsible_person"], e_qty, e_unit, e_factor):
                st.success(f"✅ Logged {e_qty} {e_unit} of {e_activity}!")

# ── Tab: Waste ──
with tabs[1]:
    st.markdown("### Log Waste Management (Scope 3)")
    w_date = st.date_input("Date", key="w_date")
    
    w_cat = "Waste"
    w_activity = st.selectbox("Disposal Method & Material", get_activities(w_cat))
    
    w_data = ef.get_emission_factor(w_cat, w_activity)
    w_unit = w_data["unit"] if w_data else "kg"
    w_factor = w_data["factor"] if w_data else 0.0

    w_qty = st.number_input(f"Quantity ({w_unit})", min_value=0.0, format="%.2f", key="w_qty")
    st.info(f"**GHG Protocol Factor:** {w_factor} kgCO2e / {w_unit}")

    if st.button("Log Waste Data", type="primary"):
        if w_qty <= 0:
            st.error("❌ Quantity must be greater than 0. Ghost entries are not allowed.")
        else:
            if ds.add_emission_entry(w_date, defaults["business_unit"], "Waste Management", w_cat, w_activity, defaults["country"], defaults["facility"], defaults["responsible_person"], w_qty, w_unit, w_factor):
                st.success(f"Logged {w_qty} {w_unit} of {w_activity} waste!")

# ── Tab: Carbon & Travel ──
with tabs[2]:
    st.markdown("### Log Direct Emissions & Travel")
    c_date = st.date_input("Date", key="c_date")
    
    c_cat = st.selectbox("Emission Category", [
        "Mobile Combustion", 
        "Refrigerants", 
        "Business Travel", 
        "Employee Commuting",
        "Water",
        "Purchased Goods & Services"
    ])
    
    c_activity = st.selectbox("Specific Activity", get_activities(c_cat))
    
    c_data = ef.get_emission_factor(c_cat, c_activity)
    c_unit = c_data["unit"] if c_data else "unit"
    c_factor = c_data["factor"] if c_data else 0.0

    c_qty = st.number_input(f"Quantity ({c_unit})", min_value=0.0, format="%.2f", key="c_qty")
    st.info(f"**GHG Protocol Factor:** {c_factor} kgCO2e / {c_unit}")


    if st.button("Log Carbon Data", type="primary"):
        if c_qty <= 0:
            st.error("❌ Quantity must be greater than 0. Ghost entries are not allowed.")
        else:
            if ds.add_emission_entry(c_date, defaults["business_unit"], "Carbon Emissions", c_cat, c_activity, defaults["country"], defaults["facility"], defaults["responsible_person"], c_qty, c_unit, c_factor):
                st.success(f"Logged {c_qty} {c_unit} for {c_activity}!")

# ── Tab: CSV Upload ──
with tabs[3]:
    st.markdown("### Bulk Data Upload")
    st.warning("Ensure your CSV contains columns matching the exact names generated by the system. Required: `date, scope, category, activity, quantity, unit, emission_factor`")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file and st.button("Process CSV", type="primary"):
        with st.spinner("Hashing rows and verifying duplicates..."):
            ds.process_csv(uploaded_file)

# ── Data Viewer & Safe Delete ──
st.divider()
st.markdown("### 🗄️ Manage Database Entries")

if len(st.session_state.emissions_data) == 0:
    st.info("Database is empty. Add entries above to begin.")
else:
    # 1. Create a working copy and insert a temporary checkbox column
    edit_df = st.session_state.emissions_data.copy()
    edit_df.insert(0, "Select for Deletion", False)
    
    st.info("💡 **How to delete:** Tick the boxes in the 'Select for Deletion' column, then click the red confirmation button.")
    
    # 2. Render the interactive editor
    # We disable editing on all original columns to prevent accidental data corruption
    edited_df = st.data_editor(
        edit_df,
        hide_index=True,
        use_container_width=True,
        disabled=st.session_state.emissions_data.columns.tolist(), # Locks actual data
        column_config={
            "Select for Deletion": st.column_config.CheckboxColumn(required=True),
            "id": None # Hides the ugly UUID string from the user interface
        }
    )
    
    # 3. Process Deletions safely via UUID mapping
    rows_to_delete = edited_df[edited_df["Select for Deletion"] == True]
    
    if not rows_to_delete.empty:
        st.error(f"⚠️ You have selected {len(rows_to_delete)} row(s) for permanent deletion. This cannot be undone.")
        
        if st.button("🗑️ Confirm Deletion", type="primary", use_container_width=True):
            # Keep only the rows where the UUID is NOT in the deletion list
            target_ids = rows_to_delete["id"].tolist()
            remaining_data = st.session_state.emissions_data[~st.session_state.emissions_data["id"].isin(target_ids)]
            
            # Save the pristine remaining data back to state and disk
            st.session_state.emissions_data = remaining_data.reset_index(drop=True)
            
            import data_store as ds # Ensure this matches your new module name
            ds.save_emissions_data()
            
            st.success(f"✅ Successfully deleted {len(rows_to_delete)} row(s).")
            st.rerun()

# ... [Existing UUID deletion logic] ...
    
st.divider()
with st.expander("🚨 Danger Zone (System Administration)"):
    st.warning("The actions below bypass individual row selection and are strictly irreversible. Use only in case of catastrophic data corruption or testing resets.")
    
    if st.button("💀 Purge Entire Database", type="primary", use_container_width=True):
        # Re-initialize an empty DataFrame retaining the exact schema
        st.session_state.emissions_data = pd.DataFrame(columns=st.session_state.emissions_data.columns)
        
        import data_store as ds 
        ds.save_emissions_data()
        
        st.success("Database has been completely purged.")
        st.rerun()