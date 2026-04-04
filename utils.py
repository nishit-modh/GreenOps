import streamlit as st
import pandas as pd
import os
import json
import shutil
import time
import hashlib
from fpdf import FPDF

# --- Core Styling & UI Components ---
def local_css():
    st.markdown('''
    <style>
    /* --- 1. BASE APP & BACKGROUND --- */
    /* Kill the default header/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Inject a subtle off-white/gray background to break the "plain white" stock look */
    .stApp {
        background-color: #F8FAFC; 
    }
    html, body, [class*="css"] { 
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif; 
        color: #1E293B;
    }
                
    /* --- THE SLEDGEHAMMER FIX --- */
    /* Force all text to stay dark regardless of system theme */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp span, .stApp label {
        color: #1A1A1A !important;
    }

    /* Keep metric values and labels consistent */
    .metric-value { color: #0F172A !important; }
    .metric-label { color: #64748B !important; }

    /* Ensure sidebar text stays visible */
    [data-testid="stSidebarNav"] a span {
        color: #475569 !important;
    }
    
    /* Active sidebar text should be green */
    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #166534 !important;
    }
    
    /* Kill the annoying anchor link chain icons on all headers */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, .stMarkdown a.anchor-link {
        display: none !important;
    }
    
    /* Inject a subtle off-white/gray background */
    .stApp {
        background-color: #F8FAFC; 
    }

    /* --- 2. SIDEBAR OVERHAUL --- */
    /* Style the sidebar container */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Target the native Streamlit page navigation links */
    [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }
    [data-testid="stSidebarNav"] ul {
        gap: 0.5rem;
    }
    [data-testid="stSidebarNav"] a {
        border-radius: 8px;
        margin: 0 1rem;
        padding: 0.5rem 1rem;
        color: #475569 !important;
        transition: all 0.2s ease;
    }
    /* Hover effect for sidebar links */
    [data-testid="stSidebarNav"] a:hover {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }
    /* Active page highlight */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #E6F4EA !important; /* Soft Green */
        color: #166534 !important; /* Dark Green Text */
        font-weight: 600;
        border-left: 4px solid #166534;
        border-radius: 4px 8px 8px 4px;
    }
    
    /* --- 3. TYPOGRAPHY --- */
    h1, h2, h3, h4, h5, h6 { 
        color: #0F172A; 
        font-weight: 700; 
        letter-spacing: -0.02em;
    }
    h1 { font-size: 2.2rem; padding-bottom: 1rem; border-bottom: 1px solid #E2E8F0; margin-bottom: 2rem;}
    
    /* --- 4. CARDS & ELEVATION --- */
    /* Force cards to be pure white against the gray background for depth */
    div.stCard, .stCard {
        background-color: #FFFFFF; 
        border-radius: 12px; 
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem; 
        border: 1px solid #E2E8F0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stCard:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        transform: translateY(-2px);
    }
    
    /* Custom Metric Cards */
    .metric-card {
        background-color: #FFFFFF; 
        border-radius: 12px; 
        padding: 1.5rem;
        text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-bottom: 4px solid #10B981; /* Emerald Green Bottom border */
        margin-bottom: 1.5rem;
        border-top: 1px solid #E2E8F0;
        border-left: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
    }
    .metric-value { font-size: 28px; font-weight: 800; margin: 0.5rem 0; color: #0F172A; }
    .metric-label { font-size: 13px; color: #64748B; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }
    
    /* --- 5. BUTTONS & INPUTS --- */
    .stButton>button {
        background-color: #10B981; /* Primary Emerald */
        color: white; 
        border-radius: 8px;
        border: none; 
        padding: 0.5rem 1rem; 
        font-weight: 600; 
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .stButton>button:hover { 
        background-color: #059669; 
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2); 
    }
    
    /* Tabs styling to make them look less 'stock' */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #E2E8F0; padding-bottom: 0px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent; 
        border-radius: 8px 8px 0px 0px; 
        padding: 12px 16px; 
        font-weight: 600; 
        color: #64748B;
    }
    .stTabs [aria-selected="true"] { 
        background-color: transparent !important; 
        color: #10B981 !important; 
        border-bottom: 3px solid #10B981;
    }
    
    /* Clean up inputs */
    [data-baseweb="input"], [data-baseweb="select"] { border-radius: 8px; }
    </style>
    ''', unsafe_allow_html=True)

