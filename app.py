import streamlit as st
import pandas as pd
import os
import json
import shutil
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Set page config for wide layout
st.set_page_config(page_title="GreenOps", page_icon="🌱", layout="wide")

# Initialize session state variables if they don't exist
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'emissions_data' not in st.session_state:
    # Load data if exists, otherwise create empty dataframe
    if os.path.exists('data/emissions.json'):
        try:
            with open('data/emissions.json', 'r') as f:
                data = f.read().strip()
                if data:  # Check if file is not empty
                    try:
                        st.session_state.emissions_data = pd.DataFrame(json.loads(data))
                    except json.JSONDecodeError:
                        # Create a backup of the corrupted file
                        backup_file = f'data/emissions_backup_{int(time.time())}.json'
                        shutil.copy('data/emissions.json', backup_file)
                        st.warning(f"Corrupted emissions data file found. A backup has been created at {backup_file}")
                        # Create empty dataframe
                        st.session_state.emissions_data = pd.DataFrame(columns=[
                            'date', 'scope', 'category', 'activity', 'quantity', 
                            'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
                        ])
                else:
                    # Empty file, create new DataFrame
                    st.session_state.emissions_data = pd.DataFrame(columns=[
                        'date', 'scope', 'category', 'activity', 'quantity', 
                        'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
                    ])
        except Exception as e:
            st.error(f"Error loading emissions data: {str(e)}")
            # Create empty dataframe if loading fails
            st.session_state.emissions_data = pd.DataFrame(columns=[
                'date', 'scope', 'category', 'activity', 'quantity', 
                'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
            ])
            # Make sure data directory exists
            os.makedirs('data', exist_ok=True)
    else:
        st.session_state.emissions_data = pd.DataFrame(columns=[
            'date', 'scope', 'category', 'activity', 'quantity', 
            'unit', 'emission_factor', 'emissions_kgCO2e', 'notes'
        ])
        # Make sure data directory exists
        os.makedirs('data', exist_ok=True)
if 'active_page' not in st.session_state:
    st.session_state.active_page = "AI Insights"

# Translation dictionary
translations = {
    'English': {
        'title': 'GreenOps',
        'subtitle': 'Sustainability Accounting Tool for SMEs',
        'dashboard': 'Dashboard',
        'data_entry': 'Data Entry',
        'reports': 'Reports',
        'settings': 'Settings',
        'about': 'About',
        'scope1': 'Scope 1 (Direct Emissions)',
        'scope2': 'Scope 2 (Indirect Emissions - Purchased Energy)',
        'scope3': 'Scope 3 (Other Indirect Emissions)',
        'date': 'Date',
        'scope': 'Scope',
        'category': 'Category',
        'activity': 'Activity',
        'quantity': 'Quantity',
        'unit': 'Unit',
        'emission_factor': 'Emission Factor',
        'emissions': 'Emissions (kgCO2e)',
        'notes': 'Notes',
        'add_entry': 'Add Entry',
        'upload_csv': 'Upload CSV',
        'download_report': 'Download Report',
        'total_emissions': 'Total Emissions',
        'emissions_by_scope': 'Emissions by Scope',
        'emissions_by_category': 'Emissions by Category',
        'emissions_over_time': 'Emissions Over Time',
        'language': 'Language',
        'save': 'Save',
        'cancel': 'Cancel',
        'success': 'Success!',
        'error': 'Error!',
        'entry_added': 'Entry added successfully!',
        'csv_uploaded': 'CSV uploaded successfully!',
        'report_downloaded': 'Report downloaded successfully!',
        'settings_saved': 'Settings saved successfully!',
        'no_data': 'No data available.',
        'welcome_message': 'Welcome to GreenOps! Start by adding your emissions data or uploading a CSV file.',
        'custom_category': 'Custom Category',
        'custom_activity': 'Custom Activity',
        'custom_unit': 'Custom Unit',
        'entry_failed': 'Failed to add entry.'
    },
    'Hindi': {
        'title': 'GreenOps',
        'subtitle': 'एसएमई के लिए कार्बन अकाउंटिंग और रिपोर्टिंग टूल',
        'dashboard': 'डैशबोर्ड',
        'data_entry': 'डेटा प्रविष्टि',
        'reports': 'रिपोर्ट',
        'settings': 'सेटिंग्स',
        'about': 'के बारे में',
        'scope1': 'स्कोप 1 (प्रत्यक्ष उत्सर्जन)',
        'scope2': 'स्कोप 2 (अप्रत्यक्ष उत्सर्जन - खरीदी गई ऊर्जा)',
        'scope3': 'स्कोप 3 (अन्य अप्रत्यक्ष उत्सर्जन)',
        'date': 'तारीख',
        'scope': 'स्कोप',
        'category': 'श्रेणी',
        'activity': 'गतिविधि',
        'quantity': 'मात्रा',
        'unit': 'इकाई',
        'emission_factor': 'उत्सर्जन कारक',
        'emissions': 'उत्सर्जन (kgCO2e)',
        'notes': 'नोट्स',
        'add_entry': 'प्रविष्टि जोड़ें',
        'upload_csv': 'CSV अपलोड करें',
        'download_report': 'रिपोर्ट डाउनलोड करें',
        'total_emissions': 'कुल उत्सर्जन',
        'emissions_by_scope': 'स्कोप द्वारा उत्सर्जन',
        'emissions_by_category': 'श्रेणी द्वारा उत्सर्जन',
        'emissions_over_time': 'समय के साथ उत्सर्जन',
        'language': 'भाषा',
        'save': 'सहेजें',
        'cancel': 'रद्द करें',
        'success': 'सफलता!',
        'error': 'त्रुटि!',
        'entry_added': 'प्रविष्टि सफलतापूर्वक जोड़ी गई!',
        'csv_uploaded': 'CSV सफलतापूर्वक अपलोड की गई!',
        'report_downloaded': 'रिपोर्ट सफलतापूर्वक डाउनलोड की गई!',
        'settings_saved': 'सेटिंग्स सफलतापूर्वक सहेजी गईं!',
        'no_data': 'कोई डेटा उपलब्ध नहीं है।',
        'welcome_message': 'आपका कार्बन फुटप्रिंट में आपका स्वागत है! अपना उत्सर्जन डेटा जोड़कर या CSV फ़ाइल अपलोड करके प्रारंभ करें।',
        'custom_category': 'कस्टम श्रेणी',
        'custom_activity': 'कस्टम गतिविधि',
        'custom_unit': 'कस्टम इकाई',
        'entry_failed': 'प्रविष्टि जोड़ने में विफल रहा।'
    }
}

