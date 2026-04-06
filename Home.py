import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import data_store as ds
import ui_components as ui

load_dotenv()

# set_page_config MUST be first Streamlit call
st.set_page_config(
    page_title="GreenOps — Carbon Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

ds.init_session_state()
ui.load_css()


# ─── LIVE DATA PULL ───────────────────────────────────────────────────────────
df_raw = st.session_state.emissions_data
has_data = len(df_raw) > 0

if has_data:
    df = df_raw.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    total_co2   = df["emissions_kgCO2e"].sum()
    entry_count = len(df)

    min_d = df["date"].min()
    max_d = df["date"].max()
    period_str  = f"{min_d.strftime('%b %Y')} – {max_d.strftime('%b %Y')}"
    # Change "%-d %b %Y" to "%d %b %Y"
    updated_str = max_d.strftime("%d %b %Y") if pd.notna(max_d) else "—"
    # Snapshot KPIs
    scope_totals  = df.groupby("ghg_scope")["emissions_kgCO2e"].sum() if "ghg_scope" in df.columns else df.groupby("scope")["emissions_kgCO2e"].sum()
    top_scope     = scope_totals.idxmax() if not scope_totals.empty else "—"
    top_scope_pct = (scope_totals.max() / total_co2 * 100) if total_co2 > 0 else 0

    top_emitter   = df.groupby("activity")["emissions_kgCO2e"].sum().idxmax() if total_co2 > 0 else "—"

    # Format helpers
    def fmt_co2(v):
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
        if v >= 1_000:     return f"{v/1_000:.1f}k"
        return f"{v:,.0f}"

    stat_emissions = fmt_co2(total_co2)
    stat_entries   = f"{entry_count:,}"
    stat_period    = period_str
else:
    stat_emissions = "—"
    stat_entries   = "—"
    stat_period    = "No data loaded"
    updated_str    = "—"

# Change "%-d %b %Y, %H:%M" to "%d %b %Y, %H:%M"
# Forces the timestamp to evaluate in IST, bypassing OS defaults
today_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %H:%M")

# ─── HERO SECTION ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="go-hero">
<div class="go-inner">
<div class="go-status-row">
<div class="go-status-dot"></div>
<span class="go-status-label">System Online</span>
<div class="go-status-sep"></div>
<span class="go-status-date">{today_str}</span>
</div>
<p class="go-hero-eyebrow">Carbon Intelligence Platform</p>
<h1 class="go-hero-h1">Measure. Report.<br><em>Reduce.</em></h1>
<p class="go-hero-sub">
Enterprise-grade Scope 1, 2 &amp; 3 emissions tracking with autonomous AI advisory —
built for SMEs that take compliance seriously.
</p>
<div class="go-hero-actions">
<a class="go-btn-amber" href="/Dashboard" target="_self">Open Dashboard →</a>
<a class="go-btn-ghost" href="/Data_Entry" target="_self">Log Emissions</a>
</div>
<div class="go-hero-rule"></div>
<div class="go-stats-grid">
<div class="go-stat">
<div class="go-stat-label">Total Footprint</div>
<div class="go-stat-value {'go-empty' if not has_data else ''}">{stat_emissions}</div>
<div class="go-stat-sub">{'kgCO₂e tracked' if has_data else 'no data — add entries to begin'}</div>
</div>
<div class="go-stat">
<div class="go-stat-label">Database Entries</div>
<div class="go-stat-value {'go-empty' if not has_data else ''}">{stat_entries}</div>
<div class="go-stat-sub">{'emission records' if has_data else 'upload CSV or log manually'}</div>
</div>
<div class="go-stat">
<div class="go-stat-label">Reporting Period</div>
<div class="go-stat-value {'go-empty' if not has_data else ''}" style="font-size:1.05rem;padding-top:0.3rem">{stat_period}</div>
<div class="go-stat-sub">{'last entry: ' + updated_str if has_data else 'no period established'}</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ─── CAPABILITIES SECTION ─────────────────────────────────────────────────────
st.markdown("""
<div class="go-section">
<div class="go-inner">
<div class="go-section-label">Platform Capabilities</div>
<div class="go-caps">
<div class="go-cap">
<div class="go-cap-num">01</div>
<div class="go-cap-title">GHG Protocol Physics Engine</div>
<div class="go-cap-desc">
Regionally-locked DEFRA and IPCC emission factors applied with strict
mathematical validation. Every entry is audit-traceable to a published
standard — no estimates, no hallucination.
</div>
</div>
<div class="go-cap">
<div class="go-cap-num">02</div>
<div class="go-cap-title">Autonomous AI Advisory</div>
<div class="go-cap-desc">
Five specialist agents powered by Llama-3 handle report generation,
offset sourcing, optimisation strategy, and regulatory gap analysis —
each grounded in your actual emissions data.
</div>
</div>
<div class="go-cap">
<div class="go-cap-num">03</div>
<div class="go-cap-title">CBAM &amp; BRSR Compliance Radar</div>
<div class="go-cap-desc">
Cross-references your export markets against live carbon border
adjustment frameworks. Flags compliance gaps before they become
border-tax liabilities.
</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ─── DATA SNAPSHOT (conditional) ──────────────────────────────────────────────
if has_data:
    top_scope_display   = top_scope.replace("Scope ", "S") if top_scope != "—" else "—"
    top_emitter_display = top_emitter[:22] + "…" if len(str(top_emitter)) > 22 else top_emitter

    st.markdown(f"""
<div class="go-section go-section-alt">
<div class="go-inner">
<div class="go-section-label">Live Data Snapshot</div>
<div class="go-kpi-grid">
<div class="go-kpi go-kpi-accent">
<div class="go-kpi-label">Total Footprint</div>
<div class="go-kpi-value">{stat_emissions}</div>
<div class="go-kpi-unit">kgCO₂e</div>
</div>
<div class="go-kpi">
<div class="go-kpi-label">Dominant Scope</div>
<div class="go-kpi-value">{top_scope_display}</div>
<div class="go-kpi-unit">{top_scope_pct:.1f}% of total</div>
</div>
<div class="go-kpi">
<div class="go-kpi-label">Primary Emitter</div>
<div class="go-kpi-value" style="font-size:1.1rem;padding-top:0.4rem;line-height:1.2">{top_emitter_display}</div>
<div class="go-kpi-unit">highest single source</div>
</div>
<div class="go-kpi">
<div class="go-kpi-label">Records</div>
<div class="go-kpi-value">{stat_entries}</div>
<div class="go-kpi-unit">across {stat_period}</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

else:
    st.markdown("""
<div class="go-section go-section-alt">
<div class="go-inner">
<div class="go-section-label">Live Data Snapshot</div>
<div class="go-snapshot-empty">
<div class="go-snapshot-empty-title">No emissions data in the database</div>
<div class="go-snapshot-empty-sub">
Head to <strong>Data Entry</strong> to log your first entries manually,
or upload a bulk CSV to populate the dashboard instantly.
The snapshot above will update in real time.
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ─── NAVIGATION GUIDE ─────────────────────────────────────────────────────────
st.markdown("""
<div class="go-section">
<div class="go-inner">
<div class="go-section-label">Where to Start</div>
<div class="go-steps-grid">
<div class="go-step">
<div class="go-step-num">01</div>
<div class="go-step-title">Settings</div>
<div class="go-step-desc">Configure your company profile, grid region, and export markets.</div>
</div>
<div class="go-step">
<div class="go-step-num">02</div>
<div class="go-step-title">Data Entry</div>
<div class="go-step-desc">Log energy, waste, and travel — or bulk-upload a CSV file.</div>
</div>
<div class="go-step">
<div class="go-step-num">03</div>
<div class="go-step-title">Dashboard</div>
<div class="go-step-desc">Analyse Scope breakdown, trends, and download compliance exports.</div>
</div>
<div class="go-step">
<div class="go-step-num">04</div>
<div class="go-step-title">AI Insights</div>
<div class="go-step-desc">Run AI agents for reports, offset advice, and regulation checks.</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="go-footer">
<div class="go-footer-inner">
<span class="go-footer-brand">GreenOps</span>
<span class="go-footer-meta">
v3.0.0
<span class="go-footer-divider"></span>
Carbon Accounting Engine
<span class="go-footer-divider"></span>
GHG Protocol &middot; DEFRA &middot; IPCC
</span>
</div>
</div>
""", unsafe_allow_html=True)