def metric_card(title, value, description=None, icon=None, prefix="", suffix=""):
    st.markdown(f"""
    <div class="metric-card">
        {f'<div style="font-size:24px">{icon}</div>' if icon else ''}
        <div class="metric-label">{title}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {f'<div style="color:#aaa;font-size:12px">{description}</div>' if description else ''}
    </div>
    """, unsafe_allow_html=True)

# --- State Management & Setup ---
def init_session_state():
    os.makedirs("data", exist_ok=True)
    _EMPTY_COLS = ["date", "scope", "category", "activity", "quantity", "unit", "emission_factor", "emissions_kgCO2e"]

    if "emissions_data" not in st.session_state:
        if os.path.exists("data/emissions.json"):
            try:
                with open("data/emissions.json", "r") as fh:
                    raw = fh.read().strip()
                if raw:
                    loaded_df = pd.DataFrame(json.loads(raw))
                    if "date" in loaded_df.columns:
                        loaded_df["date"] = pd.to_datetime(loaded_df["date"], errors="coerce")
                    st.session_state.emissions_data = loaded_df
                else:
                    st.session_state.emissions_data = pd.DataFrame(columns=_EMPTY_COLS)
            except Exception as exc:
                st.error(f"Error loading emissions data: {exc}")
                st.session_state.emissions_data = pd.DataFrame(columns=_EMPTY_COLS)
        else:
            st.session_state.emissions_data = pd.DataFrame(columns=_EMPTY_COLS)

    if "company_settings" not in st.session_state:
        try:
            with open("data/settings.json", "r") as fh:
                st.session_state.company_settings = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            st.session_state.company_settings = {
                "company_name": "", "industry": "", "location": "",
                "contact_person": "", "email": "", "phone": "", "export_markets": []
            }

# --- Data Operations ---
def save_emissions_data() -> bool:
    try:
        temp_df = st.session_state.emissions_data.copy()
        if "date" in temp_df.columns:
            temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.strftime("%Y-%m-%d")
        with open("data/emissions.json", "w") as fh:
            json.dump(temp_df.to_dict("records") if len(temp_df) > 0 else [], fh, indent=2)
        return True
    except Exception as exc:
        st.error(f"Error saving data: {exc}")
        return False

def add_emission_entry(date, business_unit, scope, category, activity, country, facility, responsible_person, quantity, unit, emission_factor) -> bool:
    try:
        emissions_kgCO2e = float(quantity) * float(emission_factor)
        new_entry = pd.DataFrame([{
            "date": pd.to_datetime(date), "business_unit": business_unit, "scope": scope,
            "category": category, "activity": activity, "country": country,
            "facility": facility, "responsible_person": responsible_person,
            "quantity": float(quantity), "unit": unit, "emission_factor": float(emission_factor),
            "emissions_kgCO2e": emissions_kgCO2e,
        }])
        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, new_entry], ignore_index=True)
        return save_emissions_data()
    except Exception as exc:
        st.error(f"Error adding entry: {exc}")
        return False

def _row_hash(row):
    key = f"{row.get('date', '')}|{row.get('scope', '')}|{row.get('category', '')}|{row.get('activity', '')}|{row.get('quantity', '')}|{row.get('unit', '')}|{row.get('emission_factor', '')}"
    return hashlib.md5(key.encode()).hexdigest()