# Function to get translated text
def t(key):
    lang = st.session_state.language
    return translations.get(lang, {}).get(key, key)

# Function to save emissions data
def save_emissions_data():
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Create a backup of the existing file if it exists
        if os.path.exists('data/emissions.json'):
            backup_path = 'data/emissions_backup.json'
            try:
                with open('data/emissions.json', 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            except Exception:
                # Continue even if backup fails
                pass
        
# Save data to JSON file with proper formatting
        with open('data/emissions.json', 'w') as f:
            if len(st.session_state.emissions_data) > 0:
                # Nuke-proof: Force dates to strings before saving to prevent Timestamp crashes
                temp_df = st.session_state.emissions_data.copy()
                if 'date' in temp_df.columns:
                    temp_df['date'] = pd.to_datetime(temp_df['date']).dt.strftime('%Y-%m-%d')
                json.dump(temp_df.to_dict('records'), f, indent=2)
            else:
                # Write empty array if no data
                f.write('[]')              
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

# Function to add new emission entry
def add_emission_entry(date, business_unit, scope, category, activity, country, facility, responsible_person, quantity, unit, emission_factor):
    """Add a new lean emission entry."""
    try:
        emissions_kgCO2e = float(quantity) * float(emission_factor)
        
        new_entry = pd.DataFrame([{
            'date': date.strftime('%Y-%m-%d'),
            'business_unit': business_unit,
            'scope': scope,
            'category': category,
            'activity': activity,
            'country': country,
            'facility': facility,
            'responsible_person': responsible_person,
            'quantity': float(quantity),
            'unit': unit,
            'emission_factor': float(emission_factor),
            'emissions_kgCO2e': emissions_kgCO2e
        }])
        
        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, new_entry], ignore_index=True)
        return save_emissions_data()
    except Exception as e:
        st.error(f"Error adding entry: {str(e)}")
        return False

def delete_emission_entry(index):
    try:
        # Make a copy of the current data
        if len(st.session_state.emissions_data) > index:
            # Drop the row at the specified index
            st.session_state.emissions_data = st.session_state.emissions_data.drop(index).reset_index(drop=True)
            
            # Save data and return success/failure
            return save_emissions_data()
        else:
            st.error(f"Index {index} is invalid for deletion, No deletion performed.")
            return False
    except Exception as e:
        st.error(f"Error deleting entry: {str(e)}")
        return False

