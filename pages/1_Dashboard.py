import streamlit as st
import pandas as pd
import plotly.express as px
import data_store as ds
import ui_components as ui
import report_generator as rg

st.set_page_config(page_title="Dashboard - GreenOps", page_icon="🌱", layout="wide")
ds.init_session_state()
ui.load_css()

ui.page_header(
    eyebrow="Analytics",
    title="Dashboard",
    subtitle="Scope 1, 2 and 3 emissions overview with temporal filtering and compliance exports.",
)

if len(st.session_state.emissions_data) == 0:
    st.info("No data available. Proceed to Data Entry to initialise the database.")
    st.stop()

df = st.session_state.emissions_data.copy()
df["date"] = pd.to_datetime(df["date"])

# ── Temporal Filter ────────────────────────────────────────────────────────────
ui.sep("Temporal Filter")

min_date = df["date"].min().date()
max_date = df["date"].max().date()
default_start = max_date - pd.Timedelta(days=365) if (max_date - min_date).days > 365 else min_date

if "global_date_range" not in st.session_state:
    st.session_state.global_date_range = (default_start, max_date)

filt_col1, filt_col2, _ = st.columns([1, 1, 2])
with filt_col1:
    start_date = st.date_input("Start Date", value=st.session_state.global_date_range[0],
                               min_value=min_date, max_value=max_date, key="dash_start")
with filt_col2:
    end_date = st.date_input("End Date", value=st.session_state.global_date_range[1],
                             min_value=min_date, max_value=max_date, key="dash_end")

if start_date > end_date:
    st.error("Invalid range: Start Date cannot be after End Date.")
    st.stop()

st.session_state.global_date_range = (start_date, end_date)
df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]

if df.empty:
    st.warning("No data exists in this date range.")
    st.stop()

# ── Core Math ──────────────────────────────────────────────────────────────────
total_impact = df["emissions_kgCO2e"].sum()

energy_df = df[df["category"].str.contains("Electricity|Stationary", case=False, na=False)].copy()
elec_df   = energy_df[energy_df["category"].str.contains("Electricity", case=False, na=False)]
total_elec  = elec_df["quantity"].sum()
renew_energy = elec_df[elec_df["activity"].str.contains("solar|wind", case=False, na=False)]["quantity"].sum()
renew_ratio  = (renew_energy / total_elec * 100) if total_elec > 0 else 0

waste_df    = df[df["category"].str.contains("Waste", case=False, na=False)].copy()
total_waste = waste_df["quantity"].sum()
recycled_waste = waste_df[waste_df["activity"].str.contains("recycl|scrap", case=False, na=False)]["quantity"].sum()
recycle_ratio  = (recycled_waste / total_waste * 100) if total_waste > 0 else 0

# ── Compliance Exports ─────────────────────────────────────────────────────────
ui.sep("Compliance Exports")

exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    csv_export = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Raw Data (CSV)", data=csv_export,
                       file_name="GreenOps_Data.csv", mime="text/csv",
                       use_container_width=True)
with exp_col2:
    date_range_str = f"{df['date'].min().date()} to {df['date'].max().date()}"
    try:
        pdf_bytes = rg.generate_esg_pdf(df, st.session_state.get("company_settings", {}), date_range_str)
        st.download_button("Download Executive Report (PDF)", data=pdf_bytes,
                           file_name="GreenOps_Report.pdf", mime="application/pdf",
                           use_container_width=True)
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

# ── Charts ─────────────────────────────────────────────────────────────────────
ui.sep("Analysis")