def process_csv(uploaded_file) -> bool:
    try:
        df = pd.read_csv(uploaded_file)
        df["quantity"] = df["quantity"].astype(float)
        df["emission_factor"] = df["emission_factor"].astype(float)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "emissions_kgCO2e" not in df.columns:
            df["emissions_kgCO2e"] = df["quantity"] * df["emission_factor"]
            
        if len(st.session_state.emissions_data) > 0:
            existing_hashes = set(st.session_state.emissions_data.apply(_row_hash, axis=1))
            incoming_hashes = df.apply(_row_hash, axis=1)
            is_duplicate = incoming_hashes.isin(existing_hashes)
            dup_count = int(is_duplicate.sum())
            if dup_count > 0:
                st.warning(f"⚠️ {dup_count} duplicate row(s) skipped.")
                df = df[~is_duplicate].copy()
            if df.empty: return False

        cs = st.session_state.get("company_settings", {})
        context_defaults = {"business_unit": cs.get("company_name", "Corporate"), "country": cs.get("location", "India"), "facility": cs.get("location", "HQ"), "responsible_person": cs.get("contact_person", "Admin")}
        for field, default in context_defaults.items():
            if field not in df.columns: df[field] = default

        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, df], ignore_index=True)
        if save_emissions_data():
            st.success(f"✅ {len(df)} new row(s) added successfully.")
            return True
        return False
    except Exception as exc:
        st.error(f"Error processing CSV: {exc}")
        return False

def compress_data(df: pd.DataFrame) -> str:
    if df.empty: return "No data available."
    total_impact = df["emissions_kgCO2e"].sum()
    scope_summary = df.groupby("scope")["emissions_kgCO2e"].sum().to_dict()
    top_offenders = df.groupby("activity")["emissions_kgCO2e"].sum().nlargest(3).to_dict()
    return f"Total Footprint: {total_impact:.2f} kgCO2e\nBreakdown by Scope: {scope_summary}\nTop 3 Carbon Offenders: {top_offenders}"

def generate_esg_pdf(df, cs, date_range_str):
    """Generates an executive PDF summary of emissions without crashing RAM."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "GreenOps ESG Compliance Report", 0, 1, "C")
    
    # Metadata
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Company: {cs.get('company_name', 'Enterprise')}", 0, 1)
    pdf.cell(0, 8, f"Location: {cs.get('location', 'Not Specified')}", 0, 1)
    pdf.cell(0, 8, f"Reporting Period: {date_range_str}", 0, 1)
    
    markets = ", ".join(cs.get('export_markets', [])) if cs.get('export_markets') else "None"
    pdf.cell(0, 8, f"Export Markets (CBAM Risk): {markets}", 0, 1)
    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # 1. Executive Summary
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    total_emissions = df['emissions_kgCO2e'].sum()
    pdf.cell(0, 8, f"Total Carbon Footprint: {total_emissions:,.2f} kgCO2e", 0, 1)

    # 2. Scope/Domain Breakdown
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Breakdown by Domain:", 0, 1)
    
    pdf.set_font("Arial", "", 11)
    scope_data = df.groupby('scope')['emissions_kgCO2e'].sum()
    for scope, val in scope_data.items():
        percentage = (val / total_emissions * 100) if total_emissions > 0 else 0
        pdf.cell(0, 8, f" - {scope}: {val:,.2f} kgCO2e ({percentage:.1f}%)", 0, 1)

    # 3. Top Carbon Bottlenecks
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Top 5 Carbon Bottlenecks (Highest Emitters):", 0, 1)
    
    pdf.set_font("Arial", "", 11)
    top_offenders = df.groupby('activity')['emissions_kgCO2e'].sum().nlargest(5)
    if not top_offenders.empty:
        for act, val in top_offenders.items():
            pdf.cell(0, 8, f" - {act}: {val:,.2f} kgCO2e", 0, 1)
    else:
        pdf.cell(0, 8, " - No emissions data available.", 0, 1)

    # Footer
    pdf.ln(15)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "This report was generated automatically by GreenOps. Calculations are based on user inputs and standard GHG Protocol emission factors.")

    # Return as bytes
    return pdf.output(dest='S').encode('latin1')