# Function to process uploaded CSV
def process_csv(uploaded_file):
    """Process uploaded CSV file and add to emissions data."""
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        required_columns = ['date', 'scope', 'category', 'activity', 'quantity', 'unit', 'emission_factor']
        
        # Check if all required columns exist
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV must contain all required columns: {', '.join(required_columns)}")
            return False
        
        # Validate data types
        try:
            # Convert quantity and emission_factor to float
            df['quantity'] = df['quantity'].astype(float)
            df['emission_factor'] = df['emission_factor'].astype(float)
            
            # Validate dates
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        except Exception as e:
            st.error(f"Data validation error: {str(e)}")
            return False
        
        # Calculate emissions if not provided
        if 'emissions_kgCO2e' not in df.columns:
            df['emissions_kgCO2e'] = df['quantity'] * df['emission_factor']
        
        # Add minimal enterprise context if missing from CSV
        cs = st.session_state.get('company_settings', {})
        context_fields = {
            'business_unit': cs.get("company_name", "Corporate"),
            'country': cs.get("location", "India"), # Will use location or default to India
            'facility': cs.get("location", "HQ"),
            'responsible_person': cs.get("contact_person", "Admin")
        }
        
        # Add missing columns with default values
        for field, default_value in context_fields.items():
            if field not in df.columns:
                df[field] = default_value
        
        # Append to existing data
        st.session_state.emissions_data = pd.concat([st.session_state.emissions_data, df], ignore_index=True)
        
        # Save data
        if save_emissions_data():
            st.success(f"Successfully added {len(df)} entries")
            return True
        else:
            st.error("Failed to save data")
            return False
    except Exception as e:
        st.error(f"Error processing CSV: {str(e)}")
        return False

# Function to generate report
def generate_report():
    # Create a BytesIO object
    buffer = BytesIO()
    
    # Create a simple CSV report for now
    st.session_state.emissions_data.to_csv(buffer, index=False)
    buffer.seek(0)
    
    return buffer

# Custom CSS
def local_css():
    st.markdown('''
    <style>
    /* Remove default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Base styling */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar styling - IMPORTANT: Override the dark background */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #ffffff !important;
        padding: 2rem 1rem;
    }
    
    /* Sidebar title */
    [data-testid="stSidebar"] h1 {
        color: #2E7D32;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 0;
    }
    
    /* Sidebar subtitle */
    [data-testid="stSidebar"] p {
        color: #555555;
        font-size: 14px;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #2E7D32;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.2rem;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }
    
    /* Card styling */
    div.stCard {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin-bottom: 1.5rem;
        border: none;
    }
    
    /* Card styling */
    .stCard {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border: 1px solid #f0f0f0;
    }
    
    /* AI Insights card styling */
    .stCard p {
        margin-bottom: 10px;
        line-height: 1.6;
    }
    
    .stCard h1, .stCard h2, .stCard h3, .stCard h4 {
        color: #2E7D32;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    .stCard ul, .stCard ol {
        margin-left: 20px;
        margin-bottom: 15px;
    }
    
    .stCard table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 15px;
    }
    
    .stCard th, .stCard td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    .stCard th {
        background-color: #f2f2f2;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border-left: 4px solid #2E7D32;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 0.5rem 0;
        color: #2E7D32;
    }
    
    .metric-label {
        font-size: 14px;
        color: #555555;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #388E3C;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton>button:focus {
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.5);
    }
    
    /* Secondary buttons */
    .stButton>button[kind="secondary"] {
        background-color: #f8f9fa;
        color: #2E7D32;
        border: 1px solid #2E7D32;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background-color: #f1f3f5;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32 !important;
        color: white !important;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #FFF8E1;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #555555;
        font-size: 12px;
        margin-top: 2rem;
        border-top: 1px solid #e9ecef;
    }
    
    /* Form fields */
    [data-baseweb="input"] {
        border-radius: 4px;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        border-radius: 4px;
    }
    
    /* Sidebar navigation buttons */
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        text-align: left;
        background-color: transparent;
        color: #333333;
        border: none;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        font-weight: normal;
        display: flex;
        align-items: center;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #f1f3f5;
        box-shadow: none;
    }
    
    /* Active navigation button */
    [data-testid="stSidebar"] .stButton>button.active {
        background-color: #E8F5E9;
        border-left: 4px solid #2E7D32;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: 0;
        border-top: 1px solid #e9ecef;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        border: 1px solid #e9ecef;
    }
    
    .dataframe th {
        background-color: #f8f9fa;
        color: #333333;
        font-weight: 500;
        text-align: left;
        padding: 0.75rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .dataframe td {
        padding: 0.75rem;
        border-bottom: 1px solid #e9ecef;
    }
    
    .dataframe tr:hover {
        background-color: #f8f9fa;
    }
    </style>
    ''', unsafe_allow_html=True)

# Navigation component
def render_navigation():
    nav_items = [
        {"icon": "🤖", "label": "AI Insights", "id": "AI Insights"},
        {"icon": "📝", "label": "Data Entry", "id": "Data Entry"},
        {"icon": "📊", "label": "Dashboard", "id": "Dashboard"},
        {"icon": "⚙️", "label": "Settings", "id": "Settings"}
    ]
    
    st.markdown("### Navigation")
    
    for item in nav_items:
        active_class = "active" if st.session_state.active_page == item["id"] else ""
        if st.sidebar.button(
            f"{item['icon']} {item['label']}", 
            key=f"nav_{item['id']}",
            help=f"Go to {item['label']}",
            use_container_width=True
        ):
            st.session_state.active_page = item["id"]
            st.rerun()

