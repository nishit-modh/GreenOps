import streamlit as st
import pandas as pd
import emission_factors as ef
import data_store as ds
import ui_components as ui

st.set_page_config(page_title="Data Entry - GreenOps", page_icon="🌱", layout="wide")
ds.init_session_state()
ui.load_css()

ui.page_header(
    eyebrow="Operations",
    title="Data Entry",
    subtitle="Log Scope 1, 2, and 3 emission activities manually, or bulk-import via CSV.",
)

cs = st.session_state.get("company_settings", {})
defaults = {
    "business_unit":    cs.get("company_name", "Main Office"),
    "country":          cs.get("location", "Not Specified"),
    "facility":         cs.get("location", "HQ"),
    "responsible_person": cs.get("contact_person", "Admin"),
}

if defaults["country"] == "Not Specified":
    st.warning("Operating region not set. Configure your profile in **Settings** for regionally accurate emission factors.")


def get_activities(category):
    return list(ef.EMISSION_FACTORS.get(category, {}).keys())


# ── Entry Tabs ─────────────────────────────────────────────────────────────────
ui.sep("Log New Entry")

tabs = st.tabs(["Energy", "Waste", "Direct Carbon & Travel", "CSV Upload"])

# Energy
with tabs[0]:
    e_date = st.date_input("Date", key="e_date")
    e_type = st.radio("Energy Type", ["Purchased Electricity (Scope 2)", "Stationary Combustion / Generators (Scope 1)"])
    e_cat  = "Electricity" if "Electricity" in e_type else "Stationary Combustion"

    if e_cat == "Electricity":
        saved_grid  = cs.get("grid_selection", "India Grid")
        power_source = st.selectbox("Power Source", ["Grid Electricity", "Solar Power", "Wind Power"])
        if power_source == "Grid Electricity":
            if saved_grid == "Custom / Manual Entry":
                e_activity = cs.get("custom_grid_name", "Custom Grid")
                e_unit     = "kWh"
                e_factor   = cs.get("custom_grid_factor", 0.0)
            else:
                e_activity = saved_grid
                e_data     = ef.get_emission_factor(e_cat, e_activity)
                e_unit     = e_data["unit"] if e_data else "kWh"
                e_factor   = e_data["factor"] if e_data else 0.0
        else:
            e_activity = power_source
            e_data     = ef.get_emission_factor(e_cat, e_activity)
            e_unit     = e_data["unit"] if e_data else "kWh"
            e_factor   = e_data["factor"] if e_data else 0.0
    else:
        e_activity = st.selectbox("Fuel Source", get_activities(e_cat))
        e_data     = ef.get_emission_factor(e_cat, e_activity)
        e_unit     = e_data["unit"] if e_data else "unit"
        e_factor   = e_data["factor"] if e_data else 0.0

    e_qty = st.number_input(f"Quantity ({e_unit})", min_value=0.0, format="%.2f", key="e_qty")
    st.info(f"**GHG Protocol Factor:** {e_factor} kgCO₂e / {e_unit}")

    if st.button("Log Energy Entry", type="primary", key="btn_energy"):
        if e_qty <= 0:
            st.error("Quantity must be greater than 0.")
        else:
            # Re-read settings at click time to avoid stale factor
            cs_now    = st.session_state.get("company_settings", {})
            grid_now  = cs_now.get("grid_selection", "India Grid")
            if e_cat == "Electricity" and power_source == "Grid Electricity" and grid_now == "Custom / Manual Entry":
                e_factor = cs_now.get("custom_grid_factor", e_factor)
            mapped_scope = "Scope 2" if e_cat == "Electricity" else "Scope 1"
            if ds.add_emission_entry(e_date, defaults["business_unit"], mapped_scope,
                                     e_cat, e_activity, defaults["country"],
                                     defaults["facility"], defaults["responsible_person"],
                                     e_qty, e_unit, e_factor):
                st.success(f"Logged {e_qty} {e_unit} of {e_activity}.")

