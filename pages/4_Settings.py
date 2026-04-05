import streamlit as st
import json
import os
import data_store as ds
import ui_components as ui

st.set_page_config(page_title="Settings - GreenOps", page_icon="🌱", layout="wide")
ds.init_session_state()
ui.load_css()

ui.page_header(
    eyebrow="Configuration",
    title="Settings",
    subtitle="Enterprise profile, grid configuration, and export market selection. Used as defaults by all AI agents.",
)

cs = st.session_state.company_settings

# ── Company Profile ────────────────────────────────────────────────────────────
ui.sep("Enterprise Profile")

with st.form("company_info_form"):

    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input(
            "Company Name",
            value=cs.get("company_name", ""),
            help="Use English/Latin characters for PDF report compatibility.",
        )
        industry = st.text_input("Industry Sector", value=cs.get("industry", ""))
        location = st.text_input("Primary Facility Location (Country)", value=cs.get("location", ""))
    with col2:
        contact_person = st.text_input("Responsible Data Officer", value=cs.get("contact_person", ""))
        email  = st.text_input("Contact Email", value=cs.get("email", ""))
        phone  = st.text_input("Contact Phone", value=cs.get("phone", ""))

    # ── Export Markets ─────────────────────────────────────────────────────────
    ui.sep("Target Export Markets", small=True)

    market_options = [
        "European Union (CBAM)", "United States",
        "United Arab Emirates (UAE)", "United Kingdom",
        "ASEAN (SE Asia)", "Japan", "Australia",
        "Africa", "South Asia (SAARC)",
    ]
    saved_markets = cs.get("export_markets", [])
    export_markets = st.multiselect(
        "Select applicable trade regions",
        options=market_options,
        default=[m for m in saved_markets if m in market_options],
    )

    # ── Grid Configuration ─────────────────────────────────────────────────────
    ui.sep("Scope 2 — Electricity Grid", small=True)

    st.caption("Select your regional grid for accurate Scope 2 carbon math.")

    grid_options = [
        "India Grid", "US Grid Average", "EU Grid Average", "UK Grid",
        "China Grid", "Japan Grid", "Indonesia Grid", "Global Average Grid",
        "Custom / Manual Entry",
    ]
    selected_grid = st.selectbox(
        "Primary Electricity Grid",
        options=grid_options,
        index=grid_options.index(cs.get("grid_selection", "India Grid"))
              if cs.get("grid_selection", "India Grid") in grid_options else 0,
    )

    # Preserve existing custom values when not in custom mode
    existing_custom_name   = cs.get("custom_grid_name", "")
    existing_custom_factor = cs.get("custom_grid_factor", 0.0)
    existing_verified      = cs.get("grid_verified", False)

    custom_name   = existing_custom_name
    custom_factor = existing_custom_factor
    is_verified   = existing_verified

    if selected_grid == "Custom / Manual Entry":
        st.warning("You are bypassing standard IPCC/DEFRA emission factors. Provide your contracted grid data.")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            custom_name = st.text_input(
                "Custom Grid / PPA Name",
                value=existing_custom_name,
                placeholder="e.g. GreenTech PPA 2026",
            )
        with g_col2:
            custom_factor = st.number_input(
                "Emission Factor (kgCO₂e per kWh)",
                value=float(existing_custom_factor),
                format="%.4f",
            )
        is_verified = st.checkbox(
            "I self-verify this emission factor is legally accurate and supported by official utility documentation.",
            value=existing_verified,
        )

    submitted = st.form_submit_button("Save Configuration", type="primary")

    if submitted:
        if selected_grid == "Custom / Manual Entry" and not is_verified:
            st.error("Check the self-verify box to use a custom emission factor.")
        else:
            st.session_state.company_settings = {
                "company_name":      company_name,
                "industry":          industry,
                "location":          location,
                "contact_person":    contact_person,
                "email":             email,
                "phone":             phone,
                "export_markets":    export_markets,
                "grid_selection":    selected_grid,
                "custom_grid_name":  custom_name,
                "custom_grid_factor": custom_factor,
                "grid_verified":     is_verified,
            }
            os.makedirs("data", exist_ok=True)
            with open("data/settings.json", "w") as fh:
                json.dump(st.session_state.company_settings, fh, indent=2)
            st.success("Configuration saved.")