# Metric card component
def metric_card(title, value, description=None, icon=None, prefix="", suffix=""):
    st.markdown(f'''
    <div class="metric-card">
        {f'<div style="font-size: 24px;">{icon}</div>' if icon else ''}
        <div class="metric-label">{title}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {f'<div style="color: #aaa; font-size: 12px;">{description}</div>' if description else ''}
    </div>
    ''', unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Sidebar
with st.sidebar:
    st.markdown(f"<h1 style='margin-bottom: 0; font-size: 24px;'>{t('title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-top: 0; color: #aaa; font-size: 12px;'>{t('subtitle')}</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Language selector
    language = st.selectbox(t('language'), ['English', 'Hindi'], key='language')
    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()
    
    st.divider()
    
    # Navigation
    render_navigation()
    
    st.divider()
    
    # Footer
    st.markdown(
        "<div class='footer' style='color: #555555;'> 2026 GreenOps<br>Product Owner: GTU<br>abc123@gmail.com</div>",
        unsafe_allow_html=True
    )

# Main content
if st.session_state.active_page == "Dashboard":
    st.markdown("<h1>Enterprise Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.emissions_data) == 0:
        st.info("No data available. Proceed to Data Entry to initialize the database.")
    else:
        df = st.session_state.emissions_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # --- CORE MATH & FILTERING ---
        total_impact = df['emissions_kgCO2e'].sum()
        
        # Energy Math
        energy_df = df[df['scope'] == 'Energy Consumption']
        total_energy = energy_df['quantity'].sum()
        renew_energy = energy_df[energy_df['category'] == 'Renewable (Clean)']['quantity'].sum()
        renew_ratio = (renew_energy / total_energy * 100) if total_energy > 0 else 0
        
        # Waste Math
        waste_df = df[df['scope'] == 'Waste Management']
        total_waste = waste_df['quantity'].sum()
        recycled_waste = waste_df[waste_df['category'] == 'Recycled/Composted']['quantity'].sum()
        recycle_ratio = (recycled_waste / total_waste * 100) if total_waste > 0 else 0

        # --- HIGH-LEVEL INSIGHT ENGINE ---
        st.markdown("### 🧠 Automated System Insights")
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            # Insight 1: Predictive Run-Rate
            days_logged = (df['date'].max() - df['date'].min()).days
            if days_logged > 5: # Need a minimum baseline for projection
                daily_rate = total_impact / days_logged
                projected_annual = daily_rate * 365
                st.warning(f"**📈 Projected Annual Run-Rate:** Based on current velocity, your facility is on track to emit **{projected_annual:,.0f} kgCO2e** over 12 months.")
            else:
                st.info("**📈 Projected Annual Run-Rate:** Insufficient temporal data (need >5 days spread) to calculate yearly projection.")
                
        with insight_col2:
            # Insight 2: Worst Offender Identification
            if total_impact > 0:
                worst_offender = df.groupby('activity')['emissions_kgCO2e'].sum().idxmax()
                worst_value = df.groupby('activity')['emissions_kgCO2e'].sum().max()
                st.error(f"**⚠️ Primary Carbon Bottleneck:** **{worst_offender}** is currently responsible for **{worst_value:,.0f} kgCO2e**, making it your highest priority for reduction.")

        st.divider()

        # --- EXPORT REPORT ---
        csv_export = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download ESG Compliance Report",
            data=csv_export,
            file_name=f"GreenOps_Report_{st.session_state.get('company_settings', {}).get('company_name', 'Enterprise')}.csv",
            mime="text/csv",
        )

        # --- THE 3-TAB ARCHITECTURE ---
        tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "⚡ Energy Deep-Dive", "🗑️ Waste & Logistics"])
        
        # ==========================================
        # TAB 1: EXECUTIVE SUMMARY
        # ==========================================
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric_card("Total Impact", f"{total_impact:,.0f}", "kgCO2e", "🌍")
            with col2:
                metric_card("Renewable Ratio", f"{renew_ratio:.1f}", "% of Total Power", "🌱")
            with col3:
                metric_card("Recycling Rate", f"{recycle_ratio:.1f}", "% of Total Waste", "♻️")
            with col4:
                metric_card("Total Entries", str(len(df)), "Database Rows", "🗄️")
                
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("**Impact by Domain**")
                domain_data = df.groupby('scope')['emissions_kgCO2e'].sum().reset_index()
                if domain_data['emissions_kgCO2e'].sum() > 0:
                    fig1 = px.pie(domain_data, values='emissions_kgCO2e', names='scope', hole=0.4,
                                  color_discrete_sequence=['#2196F3', '#8D6E63', '#4CAF50'])
                    fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.info("Awaiting impactful data.")
                    
            with col_chart2:
                st.markdown("**Temporal Trend (Month over Month)**")
                df['month'] = df['date'].dt.strftime('%Y-%m')
                trend_data = df.groupby('month')['emissions_kgCO2e'].sum().reset_index()
                if len(trend_data) > 0:
                    fig2 = px.line(trend_data, x='month', y='emissions_kgCO2e', markers=True)
                    fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), xaxis_title="", yaxis_title="kgCO2e")
                    st.plotly_chart(fig2, use_container_width=True)

        # ==========================================
        # TAB 2: ENERGY ANALYTICS
        # ==========================================
        with tab2:
            if energy_df.empty:
                st.info("No Energy data logged.")
            else:
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    st.markdown("**Carbon Footprint by Source (kgCO2e)**")
                    e_emissions_data = energy_df.groupby('activity')['emissions_kgCO2e'].sum().reset_index()
                    # Filter out renewables so we only map the actual carbon offenders
                    dirty_energy = e_emissions_data[e_emissions_data['emissions_kgCO2e'] > 0]
                    
                    if not dirty_energy.empty:
                        fig3 = px.pie(dirty_energy, values='emissions_kgCO2e', names='activity', hole=0.4,
                                      color_discrete_sequence=['#F44336', '#FF9800', '#8D6E63'])
                        fig3.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                        st.plotly_chart(fig3, use_container_width=True)
                    else:
                        st.success("100% Clean Energy! No carbon footprint from power consumption.")
                with e_col2:
                    st.markdown("**Energy Transition Trajectory (Ternary Plot)**")
                    if 'date' in energy_df.columns and not energy_df.empty:
                        t_df = energy_df.copy()
                        t_df['month'] = pd.to_datetime(t_df['date']).dt.strftime('%Y-%m')
                        
                        # Map activities to the 3 Ternary Axes
                        def map_axis(activity):
                            if activity == 'Grid Electricity': return 'Grid (Traditional)'
                            elif activity == 'Diesel Generator': return 'Diesel (Off-Grid Fossil)'
                            else: return 'Clean (Solar/Wind)'
                            
                        t_df['axis'] = t_df['activity'].apply(map_axis)
                        
                        # Aggregate and calculate percentages
                        pivot_df = t_df.groupby(['month', 'axis'])['quantity'].sum().unstack(fill_value=0).reset_index()
                        
                        # Ensure all axes exist even if data is missing
                        for col in ['Grid (Traditional)', 'Diesel (Off-Grid Fossil)', 'Clean (Solar/Wind)']:
                            if col not in pivot_df.columns: pivot_df[col] = 0
                                
                        pivot_df['Total'] = pivot_df['Grid (Traditional)'] + pivot_df['Diesel (Off-Grid Fossil)'] + pivot_df['Clean (Solar/Wind)']
                        pivot_df = pivot_df[pivot_df['Total'] > 0] # Prevent division by zero
                        
                        # Normalize to 100%
                        pivot_df['Clean_%'] = (pivot_df['Clean (Solar/Wind)'] / pivot_df['Total']) * 100
                        pivot_df['Grid_%'] = (pivot_df['Grid (Traditional)'] / pivot_df['Total']) * 100
                        pivot_df['Diesel_%'] = (pivot_df['Diesel (Off-Grid Fossil)'] / pivot_df['Total']) * 100
                        
                        # Plot the triangle
                        if len(pivot_df) > 0:
                            fig_ternary = px.line_ternary(
                                pivot_df, 
                                a="Clean_%", 
                                b="Grid_%", 
                                c="Diesel_%",
                                hover_name="month", 
                                markers=True,
                                template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white"
                            )
                            fig_ternary.update_traces(line=dict(width=3, color='#4CAF50'), marker=dict(size=8))
                            fig_ternary.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                            st.plotly_chart(fig_ternary, use_container_width=True)
                        else:
                            st.info("Insufficient data to plot trajectory.")
                    else:
                        st.info("Awaiting temporal data.")

        # ==========================================
        # TAB 3: WASTE & LOGISTICS
        # ==========================================
        with tab3:
            w_col1, w_col2 = st.columns(2)
            with w_col1:
                st.markdown("**Waste Lifecycle Analysis**")
                if not waste_df.empty:
                    # Extract just the material name by stripping the method from the activity string
                    waste_df['material'] = waste_df['activity'].apply(lambda x: x.split(' (')[0])
                    fig5 = px.bar(waste_df, x='material', y='quantity', color='category', 
                                  title="Disposal Method by Material (kg)",
                                  color_discrete_map={'Recycled/Composted': '#4CAF50', 'Landfill': '#8D6E63'})
                    st.plotly_chart(fig5, use_container_width=True)
                else:
                    st.info("No Waste data logged.")
                    
            with w_col2:
                st.markdown("**Direct Carbon Footprint**")
                carbon_df = df[df['scope'] == 'Carbon Emissions']
                if not carbon_df.empty:
                    fig6 = px.bar(carbon_df, x='activity', y='emissions_kgCO2e', color='activity')
                    st.plotly_chart(fig6, use_container_width=True)
                else:
                    st.info("No Direct Carbon data logged.")

