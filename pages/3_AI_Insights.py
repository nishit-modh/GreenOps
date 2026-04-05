import streamlit as st
import pandas as pd
import os
import data_store as ds
import ui_components as ui

st.set_page_config(page_title="AI Insights - GreenOps", page_icon="🌱", layout="wide")
ds.init_session_state()
ui.load_css()

ui.page_header(
    eyebrow="Intelligence",
    title="AI Insights",
    subtitle="Five specialist agents for reporting, offset advisory, regulation radar, and emission optimisation.",
)

if not os.getenv("GROQ_API_KEY"):
    st.error("**GROQ_API_KEY not set.** Add it to your `.env` file and restart the application.")
    st.stop()

from ai_agents import GreenOpsAgents


@st.cache_resource
def load_agents():
    return GreenOpsAgents()


agents = load_agents()

cs         = st.session_state.get("company_settings", {})
c_location = cs.get("location", "Not Specified")
c_industry = cs.get("industry", "Not Specified")
saved_markets = cs.get("export_markets", [])
c_exports  = ", ".join(saved_markets) if saved_markets else "None"

settings_incomplete = c_location == "Not Specified" or c_industry == "Not Specified"
if settings_incomplete:
    st.warning("Company profile incomplete. Configure **Settings** for accurate AI advice — agents will receive generic placeholders until then.")

# ── Analysis Timeframe ─────────────────────────────────────────────────────────
ui.sep("Analysis Timeframe")

if len(st.session_state.emissions_data) > 0:
    df_ai = st.session_state.emissions_data.copy()
    df_ai["date"] = pd.to_datetime(df_ai["date"], errors="coerce")
    df_ai = df_ai.dropna(subset=["date"])

    min_date = df_ai["date"].min().date()
    max_date = df_ai["date"].max().date()
    default_start = max_date - pd.Timedelta(days=365) if (max_date - min_date).days > 365 else min_date

    if "global_date_range" not in st.session_state:
        st.session_state.global_date_range = (default_start, max_date)

    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        start_date = st.date_input("Start Date", value=st.session_state.global_date_range[0],
                                   min_value=min_date, max_value=max_date, key="ai_start")
    with col2:
        end_date = st.date_input("End Date", value=st.session_state.global_date_range[1],
                                 min_value=min_date, max_value=max_date, key="ai_end")

    if start_date > end_date:
        st.error("Invalid range: Start Date cannot be after End Date.")
        st.stop()

    st.session_state.global_date_range = (start_date, end_date)
    filtered_df = df_ai[
        (df_ai["date"].dt.date >= start_date) & (df_ai["date"].dt.date <= end_date)
    ]

    excluded = len(df_ai) - len(filtered_df)
    if excluded > 0:
        st.caption(f"{excluded} row(s) with invalid or out-of-range dates excluded from analysis.")
else:
    filtered_df = pd.DataFrame()

# ── Agent Tabs ─────────────────────────────────────────────────────────────────
ui.sep("Agent Console")

ai_tabs = st.tabs([
    "Data Assistant",
    "Report Summary",
    "Offset Advisor",
    "Regulation Radar",
    "Emission Optimizer",
])

with ai_tabs[0]:
    st.caption("Classify an emission activity into the correct scope and UI category.")
    data_description = st.text_area(
        "Describe the emission activity",
        placeholder="e.g. We run diesel generators for backup power during load shedding.",
    )
    if st.button("Get Classification", type="primary") and data_description:
        with st.spinner("Analysing…"):
            try:
                result = agents.run_data_entry_crew(data_description)
                with st.container(border=True):
                    st.markdown(str(result))
            except Exception as e:
                st.error(f"Agent error: {e}")

with ai_tabs[1]:
    st.caption("Generate an executive ESG summary from the filtered dataset.")
    if filtered_df.empty:
        st.warning("No data in selected timeframe.")
    elif st.button("Generate Summary", type="primary"):
        with st.spinner("Generating report…"):
            try:
                result = agents.run_report_summary_crew(ds.compress_data(filtered_df))
                with st.container(border=True):
                    st.markdown(str(result))
            except Exception as e:
                st.error(f"Agent error: {e}")

with ai_tabs[2]:
    st.caption("Recommend verified offset projects based on your footprint and location.")
    if filtered_df.empty:
        st.warning("No data in selected timeframe.")
    else:
        total = filtered_df["emissions_kgCO2e"].sum()
        st.info(f"**Offset target:** {total:,.2f} kgCO₂e")
        if st.button("Get Recommendations", type="primary"):
            with st.spinner("Searching offset programs…"):
                try:
                    result = agents.run_offset_advice_crew(total, c_location, c_industry)
                    with st.container(border=True):
                        st.markdown(str(result))
                except Exception as e:
                    st.error(f"Agent error: {e}")

with ai_tabs[3]:
    st.caption("Assess carbon border tax and reporting obligations for your export markets.")
    if c_exports == "None":
        st.warning("No export markets configured. Add them in **Settings → Target Export Markets**.")
    elif st.button("Check Regulations", type="primary"):
        with st.spinner("Analysing compliance framework…"):
            try:
                result = agents.run_regulation_check_crew(c_location, c_industry, c_exports)
                with st.container(border=True):
                    st.markdown(str(result))
            except Exception as e:
                st.error(f"Agent error: {e}")

with ai_tabs[4]:
    st.caption("Identify the highest-impact operational changes to reduce your primary emission sources.")
    if filtered_df.empty:
        st.warning("No data in selected timeframe.")
    elif st.button("Generate Optimisation Strategy", type="primary"):
        with st.spinner("Analysing emission bottlenecks…"):
            try:
                result = agents.run_optimization_crew(ds.compress_data(filtered_df))
                with st.container(border=True):
                    st.markdown(str(result))
            except Exception as e:
                st.error(f"Agent error: {e}")