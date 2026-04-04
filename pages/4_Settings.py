import streamlit as st
import json
import os
import data_store as ds
import ui_components as ui

ds.init_session_state()
ui.load_css()
st.set_page_config(page_title="GreenOps | ESG Analytics", page_icon="🌱", layout="wide")

st.markdown("<h1>System Configuration</h1>", unsafe_allow_html=True)
cs = st.session_state.company_settings

st.markdown("<h3>Enterprise Context</h3>", unsafe_allow_html=True)
st.info("These settings act as global defaults for the AI Insights engine and your Carbon Math.")

with st.form("company_info_form"):
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", value=cs.get("company_name", ""),help="*Please use English/Latin characters for PDF report compatibility.")
        industry = st.text_input("Industry Sector", value=cs.get("industry", ""))
        location = st.text_input("Primary Facility Location (Country)", value=cs.get("location", ""))
    with col2:
        contact_person = st.text_input("Responsible Data Officer", value=cs.get("contact_person", ""))
        email = st.text_input("Contact Email", value=cs.get("email", ""))
        phone = st.text_input("Contact Phone", value=cs.get("phone", ""))

    st.markdown("<h4>Target Export Markets</h4>", unsafe_allow_html=True)
    market_options = ["European Union (CBAM)", "United States", "United Arab Emirates (UAE)", "United Kingdom", "ASEAN (SE Asia)", "Japan", "Australia", "Africa", "South Asia (SAARC)"]
    saved_markets = cs.get("export_markets", [])
    export_markets = st.multiselect("Select applicable trade regions:", options=market_options, default=[m for m in saved_markets if m in market_options])

    st.markdown("<h4>Power Grid Configuration (Scope 2)</h4>", unsafe_allow_html=True)
    st.caption("Select your regional electricity grid to ensure accurate Scope 2 carbon math.")
    
    grid_options = ["India Grid", "US Grid Average", "EU Grid Average", "UK Grid", "China Grid", "Japan Grid", "Indonesia Grid", "Global Average Grid", "Custom / Manual Entry"]
    selected_grid = st.selectbox("Primary Electricity Grid", options=grid_options, index=grid_options.index(cs.get("grid_selection", "India Grid")) if cs.get("grid_selection", "India Grid") in grid_options else 0)
    
    # Custom Grid Logic
    custom_name = cs.get("custom_grid_name", "")
    custom_factor = cs.get("custom_grid_factor", 0.0)
    is_verified = cs.get("grid_verified", False)
    
    if selected_grid == "Custom / Manual Entry":
        st.warning("⚠️ You are bypassing standard IPCC/DEFRA emission factors. You must provide your contracted grid data.")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            custom_name = st.text_input("Custom Grid / PPA Name", value=custom_name, placeholder="e.g., GreenTech PPA 2026")
        with g_col2:
            custom_factor = st.number_input("Emission Factor (kgCO2e per kWh)", value=float(custom_factor), format="%.4f")
        
        is_verified = st.checkbox("✅ I self-verify that this emission factor is legally accurate and supported by official utility documentation.", value=is_verified)

    if st.form_submit_button("Save Global Configuration", type="primary"):
        if selected_grid == "Custom / Manual Entry" and not is_verified:
            st.error("You must check the 'Self-Verify' box to use a custom grid emission factor.")
        else:
            st.session_state.company_settings = {
                "company_name": company_name, "industry": industry, "location": location,
                "contact_person": contact_person, "email": email, "phone": phone,
                "export_markets": export_markets,
                "grid_selection": selected_grid,
                "custom_grid_name": custom_name,
                "custom_grid_factor": custom_factor,
                "grid_verified": is_verified
            }
            os.makedirs("data", exist_ok=True)
            with open("data/settings.json", "w") as fh:
                json.dump(st.session_state.company_settings, fh, indent=2)
            st.success("✅ Configuration saved.")