elif st.session_state.active_page == "Data Entry":
    st.markdown("<h1>Add New Sustainability Entry</h1>", unsafe_allow_html=True)
    
    # Global context for the manual entry session
    region = st.selectbox("Operating Region", ["India", "EU", "UK", "USA", "Japan", "China", "Other"])
    
    tabs = st.tabs(["Energy", "Waste", "Carbon", "CSV Upload"])
    
    # Dynamic defaults pulling from Settings
    cs = st.session_state.get('company_settings', {})
    defaults = {
        "business_unit": cs.get("company_name", "Main Office"), 
        "country": region, 
        "facility": cs.get("location", "HQ"), 
        "responsible_person": cs.get("contact_person", "Admin"), 
    }

    # ==========================================
    # TAB 1: ENERGY
    # ==========================================
    with tabs[0]:
        st.markdown("### Log Energy Consumption")
        e_date = st.date_input("Date", key="e_date")
        e_activity = st.selectbox("Energy Source", ["Grid Electricity", "Solar Power", "Wind Power", "Diesel Generator"])
        
        # Dynamic unit and factor routing
        if e_activity == "Diesel Generator":
            e_unit, e_cat = "Liters", "Non-Renewable (Fossil)"
            e_factor = 2.68 # Global constant for Diesel
        elif e_activity in ["Solar Power", "Wind Power"]:
            e_unit, e_cat = "kWh", "Renewable (Clean)"
            e_factor = 0.0 # Zero operational emissions
        else: 
            e_unit, e_cat = "kWh", "Non-Renewable (Fossil)"
            # Regional Grid Carbon Intensity (Approximate kgCO2e/kWh)
            grid_factors = {
                "India": 0.82, "China": 0.58, "Japan": 0.45, 
                "USA": 0.38, "EU": 0.23, "UK": 0.21, "Other": 0.45
            }
            e_factor = grid_factors.get(region, 0.45)
            
        e_qty = st.number_input(f"Quantity ({e_unit})", min_value=0.0, format="%.2f", key="e_qty")
        st.info(f"**GHG Protocol Factor:** {e_factor} kgCO2e/{e_unit}")
        
        if st.button("Log Energy Data", type="primary"):
            if add_emission_entry(e_date, defaults['business_unit'],"Energy Consumption", e_cat, e_activity, defaults['country'], defaults['facility'], defaults['responsible_person'], e_qty, e_unit, e_factor):
                st.success(f"Logged {e_qty} {e_unit} of {e_activity}!")

    # ==========================================
    # TAB 2: WASTE
    # ==========================================
    with tabs[1]:
        st.markdown("### Log Waste Management")
        w_date = st.date_input("Date", key="w_date")
        w_activity = st.selectbox("Waste Material", ["Organic Waste", "Plastic Packaging", "Paper/Cardboard", "E-Waste"])
        w_method = st.radio("Disposal Method", ["Landfill", "Recycled/Composted"])
        w_qty = st.number_input("Quantity (kg)", min_value=0.0, format="%.2f", key="w_qty")
        
        # Universal waste factors (kgCO2e/kg)
        w_factor = 0.0
        if w_method == "Landfill":
            factors = {"Organic Waste": 1.5, "Plastic Packaging": 0.05, "Paper/Cardboard": 0.5, "E-Waste": 0.1}
            w_factor = factors.get(w_activity, 0.0)
        else: # Recycled
            factors = {"Organic Waste": 0.1, "Plastic Packaging": 0.02, "Paper/Cardboard": 0.02, "E-Waste": 0.01}
            w_factor = factors.get(w_activity, 0.0)

        st.info(f"**GHG Protocol Factor:** {w_factor} kgCO2e/kg")
        
        if st.button("Log Waste Data", type="primary"):
            detailed_activity = f"{w_activity} ({w_method})"
            if add_emission_entry(w_date, defaults['business_unit'], "Waste Management", w_method, detailed_activity, defaults['country'], defaults['facility'], defaults['responsible_person'], w_qty, "kg", w_factor):
                st.success(f"Logged {w_qty}kg of {w_activity}!")

    # ==========================================
    # TAB 3: DIRECT CARBON
    # ==========================================
    with tabs[2]:
        st.markdown("### Log Direct Carbon Emissions")
        c_date = st.date_input("Date", key="c_date")
        c_activity = st.selectbox("Activity", ["Petrol Vehicle Commute", "EV Commute", "Business Flight", "AC Refrigerant Leak (R410a)"])
        
        # Dynamic unit and factor routing
        if c_activity == "AC Refrigerant Leak (R410a)":
            c_unit, c_factor = "kg", 2088.0
        elif c_activity == "EV Commute":
            c_unit, c_factor = "km", 0.0
        elif c_activity == "Business Flight":
            c_unit, c_factor = "km", 0.25
        else: # Petrol
            c_unit, c_factor = "km", 0.19
            
        c_qty = st.number_input(f"Quantity ({c_unit})", min_value=0.0, format="%.2f", key="c_qty")
        st.info(f"**GHG Protocol Factor:** {c_factor} kgCO2e/{c_unit}")
        
        if st.button("Log Carbon Data", type="primary"):
            if add_emission_entry(c_date, defaults['business_unit'], "Carbon Emissions", "Direct Emission", c_activity, defaults['country'], defaults['facility'], defaults['responsible_person'], c_qty, c_unit, c_factor):
                st.success(f"Logged {c_activity}!")

    # ==========================================
    # TAB 4: CSV UPLOAD
    # ==========================================
    with tabs[3]:
        st.markdown("### Bulk Data Upload")
        st.warning("Ensure your CSV includes the legally correct `emission_factor` for your operating region. The system will trust your uploaded math.")
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file is not None:
            if st.button("Process CSV", type="primary"):
                process_csv(uploaded_file)

    # ==========================================
    # DATA VIEWER & DELETION CONTROLS
    # ==========================================
    st.divider()
    st.markdown("### Logged Database Entries")
    
    if len(st.session_state.emissions_data) > 0:
        # Display the table
        display_df = st.session_state.emissions_data.copy()
        st.dataframe(display_df, use_container_width=True)
        
        # Deletion controls
        st.markdown("#### Delete an Entry")
        max_idx = len(st.session_state.emissions_data) - 1
        
        # Database Management Controls
        col_del1, col_del2, col_del3 = st.columns([1, 1, 2])
        with col_del1:
            start_idx = st.number_input("From Row", min_value=0, max_value=max_idx, value=0, step=1)
        with col_del2:
            end_idx = st.number_input("To Row", min_value=0, max_value=max_idx, value=0, step=1)
        with col_del3:
            st.markdown("<br>", unsafe_allow_html=True) # alignment spacer
            if st.button("🗑️ Delete Selected Range", type="primary", use_container_width=True):
                if start_idx > end_idx:
                    st.error("Basic math failure: 'From' index cannot be greater than 'To' index.")
                else:
                    df = st.session_state.emissions_data
                    indices_to_drop = list(range(start_idx, end_idx + 1))
                    
                    # Drop the specific rows and re-index so numbers stay sequential
                    st.session_state.emissions_data = df.drop(indices_to_drop, errors='ignore').reset_index(drop=True)
                    save_emissions_data()
                    
                    st.success(f"Purged rows {start_idx} through {end_idx}.")
                    st.rerun()
    else:
        st.info("Database is currently empty. Add entries above or upload a CSV.")