# Waste
with tabs[1]:
    w_date     = st.date_input("Date", key="w_date")
    w_cat      = "Waste"
    w_activity = st.selectbox("Disposal Method & Material", get_activities(w_cat))
    w_data     = ef.get_emission_factor(w_cat, w_activity)
    w_unit     = w_data["unit"] if w_data else "kg"
    w_factor   = w_data["factor"] if w_data else 0.0
    w_qty      = st.number_input(f"Quantity ({w_unit})", min_value=0.0, format="%.2f", key="w_qty")
    st.info(f"**GHG Protocol Factor:** {w_factor} kgCO₂e / {w_unit}")

    if st.button("Log Waste Entry", type="primary", key="btn_waste"):
        if w_qty <= 0:
            st.error("Quantity must be greater than 0.")
        else:
            if ds.add_emission_entry(w_date, defaults["business_unit"], "Scope 3",
                                     w_cat, w_activity, defaults["country"],
                                     defaults["facility"], defaults["responsible_person"],
                                     w_qty, w_unit, w_factor):
                st.success(f"Logged {w_qty} {w_unit} of {w_activity}.")

# Direct Carbon & Travel
with tabs[2]:
    c_date     = st.date_input("Date", key="c_date")
    c_cat      = st.selectbox("Emission Category", [
        "Mobile Combustion", "Refrigerants", "Business Travel",
        "Employee Commuting", "Water", "Purchased Goods & Services",
    ])
    c_activity = st.selectbox("Specific Activity", get_activities(c_cat))
    c_data     = ef.get_emission_factor(c_cat, c_activity)
    c_unit     = c_data["unit"] if c_data else "unit"
    c_factor   = c_data["factor"] if c_data else 0.0
    c_qty      = st.number_input(f"Quantity ({c_unit})", min_value=0.0, format="%.2f", key="c_qty")
    st.info(f"**GHG Protocol Factor:** {c_factor} kgCO₂e / {c_unit}")

    if st.button("Log Carbon Entry", type="primary", key="btn_carbon"):
        if c_qty <= 0:
            st.error("Quantity must be greater than 0.")
        else:
            scope_1_cats = ["Mobile Combustion", "Refrigerants"]
            mapped_scope = "Scope 1" if c_cat in scope_1_cats else "Scope 3"
            if ds.add_emission_entry(c_date, defaults["business_unit"], mapped_scope,
                                     c_cat, c_activity, defaults["country"],
                                     defaults["facility"], defaults["responsible_person"],
                                     c_qty, c_unit, c_factor):
                st.success(f"Logged {c_qty} {c_unit} for {c_activity}.")

# CSV Upload
with tabs[3]:
    st.warning("Required columns: `date, scope, category, activity, quantity, unit, emission_factor`")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file and st.button("Process CSV", type="primary", key="btn_csv"):
        with st.spinner("Hashing rows and verifying duplicates…"):
            ds.process_csv(uploaded_file)

# ── Database Management ────────────────────────────────────────────────────────
ui.sep("Database Management")

if len(st.session_state.emissions_data) == 0:
    st.info("Database is empty. Add entries above to begin.")
else:
    edit_df = st.session_state.emissions_data.copy()
    edit_df.insert(0, "Select for Deletion", False)

    st.caption("Tick rows in the 'Select for Deletion' column then confirm below.")

    edited_df = st.data_editor(
        edit_df,
        hide_index=True,
        use_container_width=True,
        disabled=st.session_state.emissions_data.columns.tolist(),
        column_config={
            "Select for Deletion": st.column_config.CheckboxColumn(required=True),
            "id": None,
        },
    )

    rows_to_delete = edited_df[edited_df["Select for Deletion"] == True]

    if not rows_to_delete.empty:
        st.error(f"{len(rows_to_delete)} row(s) selected for permanent deletion.")
        if st.button("Confirm Deletion", type="primary", use_container_width=True):
            target_ids     = rows_to_delete["id"].tolist()
            remaining_data = st.session_state.emissions_data[
                ~st.session_state.emissions_data["id"].isin(target_ids)
            ]
            st.session_state.emissions_data = remaining_data.reset_index(drop=True)
            ds.save_emissions_data()
            st.success(f"Deleted {len(rows_to_delete)} row(s).")
            st.rerun()

# ── Danger Zone ────────────────────────────────────────────────────────────────
ui.sep("Administration", small=True)

with st.expander("Danger Zone — Irreversible Actions"):
    st.warning("These actions bypass row selection and cannot be undone.")
    if st.button("Purge Entire Database", type="primary", use_container_width=True):
        st.session_state.emissions_data = pd.DataFrame(
            columns=st.session_state.emissions_data.columns
        )
        ds.save_emissions_data()
        st.success("Database purged.")
        st.rerun()