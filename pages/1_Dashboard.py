import streamlit as st
import pandas as pd
import plotly.express as px
import data_store as ds
import ui_components as ui
import report_generator as rg

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="GreenOps | ESG Analytics", page_icon="🌱", layout="wide")

# 2. Initialize state and apply CSS
ds.init_session_state()
ui.load_css()

st.markdown("<h1>Enterprise Analytics Dashboard</h1>", unsafe_allow_html=True)

if len(st.session_state.emissions_data) == 0:
    st.info("No data available. Proceed to Data Entry to initialize the database.")
    st.stop()

# Work on a copy
df = st.session_state.emissions_data.copy()
df['date'] = pd.to_datetime(df['date'])

# --- GLOBAL DATE FILTER ---
min_date = df['date'].min().date()
max_date = df['date'].max().date()
default_start = max_date - pd.Timedelta(days=365) if (max_date - min_date).days > 365 else min_date

st.markdown("### 📅 Temporal Filter")
filt_col1, _ = st.columns([1, 2])
with filt_col1:
    date_selection = st.date_input(
        "Select Date Range:", 
        value=(default_start, max_date),
        min_value=min_date, 
        max_value=max_date
    )
    
st.divider()

if len(date_selection) == 2:
    start_date, end_date = date_selection
    df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    if df.empty:
        st.warning("No data exists in this date range.")
        st.stop()
elif len(date_selection) == 1:
    st.info("Select the end date to apply filter.")
    st.stop()

# --- ROBUST CORE MATH (Fixed for Standardized Scopes) ---
total_impact = df['emissions_kgCO2e'].sum()

# Energy Math: Targets Scope 2 (Grid) and Scope 1 (Diesel/Generators)
energy_df = df[df['category'].isin(['Purchased Electricity', 'Stationary Combustion'])].copy()
total_energy = energy_df['quantity'].sum()
# Detects 'Rooftop Solar' or any activity containing 'solar'
renew_energy = energy_df[energy_df['activity'].str.contains('solar', case=False, na=False)]['quantity'].sum()
renew_ratio = (renew_energy / total_energy * 100) if total_energy > 0 else 0

# Waste Math: Targets Scope 3 Waste
waste_df = df[df['category'] == 'Waste Generated'].copy()
total_waste = waste_df['quantity'].sum()
# Detects recycling by keyword
recycled_waste = waste_df[waste_df['activity'].str.contains('recycl|scrap', case=False, na=False)]['quantity'].sum()
recycle_ratio = (recycled_waste / total_waste * 100) if total_waste > 0 else 0

# --- EXPORT REPORTS ---
st.markdown("### 📥 Compliance Exports")
exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    csv_export = df.to_csv(index=False).encode('utf-8')
    st.download_button("📄 Download Raw Data (CSV)", data=csv_export, file_name="GreenOps_Data.csv", mime="text/csv", use_container_width=True)

with exp_col2:
    date_range_str = f"{df['date'].min().date()} to {df['date'].max().date()}"
    pdf_bytes = rg.generate_esg_pdf(df, st.session_state.get('company_settings', {}), date_range_str)
    st.download_button("📊 Download Executive Report (PDF)", data=pdf_bytes, file_name="GreenOps_Report.pdf", mime="application/pdf", use_container_width=True)

# --- THE 3-TAB ARCHITECTURE ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "⚡ Energy Deep-Dive", "🗑️ Waste & Logistics"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1: ui.metric_card("Total Impact", f"{total_impact:,.0f}", "kgCO2e", "🌍")
    with col2: ui.metric_card("Renewable Ratio", f"{renew_ratio:.1f}", "% of Total Power", "🌱")
    with col3: ui.metric_card("Recycling Rate", f"{recycle_ratio:.1f}", "% of Total Waste", "♻️")
    with col4: ui.metric_card("Total Entries", str(len(df)), "Database Rows", "🗄️")
        
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Impact by Scope**")
        domain_data = df.groupby('scope')['emissions_kgCO2e'].sum().reset_index()
        fig1 = px.pie(domain_data, values='emissions_kgCO2e', names='scope', hole=0.4, color_discrete_sequence=px.colors.qualitative.G10)
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.markdown("**Temporal Trend**")
        df['month'] = df['date'].dt.strftime('%Y-%m')
        trend = df.groupby('month')['emissions_kgCO2e'].sum().reset_index()
        fig2 = px.line(trend, x='month', y='emissions_kgCO2e', markers=True, color_discrete_sequence=["#10B948"])
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    if energy_df.empty:
        st.info("No Energy data logged.")
    else:
        e1, e2 = st.columns(2)
        
        with e1:
            st.markdown("**Carbon Footprint by Source (kgCO2e)**")
            # Aggregates emissions to show which fuel is the "dirtiest"
            fig_pie = px.pie(
                energy_df.groupby('activity')['emissions_kgCO2e'].sum().reset_index(), 
                values='emissions_kgCO2e', 
                names='activity', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.G10
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with e2:
            st.markdown("**Energy Mix Evolution (Monthly)**")
            # 1. Prepare monthly data
            trend_df = energy_df.copy()
            trend_df['Month'] = trend_df['date'].dt.strftime('%Y-%m')
            
            # 2. Group by Month and Activity
            mix_data = trend_df.groupby(['Month', 'activity'])['quantity'].sum().reset_index()
            
            # 3. Create a Stacked Area Chart
            # This shows the "Volume" of energy and how the proportions change
            fig_area = px.area(
                mix_data, 
                x="Month", 
                y="quantity", 
                color="activity",
                line_group="activity",
                labels={"quantity": "Consumption (kWh/Liter)"},
                color_discrete_map={
                    "Rooftop Solar": "#10b981", # Emerald Green
                    "State Grid": "#3b82f6",    # Blue
                    "DG Set (Diesel)": "#ef4444" # Red
                },
                template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"
            )
            
            fig_area.update_layout(
                margin=dict(t=30, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_area, use_container_width=True)

with tab3:
    w1, w2 = st.columns(2)
    with w1:
        st.markdown("**Direct Carbon (Logistics & Fugitive)**")
        direct_df = df[df['category'].isin(['Mobile Combustion', 'Fugitive Emissions'])]
        if not direct_df.empty:
            fig6 = px.pie(direct_df, names='category', values='emissions_kgCO2e', hole=0.4,color_discrete_sequence=px.colors.qualitative.G10)
            st.plotly_chart(fig6, use_container_width=True)
        else: st.info("No Direct Carbon data.")
            
    with w2:
        st.markdown("**Waste Lifecycle Analysis**")
        if not waste_df.empty:
            # Group by activity to show Landfill vs Recycling
            fig5 = px.bar(waste_df.groupby('activity')['quantity'].sum().reset_index(), 
                          x='activity', y='quantity', color='activity',
                          color_discrete_map={'Mixed Municipal Waste': "#445bef", 'Scrap Metal & Cardboard': '#10B948'})
            st.plotly_chart(fig5, use_container_width=True)
        else: st.info("No Waste data.")

st.divider()
st.markdown("### 🧠 Automated System Insights")
i1, i2 = st.columns(2)
with i1:
    days = (df['date'].max() - df['date'].min()).days
    if days > 5:
        st.warning(f"**📈 Projected Annual Run-Rate:** ~**{(total_impact/days)*365:,.0f} kgCO2e**")
    else: st.info("Insufficient data for projection.")
with i2:
    if total_impact > 0:
        worst = df.groupby('activity')['emissions_kgCO2e'].sum()
        st.error(f"**⚠️ Primary Bottleneck:** **{worst.idxmax()}** ({worst.max():,.0f} kgCO2e)")