elif st.session_state.active_page == "Settings":
    st.markdown("<h1>System Configuration</h1>", unsafe_allow_html=True)
    
    # Initialize settings in session state if missing
    if 'company_settings' not in st.session_state:
        try:
            with open('data/settings.json', 'r') as f:
                st.session_state.company_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            st.session_state.company_settings = {
                "company_name": "", "industry": "", "location": "",
                "contact_person": "", "email": "", "phone": "",
                "export_eu": False, "export_japan": False, "export_usa": False
            }
            
    cs = st.session_state.company_settings

    st.markdown("<h3>Enterprise Context</h3>", unsafe_allow_html=True)
    st.info("These settings act as global defaults for database entries and provide context for the AI Insights engine.")
        
    with st.form("company_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", value=cs.get("company_name", ""))
            industry = st.text_input("Industry Sector", value=cs.get("industry", ""))
            location = st.text_input("Primary Facility Location", value=cs.get("location", ""))
        with col2:
            contact_person = st.text_input("Responsible Data Officer", value=cs.get("contact_person", ""))
            email = st.text_input("Contact Email", value=cs.get("email", ""))
            phone = st.text_input("Contact Phone", value=cs.get("phone", ""))
        
        st.markdown("<h4>Target Export Markets</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            export_eu = st.checkbox("European Union (CBAM Compliance)", value=cs.get("export_eu", False))
        with col2:
            export_japan = st.checkbox("Japan", value=cs.get("export_japan", False))
        with col3:
            export_usa = st.checkbox("United States", value=cs.get("export_usa", False))
        
        if st.form_submit_button("Save Global Configuration", type="primary"):
            # Update session state
            st.session_state.company_settings = {
                "company_name": company_name, "industry": industry, "location": location,
                "contact_person": contact_person, "email": email, "phone": phone,
                "export_eu": export_eu, "export_japan": export_japan, "export_usa": export_usa
            }
            # Save to disk
            os.makedirs('data', exist_ok=True)
            with open('data/settings.json', 'w') as f:
                json.dump(st.session_state.company_settings, f, indent=2)
            st.success("Configuration locked and saved to database.")

elif st.session_state.active_page == "AI Insights":
    st.markdown(f"<h1>🤖 AI Insights</h1>", unsafe_allow_html=True)
    
    # Import AI agents
    from ai_agents import CarbonFootprintAgents
    
    # Initialize AI agents
    if 'ai_agents' not in st.session_state:
        st.session_state.ai_agents = CarbonFootprintAgents()
    
    # Create tabs for different AI insights
    ai_tabs = st.tabs(["Data Assistant", "Report Summary", "Offset Advisor", "Regulation Radar", "Emission Optimizer"])
    
    with ai_tabs[0]:
        st.markdown("<h3>Data Entry Assistant</h3>", unsafe_allow_html=True)
        st.markdown("Get help with classifying emissions and mapping them to the correct scope.")
        
        data_description = st.text_area("Describe your emission activity", 
                                      placeholder="Example: We use diesel generators for backup power at our office in Mumbai. How should I categorize this?")
        
        if st.button("Get Assistance", key="data_assistant_btn"):
            if data_description:
                with st.spinner("AI assistant is analyzing your request..."):
                    try:
                        result = st.session_state.ai_agents.run_data_entry_crew(data_description)
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
            else:
                st.warning("Please describe your emission activity first.")
    
    with ai_tabs[1]:
        st.markdown("<h3>Report Summary Generator</h3>", unsafe_allow_html=True)
        st.markdown("Generate a human-readable summary of your emissions data.")
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            if st.button("Generate Summary", key="report_summary_btn"):
                with st.spinner("Generating report summary..."):
                    try:
                        # Convert DataFrame to string representation for the AI
                        emissions_str = st.session_state.emissions_data.to_string()
                        result = st.session_state.ai_agents.run_report_summary_crew(emissions_str)
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
    
    with ai_tabs[2]:
        st.markdown("<h3>Carbon Offset Advisor</h3>", unsafe_allow_html=True)
        st.markdown("Get recommendations for verified carbon offset options based on your profile.")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location", placeholder="e.g., Mumbai, India")
            industry = st.selectbox("Industry", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"])
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            total_emissions = st.session_state.emissions_data['emissions_kgCO2e'].sum()
            st.markdown(f"<p>Total emissions to offset: <strong>{total_emissions:.2f} kgCO2e</strong></p>", unsafe_allow_html=True)
            
            if st.button("Get Offset Recommendations", key="offset_advisor_btn"):
                if location:
                    with st.spinner("Finding offset options..."):
                        try:
                            result = st.session_state.ai_agents.run_offset_advice_crew(total_emissions, location, industry)
                            # Handle CrewOutput object by converting it to string
                            result_str = str(result)
                            st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}. Please check your API key and try again.")
                else:
                    st.warning("Please enter your location.")
    
    with ai_tabs[3]:
        st.markdown("<h3>Regulation Radar</h3>", unsafe_allow_html=True)
        st.markdown("Get insights on current and upcoming carbon regulations relevant to your business.")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Company Location", placeholder="e.g., Jakarta, Indonesia", key="reg_location")
            industry = st.selectbox("Industry Sector", ["Manufacturing", "Technology", "Agriculture", "Transportation", "Energy", "Services", "Other"], key="reg_industry")
        with col2:
            export_markets = st.multiselect("Export Markets", ["European Union", "Japan", "United States", "China", "Indonesia", "India", "Other"])
        
        if st.button("Check Regulations", key="regulation_radar_btn"):
            if location and len(export_markets) > 0:
                with st.spinner("Analyzing regulatory requirements..."):
                    try:
                        result = st.session_state.ai_agents.run_regulation_check_crew(location, industry, ", ".join(export_markets))
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
            else:
                st.warning("Please enter your location and select at least one export market.")
    
    with ai_tabs[4]:
        st.markdown("<h3>Emission Optimizer</h3>", unsafe_allow_html=True)
        st.markdown("Get AI-powered recommendations to reduce your carbon footprint.")
        
        if len(st.session_state.emissions_data) == 0:
            st.warning("No emissions data available. Please add data first.")
        else:
            if st.button("Generate Optimization Recommendations", key="emission_optimizer_btn"):
                with st.spinner("Analyzing your emissions data..."):
                    try:
                        # Convert DataFrame to string representation for the AI
                        emissions_str = st.session_state.emissions_data.to_string()
                        result = st.session_state.ai_agents.run_optimization_crew(emissions_str)
                        # Handle CrewOutput object by converting it to string
                        result_str = str(result)
                        st.markdown(f"<div class='stCard'>{result_str}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}. Please check your API key and try again.")