tab1, tab2, tab3 = st.tabs(["Executive Summary", "Energy Deep-Dive", "Waste & Logistics"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ui.metric_card("Total Impact", f"{total_impact:,.0f}", "kgCO₂e")
    with col2:
        ui.metric_card("Renewable Ratio", f"{renew_ratio:.1f}%", "of electrical power")
    with col3:
        ui.metric_card("Recycling Rate", f"{recycle_ratio:.1f}%", "of total waste")
    with col4:
        ui.metric_card("Total Entries", str(len(df)), "database rows")

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Impact by GHG Scope")
        scope_col = "ghg_scope" if "ghg_scope" in df.columns else "scope"
        domain_data = df.groupby(scope_col)["emissions_kgCO2e"].sum().reset_index()
        fig1 = px.pie(domain_data, values="emissions_kgCO2e", names=scope_col,
                      hole=0.4, color_discrete_sequence=["#102d1d", "#C2410C", "#6B7280"])
        fig1.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.caption("Monthly Emissions Trend")
        df["month"] = df["date"].dt.strftime("%Y-%m")
        trend = df.groupby("month")["emissions_kgCO2e"].sum().reset_index()
        fig2 = px.line(trend, x="month", y="emissions_kgCO2e", markers=True,
                       color_discrete_sequence=["#102d1d"])
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F0EFE9"))
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    if energy_df.empty:
        st.info("No energy data logged.")
    else:
        e1, e2 = st.columns(2)
        with e1:
            st.caption("Carbon Footprint by Source (kgCO₂e)")
            fig_pie = px.pie(
                energy_df.groupby("activity")["emissions_kgCO2e"].sum().reset_index(),
                values="emissions_kgCO2e", names="activity", hole=0.4,
                color_discrete_sequence=["#102d1d", "#C2410C", "#6B7280", "#D1D1CE", "#4B5563"])
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                                  paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
        with e2:
            st.caption("Energy Mix — kWh Sources (Monthly)")
            elec_trend = elec_df.copy()
            elec_trend["Month"] = elec_trend["date"].dt.strftime("%Y-%m")
            mix_data = elec_trend.groupby(["Month", "activity"])["quantity"].sum().reset_index()
            fig_area = px.area(mix_data, x="Month", y="quantity", color="activity",
                               labels={"quantity": "kWh"},
                               color_discrete_sequence=["#102d1d", "#C2410C", "#6B7280"])
            fig_area.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   legend=dict(orientation="h", y=1.02, x=1, xanchor="right"))
            st.plotly_chart(fig_area, use_container_width=True)

with tab3:
    w1, w2 = st.columns(2)
    with w1:
        st.caption("Direct Carbon — Logistics & Fugitive")
        direct_df = df[df["category"].isin(["Mobile Combustion", "Fugitive Emissions"])]
        if not direct_df.empty:
            fig6 = px.pie(direct_df, names="category", values="emissions_kgCO2e", hole=0.4,
                          color_discrete_sequence=["#102d1d", "#C2410C"])
            fig6.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                               paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("No direct carbon data.")
    with w2:
        st.caption("Waste Lifecycle — Volume by Disposal Method")
        if not waste_df.empty:
            fig5 = px.bar(
                waste_df.groupby("activity")["quantity"].sum().reset_index(),
                x="activity", y="quantity", color="activity",
                color_discrete_sequence=["#102d1d", "#C2410C", "#6B7280", "#D1D1CE"])
            fig5.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               showlegend=False, xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True, gridcolor="#F0EFE9"))
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("No waste data.")

# ── System Insights ────────────────────────────────────────────────────────────
ui.sep("Automated Insights")

i1, i2 = st.columns(2)
with i1:
    days = (df["date"].max() - df["date"].min()).days
    safe_days = max(days, 1)
    if days >= 1:
        projected_annual = (total_impact / safe_days) * 365
        st.warning(f"**Projected Annual Run-Rate:** ~{projected_annual:,.0f} kgCO₂e")
    else:
        st.info("Insufficient temporal data for projection. Log at least 2 days of data.")
with i2:
    if total_impact > 0:
        worst = df.groupby("activity")["emissions_kgCO2e"].sum()
        st.error(f"**Primary Bottleneck:** {worst.idxmax()} ({worst.max():,.0f} kgCO₂e)")