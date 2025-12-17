import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

PLOT_CONFIG = {"displayModeBar": False}

COLORS = {
    'dark_blue': '#0173B2',      
    'orange': '#DE8F05',        
    'sky_blue': '#56B4E9',       
    'blue_green': '#029E73',     
    'yellow': '#ECE133',         
    'vermillion': '#D55E00',     
    'reddish_purple': '#CC78BC', 
    'dark_grey': '#6B6B6B',      
    
    # Sidebar colors
    'sidebar_navy': '#003B7A',
    'sidebar_gold': '#FDB913',
    'sidebar_dark': '#002A5C',
    'sidebar_border': '#004B9B',
    'sidebar_text': '#E0E7F0',
}

st.set_page_config(
    page_title="Warehouse Operations Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global font family */
    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Main background */
    .main {
        background-color: #F5F7FA;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Header styling */
    h1 {
        color: #2C3E50;
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 5px;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    h2 {
        color: #2C3E50;
        font-size: 18px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 12px;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    h3 {
        color: #2C3E50;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Text elements */
    p, div, span, label, input, select, textarea {
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        font-family: "Times New Roman", Times, serif !important;
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 11px !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Sidebar styling - ATS Group Colors (KEPT AS REQUESTED) */
    [data-testid="stSidebar"] {
        background-color: #003B7A !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #003B7A !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #E0E7F0 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Multiselect chip styling - ATS Gold (KEPT AS REQUESTED) */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #FDB913 !important;
        border: 1px solid #FDB913 !important;
        border-radius: 16px !important;
        padding: 4px 12px !important;
        color: #003B7A !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="tag"] svg {
        color: #003B7A !important;
        font-weight: 700 !important;
    }
    
    /* Multiselect container */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background-color: #002A5C !important;
        border: 1px solid #004B9B !important;
        border-radius: 8px !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #002A5C !important;
        color: #FFFFFF !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Dropdown arrow */
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        color: #E0E7F0 !important;
    }
    
    /* Placeholder text */
    [data-testid="stSidebar"] [data-baseweb="select"] input::placeholder {
        color: #8C9DB5 !important;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Radio button styling for sidebar */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        background-color: #002A5C !important;
        border: 1px solid #004B9B !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #E0E7F0 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        font-size: 13px;
        font-family: "Times New Roman", Times, serif !important;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Hide Streamlit sidebar toggle button */
    [data-testid="stSidebarToggleButton"] {
        display: none !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        infeed = pd.read_csv("infeed_6.csv")
        outfeed = pd.read_csv("outfeed_6.csv")
        transfer = pd.read_csv("transfer_6.csv")
        stock = pd.read_csv("stock.csv")
        return infeed, outfeed, transfer, stock
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

def calculate_duration(df, start_date_col, start_time_col, end_date_col, end_time_col):
    """Calculate mission duration in minutes"""
    df = df.copy()
    try:
        # Combine date and time columns
        df['start_datetime'] = pd.to_datetime(
            df[start_date_col].astype(str) + ' ' + df[start_time_col].astype(str),
            format='%d-%m-%Y %H:%M:%S',
            errors='coerce'
        )
        df['end_datetime'] = pd.to_datetime(
            df[end_date_col].astype(str) + ' ' + df[end_time_col].astype(str),
            format='%d-%m-%Y %H:%M:%S',
            errors='coerce'
        )
        
        # Calculate duration in minutes
        df['duration_minutes'] = (df['end_datetime'] - df['start_datetime']).dt.total_seconds() / 60
        
    except Exception as e:
        df['duration_minutes'] = np.nan
    
    return df

def classify_outlier_reason(duration):
    """Classify the reason for outlier"""
    if pd.isna(duration):
        return None
    elif duration < 0:
        return 'Negative Duration'
    elif duration > 3:
        return 'More than 3 mins'
    else:
        return None

infeed_df, outfeed_df, transfer_df, stock_df = load_data()

if infeed_df is None:
    st.stop()

# Calculate durations for all dataframes
infeed_df = calculate_duration(infeed_df, 'INFEED_MISSION_START_DATE', 'INFEED_MISSION_START_TIME', 
                                'INFEED_MISSION_END_DATE', 'INFEED_MISSION_END_TIME')
outfeed_df = calculate_duration(outfeed_df, 'OUTFEED_MISSION_START_DATE', 'OUTFEED_MISSION_START_TIME',
                                 'OUTFEED_MISSION_END_DATE', 'OUTFEED_MISSION_END_TIME')
transfer_df = calculate_duration(transfer_df, 'TRANSFER_MISSION_START_DATE', 'TRANSFER_MISSION_START_TIME',
                                  'TRANSFER_MISSION_END_DATE', 'TRANSFER_MISSION_END_TIME')

# Standardize mission status values to uppercase for consistent grouping
infeed_df['INFEED_MISSION_STATUS'] = infeed_df['INFEED_MISSION_STATUS'].str.upper()
outfeed_df['OUTFEED_MISSION_STATUS'] = outfeed_df['OUTFEED_MISSION_STATUS'].str.upper()
transfer_df['TRANSFER_MISSION_STATUS'] = transfer_df['TRANSFER_MISSION_STATUS'].str.upper()

# Add outlier reason classification
infeed_df['outlier_reason'] = infeed_df['duration_minutes'].apply(classify_outlier_reason)
outfeed_df['outlier_reason'] = outfeed_df['duration_minutes'].apply(classify_outlier_reason)
transfer_df['outlier_reason'] = transfer_df['duration_minutes'].apply(classify_outlier_reason)

stock_df = stock_df[
    (stock_df['PRODUCT_NAME'].notna()) & 
    (stock_df['PRODUCT_NAME'] != 'NA') &
    (stock_df['PALLET_STATUS_NAME'].notna()) &
    (stock_df['PALLET_STATUS_NAME'] != 'NA') &
    (stock_df['PALLET_STATUS_NAME'].isin(['FULL', 'EMPTY']))
].copy()

stock_df['AGEING_DAYS'] = pd.to_numeric(stock_df['AGEING_DAYS'], errors='coerce').fillna(0)

st.sidebar.image("ats_logo.png", use_container_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="padding: 10px 0;">
    <h2 style="color: white; font-size: 24px; font-weight: 700; display: flex; align-items: center; gap: 8px;">
        🔍 Filters
    </h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<p style="color: #E0E7F0; font-size: 12px; font-weight: 600; text-transform: uppercase; 
          letter-spacing: 0.5px; margin-bottom: 8px; margin-top: 20px;">
    Select Months
</p>
""", unsafe_allow_html=True)

selected_months = st.sidebar.multiselect(
    "",
    options=['2025-11', '2025-10', '2025-09', '2025-08', '2025-07', '2025-06', '2025-05'],
    default=[],
    key='months',
    label_visibility='collapsed'
)

st.sidebar.markdown("""
<p style="color: #E0E7F0; font-size: 12px; font-weight: 600; text-transform: uppercase; 
          letter-spacing: 0.5px; margin-bottom: 8px; margin-top: 20px;">
    Select Mission Type
</p>
""", unsafe_allow_html=True)

selected_mission_types = st.sidebar.multiselect(
    "",
    options=['infeed', 'outfeed', 'transfer'],
    default=[],
    key='mission_types',
    label_visibility='collapsed'
)

st.sidebar.markdown("""
<p style="color: #E0E7F0; font-size: 12px; font-weight: 600; text-transform: uppercase; 
          letter-spacing: 0.5px; margin-bottom: 8px; margin-top: 20px;">
    Mission Status
</p>
""", unsafe_allow_html=True)

selected_statuses = st.sidebar.multiselect(
    "",
    options=['COMPLETED', 'ABORT'],
    default=[],
    key='statuses',
    label_visibility='collapsed'
)


st.sidebar.markdown("""
<p style="color: #E0E7F0; font-size: 12px; font-weight: 600; text-transform: uppercase; 
          letter-spacing: 0.5px; margin-bottom: 8px; margin-top: 20px;">
    Outlier Analysis
</p>
""", unsafe_allow_html=True)

outlier_option = st.sidebar.radio(
    "",
    options=['BOTH', 'Outlier Missions', 'Normal Missions'],
    index=0,
    key='outlier_filter',
    label_visibility='collapsed',
    help="Outliers: missions > 3 minutes or negative duration"
)

# Create filtered versions for KPIs
infeed_filtered = infeed_df.copy()
outfeed_filtered = outfeed_df.copy()
transfer_filtered = transfer_df.copy()

if selected_mission_types:
    if 'infeed' not in selected_mission_types:
        infeed_filtered = pd.DataFrame(columns=infeed_filtered.columns)
    if 'outfeed' not in selected_mission_types:
        outfeed_filtered = pd.DataFrame(columns=outfeed_filtered.columns)
    if 'transfer' not in selected_mission_types:
        transfer_filtered = pd.DataFrame(columns=transfer_filtered.columns)

if selected_statuses:
    infeed_filtered = infeed_filtered[infeed_filtered['INFEED_MISSION_STATUS'].isin(selected_statuses)]
    outfeed_filtered = outfeed_filtered[outfeed_filtered['OUTFEED_MISSION_STATUS'].isin(selected_statuses)]
    transfer_filtered = transfer_filtered[transfer_filtered['TRANSFER_MISSION_STATUS'].isin(selected_statuses)]


if selected_months:
    def filter_by_month(df, date_column):
        if date_column not in df.columns:
            return df
        df_copy = df.copy()
        df_copy['year_month'] = pd.to_datetime(df_copy[date_column], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m')
        return df_copy[df_copy['year_month'].isin(selected_months)]
    
    infeed_filtered = filter_by_month(infeed_filtered, 'INFEED_MISSION_CDATE')
    outfeed_filtered = filter_by_month(outfeed_filtered, 'OUTFEED_MISSION_CDATE')
    transfer_filtered = filter_by_month(transfer_filtered, 'CDATE')

# Apply outlier filter
def apply_outlier_filter(df, option):
    """
    Apply outlier filter based on duration
    Outliers: duration > 3 minutes OR duration < 0
    """
    if option == 'BOTH':
        return df
    elif option == 'Outlier Missions':
        # Show ONLY outliers
        return df[(df['duration_minutes'] > 3) | (df['duration_minutes'] < 0)]
    elif option == 'Normal Missions':
        # Show WITHOUT outliers
        return df[(df['duration_minutes'] <= 3) & (df['duration_minutes'] >= 0)]
    return df

infeed_filtered = apply_outlier_filter(infeed_filtered, outlier_option)
outfeed_filtered = apply_outlier_filter(outfeed_filtered, outlier_option)
transfer_filtered = apply_outlier_filter(transfer_filtered, outlier_option)

all_products = sorted(list(set(
    list(infeed_df['PRODUCT_NAME'].dropna().unique()) +
    list(outfeed_df['PRODUCT_NAME'].dropna().unique()) +
    list(transfer_df['PRODUCT_NAME'].dropna().unique()) +
    list(stock_df['PRODUCT_NAME'].dropna().unique())
)))
all_products = [p for p in all_products if p != 'NA']

# ========== KPI CALCULATIONS (Using filtered data) ==========

# Determine which data to use based on outlier filter
if outlier_option == 'Outlier Missions':
    # Use only outliers for KPI calculations
    infeed_for_kpi = infeed_filtered[infeed_filtered['outlier_reason'].notna()].copy()
    outfeed_for_kpi = outfeed_filtered[outfeed_filtered['outlier_reason'].notna()].copy()
    transfer_for_kpi = transfer_filtered[transfer_filtered['outlier_reason'].notna()].copy()
elif outlier_option == 'Normal Missions':
    # Use only non-outliers
    infeed_for_kpi = infeed_filtered[infeed_filtered['outlier_reason'].isna()].copy()
    outfeed_for_kpi = outfeed_filtered[outfeed_filtered['outlier_reason'].isna()].copy()
    transfer_for_kpi = transfer_filtered[transfer_filtered['outlier_reason'].isna()].copy()
else:  # BOTH
    # Use all data
    infeed_for_kpi = infeed_filtered.copy()
    outfeed_for_kpi = outfeed_filtered.copy()
    transfer_for_kpi = transfer_filtered.copy()

infeed_completed = len(infeed_for_kpi[infeed_for_kpi['INFEED_MISSION_STATUS'] == 'COMPLETED'])
infeed_total = len(infeed_for_kpi)
outfeed_completed = len(outfeed_for_kpi[outfeed_for_kpi['OUTFEED_MISSION_STATUS'] == 'COMPLETED'])
outfeed_total = len(outfeed_for_kpi)

infeed_uptime = (infeed_completed / infeed_total * 100) if infeed_total > 0 else 0
infeed_downtime = 100 - infeed_uptime
outfeed_uptime = (outfeed_completed / outfeed_total * 100) if outfeed_total > 0 else 0
outfeed_downtime = 100 - outfeed_uptime

total_missions = infeed_total + outfeed_total + len(transfer_for_kpi)
completed_missions = (
    infeed_completed + 
    outfeed_completed + 
    len(transfer_for_kpi[transfer_for_kpi['TRANSFER_MISSION_STATUS'] == 'COMPLETED'])
)
completion_rate = (completed_missions / total_missions * 100) if total_missions > 0 else 0

# Calculate actual average duration from KPI data
all_durations = pd.concat([
    infeed_for_kpi['duration_minutes'],
    outfeed_for_kpi['duration_minutes'],
    transfer_for_kpi['duration_minutes']
]).dropna()
avg_duration = all_durations.mean() if len(all_durations) > 0 else 0

active_products = len(set(
    list(infeed_for_kpi['PRODUCT_NAME'].dropna()) +
    list(outfeed_for_kpi['PRODUCT_NAME'].dropna()) +
    list(transfer_for_kpi['PRODUCT_NAME'].dropna())
))

areas_covered = len(transfer_for_kpi['AREA_ID'].dropna().unique())

total_pallets = len(stock_df)
full_pallets = len(stock_df[stock_df['PALLET_STATUS_NAME'] == 'FULL'])
empty_pallets = len(stock_df[stock_df['PALLET_STATUS_NAME'] == 'EMPTY'])
high_ageing = len(stock_df[stock_df['AGEING_DAYS'] < 30])

# ========== DASHBOARD TABS ==========

st.title("ATS Mahindra Cell Dashboard")
st.markdown("---")

# Custom CSS for better tab styling (light theme friendly)
st.markdown("""
<style>
    /* Tab container */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 10px 0px;
        border-bottom: 2px solid #E0E0E0;
    }
    
    /* Individual tabs */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F5F5F5;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 16px;
        font-weight: 600;
        color: #333333;
        border: 2px solid #E0E0E0;
        border-bottom: none;
        transition: all 0.3s ease;
    }
    
    /* Tab hover effect */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #FFFFFF;
        border-color: #FDB913;
        border-bottom: none;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(253, 185, 19, 0.3);
    }
    
    /* Active/selected tab */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #003B7A 0%, #0056A8 100%);
        border: 2px solid #FDB913;
        border-bottom: 4px solid #FDB913;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0, 59, 122, 0.4);
    }
    
    /* Tab panel */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 30px;
        background-color: white;
    }
    
    /* Make tab text more visible */
    button[data-baseweb="tab"] > div > p {
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Fix sidebar radio button text visibility - make text white on navy background */
    [data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stRadio p {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] label[data-baseweb="radio"] span {
        color: #FFFFFF !important;
    }
    
    /* Ensure radio button circles are visible */
    [data-testid="stSidebar"] .stRadio [role="radio"] {
        border-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== CREATE TABS ==========
tab1, tab2, tab3, tab4 = st.tabs(["📊 System Health", "🚀 Missions", "⚠️ Outlier Missions", "📦 Stock Dashboard"])

# ========== TAB 1: SYSTEM HEALTH ==========
with tab1:
    st.subheader("System Health Overview")
    
    # Show indicator if outlier filter is active
    if outlier_option == 'Outlier Missions':
        st.info("⚠️ Showing metrics for OUTLIERS only (missions >3 mins or negative duration)")
    elif outlier_option == 'Normal Missions':
        st.success("✅ Showing metrics for NORMAL missions only (≤3 mins and ≥0)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, #015A8A 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Infeed Uptime</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700; margin-bottom: 4px;">{infeed_uptime:.2f}%</div>
            <div style="color: rgba(255,255,255,0.95); font-size: 11px;">↑ +2.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['sky_blue']} 0%, #3A9BD6 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Infeed Downtime</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700; margin-bottom: 4px;">{infeed_downtime:.2f}%</div>
            <div style="color: rgba(255,255,255,0.95); font-size: 11px;">↓ -1.2%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['orange']} 0%, #C57A04 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Outfeed Uptime</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700; margin-bottom: 4px;">{outfeed_uptime:.2f}%</div>
            <div style="color: rgba(255,255,255,0.95); font-size: 11px;">↑ +3.1%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['vermillion']} 0%, #B34D00 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Outfeed Downtime</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700; margin-bottom: 4px;">{outfeed_downtime:.2f}%</div>
            <div style="color: rgba(255,255,255,0.95); font-size: 11px;">↓ -0.8%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Monthly Performance Trends
    st.subheader("Monthly Performance Trends")
    
    # Prepare monthly data for infeed
    infeed_df_copy = infeed_df.copy()
    infeed_df_copy['month'] = pd.to_datetime(infeed_df_copy['INFEED_MISSION_CDATE'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m')
    
    # Prepare monthly data for outfeed
    outfeed_df_copy = outfeed_df.copy()
    outfeed_df_copy['month'] = pd.to_datetime(outfeed_df_copy['OUTFEED_MISSION_CDATE'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m')
    
    # Calculate monthly metrics for infeed
    infeed_monthly = infeed_df_copy.groupby('month').agg(
        total=('INFEED_MISSION_STATUS', 'count'),
        completed=('INFEED_MISSION_STATUS', lambda x: (x == 'COMPLETED').sum())
    ).reset_index()
    infeed_monthly['uptime'] = (infeed_monthly['completed'] / infeed_monthly['total'] * 100).round(2)
    infeed_monthly['downtime'] = (100 - infeed_monthly['uptime']).round(2)
    infeed_monthly['downtime_log'] = infeed_monthly['downtime'].apply(lambda x: max(x, 0.01))
    infeed_monthly = infeed_monthly.sort_values('month')
    
    # Calculate monthly metrics for outfeed
    outfeed_monthly = outfeed_df_copy.groupby('month').agg(
        total=('OUTFEED_MISSION_STATUS', 'count'),
        completed=('OUTFEED_MISSION_STATUS', lambda x: (x == 'COMPLETED').sum())
    ).reset_index()
    outfeed_monthly['uptime'] = (outfeed_monthly['completed'] / outfeed_monthly['total'] * 100).round(2)
    outfeed_monthly['downtime'] = (100 - outfeed_monthly['uptime']).round(2)
    outfeed_monthly['downtime_log'] = outfeed_monthly['downtime'].apply(lambda x: max(x, 0.01))
    outfeed_monthly = outfeed_monthly.sort_values('month')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Infeed Downtime by Month**")
        
        fig_infeed_trend = go.Figure()
        
        # Add lollipop stems
        min_val = 0.01
        for idx, row in infeed_monthly.iterrows():
            fig_infeed_trend.add_trace(go.Scatter(
                x=[row['month'], row['month']],
                y=[min_val, row['downtime_log']],
                mode='lines',
                line=dict(color=COLORS['dark_grey'], width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add lollipop heads
        fig_infeed_trend.add_trace(go.Scatter(
            x=infeed_monthly['month'],
            y=infeed_monthly['downtime_log'],
            mode='markers+text',
            marker=dict(
                size=14,
                color=COLORS['vermillion'],
                line=dict(color='white', width=2)
            ),
            text=[f"{val:.2f}%" for val in infeed_monthly['downtime']],
            textposition='top center',
            textfont=dict(size=10, color='#333'),
            name='Downtime',
            hovertemplate='%{x}<br>Downtime: %{text}<extra></extra>'
        ))
        
        fig_infeed_trend.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=60),
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(showgrid=False, title='Month', tickangle=-45),
            yaxis=dict(type='log', showgrid=True, gridcolor='#E0E0E0', 
                      title='Downtime % (Log Scale)', tickformat='.2f'),
            showlegend=False,
            font=dict(family="Times New Roman, Times, serif", size=11)
        )
        
        st.plotly_chart(fig_infeed_trend, use_container_width=True, config=PLOT_CONFIG)
    with col2:
        st.markdown("**Outfeed Downtime by Month**")
        
        fig_outfeed_trend = go.Figure()
        
        # Add lollipop stems
        min_val = 0.01
        for idx, row in outfeed_monthly.iterrows():
            fig_outfeed_trend.add_trace(go.Scatter(
                x=[row['month'], row['month']],
                y=[min_val, row['downtime_log']],
                mode='lines',
                line=dict(color=COLORS['dark_grey'], width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add lollipop heads
        fig_outfeed_trend.add_trace(go.Scatter(
            x=outfeed_monthly['month'],
            y=outfeed_monthly['downtime_log'],
            mode='markers+text',
            marker=dict(
                size=14,
                color=COLORS['vermillion'],
                line=dict(color='white', width=2)
            ),
            text=[f"{val:.2f}%" for val in outfeed_monthly['downtime']],
            textposition='top center',
            textfont=dict(size=10, color='#333'),
            name='Downtime',
            hovertemplate='%{x}<br>Downtime: %{text}<extra></extra>'
        ))
        
        fig_outfeed_trend.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=60),
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(showgrid=False, title='Month', tickangle=-45),
            yaxis=dict(type='log', showgrid=True, gridcolor='#E0E0E0', 
                      title='Downtime % (Log Scale)', tickformat='.2f'),
            showlegend=False,
            font=dict(family="Times New Roman, Times, serif", size=11)
        )
        
        st.plotly_chart(fig_outfeed_trend, use_container_width=True, config=PLOT_CONFIG)

# ========== TAB 2: MISSIONS ==========
with tab2:
    st.subheader("Mission Performance")
    
    # Show indicator if outlier filter is active
    if outlier_option == 'Outlier Missions':
        st.info("⚠️ Showing metrics for OUTLIERS only (missions >3 mins or negative duration)")
    elif outlier_option == 'Normal Missions':
        st.success("✅ Showing metrics for NORMAL missions only (≤3 mins and ≥0)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, #015A8A 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Total Missions</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{total_missions:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['blue_green']} 0%, #027859 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Completion Rate</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{completion_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['sky_blue']} 0%, #3A9BD6 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Avg Duration</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{avg_duration:.2f}m</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['reddish_purple']} 0%, #B565A7 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Active Products</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{active_products}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Mission Charts - use KPI data which respects outlier filter
    st.subheader("Mission Status Overview")
    
    all_missions_for_charts = pd.concat([
        infeed_for_kpi[['INFEED_MISSION_STATUS']].rename(columns={'INFEED_MISSION_STATUS': 'STATUS'}),
        outfeed_for_kpi[['OUTFEED_MISSION_STATUS']].rename(columns={'OUTFEED_MISSION_STATUS': 'STATUS'}),
        transfer_for_kpi[['TRANSFER_MISSION_STATUS']].rename(columns={'TRANSFER_MISSION_STATUS': 'STATUS'})
    ])
    
    status_counts = all_missions_for_charts['STATUS'].value_counts()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown("**i. Mission Status Distribution**")
        fig_status = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            marker=dict(colors=[COLORS['blue_green'], COLORS['vermillion']]),
            hole=0,
            textinfo='label+percent'
        )])
        fig_status.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False,
            font=dict(family="Times New Roman, Times, serif", size=12)
        )
        st.plotly_chart(fig_status, use_container_width=True, config=PLOT_CONFIG)
    
    with col2:
        st.markdown("**ii. Mission Type Distribution**")
        mission_types = pd.DataFrame({
            'Type': ['Infeed', 'Outfeed', 'Transfer'],
            'Count': [len(infeed_for_kpi), len(outfeed_for_kpi), len(transfer_for_kpi)]
        })
        fig_types = go.Figure(data=[go.Pie(
            labels=mission_types['Type'],
            values=mission_types['Count'],
            marker=dict(colors=[COLORS['dark_blue'], COLORS['orange'], COLORS['reddish_purple']]),
            hole=0.5,
            textinfo='label+percent'
        )])
        fig_types.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False,
            font=dict(family="Times New Roman, Times, serif", size=12)
        )
        st.plotly_chart(fig_types, use_container_width=True, config=PLOT_CONFIG)
    
    with col3:
        st.markdown("**iii. Mission Count by Product and Type**")
        
        product_type_data = []
        for product in all_products[:10]:
            infeed_count = len(infeed_for_kpi[infeed_for_kpi['PRODUCT_NAME'] == product])
            outfeed_count = len(outfeed_for_kpi[outfeed_for_kpi['PRODUCT_NAME'] == product])
            transfer_count = len(transfer_for_kpi[transfer_for_kpi['PRODUCT_NAME'] == product])
            if infeed_count + outfeed_count + transfer_count > 0:
                product_type_data.append({
                    'Product': product,
                    'Infeed': infeed_count,
                    'Outfeed': outfeed_count,
                    'Transfer': transfer_count
                })
        
        product_df = pd.DataFrame(product_type_data)
        
        if len(product_df) > 0:
            fig_product_type = go.Figure()
            fig_product_type.add_trace(go.Bar(name='Infeed', x=product_df['Product'], y=product_df['Infeed'], 
                                             marker_color=COLORS['dark_blue']))
            fig_product_type.add_trace(go.Bar(name='Outfeed', x=product_df['Product'], y=product_df['Outfeed'], 
                                             marker_color=COLORS['orange']))
            fig_product_type.add_trace(go.Bar(name='Transfer', x=product_df['Product'], y=product_df['Transfer'], 
                                             marker_color=COLORS['reddish_purple']))
            
            fig_product_type.update_layout(
                barmode='group',
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='white',
                plot_bgcolor='white',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                font=dict(family="Times New Roman, Times, serif", size=12)
            )
            st.plotly_chart(fig_product_type, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info("No data available for this filter")

# ========== TAB 3: OUTLIER ANALYSIS ==========
with tab3:
    st.subheader("Outlier Distribution Analysis")
    
    # ALWAYS show outliers in this tab (don't check outlier_option)
    # Get ALL outliers from unfiltered data (but respect other filters)
    all_outliers_infeed = infeed_filtered[infeed_filtered['outlier_reason'].notna()].copy()
    all_outliers_outfeed = outfeed_filtered[outfeed_filtered['outlier_reason'].notna()].copy()
    all_outliers_transfer = transfer_filtered[transfer_filtered['outlier_reason'].notna()].copy()
    
    # ALWAYS use UNFILTERED total for percentage calculation
    total_all_missions_unfiltered = len(infeed_df) + len(outfeed_df) + len(transfer_df)
    
    # Combine all outlier reasons
    all_outlier_reasons = pd.concat([
        all_outliers_infeed['outlier_reason'],
        all_outliers_outfeed['outlier_reason'],
        all_outliers_transfer['outlier_reason']
    ]).dropna()
    
    if len(all_outlier_reasons) > 0:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Outlier Reason Distribution**")
            
            reason_counts = all_outlier_reasons.value_counts()
            
            # Calculate percentages relative to UNFILTERED total
            reason_percentages = (reason_counts / total_all_missions_unfiltered * 100).round(1)
            
            # Create custom labels
            custom_labels = [f"{label}<br>{pct}%" 
                            for label, pct in zip(reason_counts.index, reason_percentages.values)]
            
            fig_outlier_reasons = go.Figure(data=[go.Pie(
                labels=custom_labels,
                values=reason_counts.values,
                marker=dict(colors=[COLORS['vermillion'], COLORS['orange']]),
                hole=0.4,
                textposition='inside',
                textinfo='label+value',
                hovertemplate='%{label}<br>%{value} missions<extra></extra>',
                showlegend=True
            )])
            
            fig_outlier_reasons.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='white',
                plot_bgcolor='white',
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=-0.2,
                    xanchor='center',
                    x=0.5,
                    title=None
                ),
                font=dict(family="Times New Roman, Times, serif", size=12)
            )
            
            st.plotly_chart(fig_outlier_reasons, use_container_width=True, config=PLOT_CONFIG)
        
        with col2:
            st.markdown("**All Outliers**")
            
            # Combine all outliers into one table
            outlier_table_data = []
            
            for idx, row in all_outliers_infeed.iterrows():
                outlier_table_data.append({
                    'Type': 'Infeed',
                    'Product': row['PRODUCT_NAME'],
                    'Status': row['INFEED_MISSION_STATUS'],
                    'Duration (min)': round(row['duration_minutes'], 2),
                    'Reason': row['outlier_reason'],
                    'Date': row['INFEED_MISSION_CDATE']
                })
            
            for idx, row in all_outliers_outfeed.iterrows():
                outlier_table_data.append({
                    'Type': 'Outfeed',
                    'Product': row['PRODUCT_NAME'],
                    'Status': row['OUTFEED_MISSION_STATUS'],
                    'Duration (min)': round(row['duration_minutes'], 2),
                    'Reason': row['outlier_reason'],
                    'Date': row['OUTFEED_MISSION_CDATE']
                })
            
            for idx, row in all_outliers_transfer.iterrows():
                outlier_table_data.append({
                    'Type': 'Transfer',
                    'Product': row['PRODUCT_NAME'],
                    'Status': row['TRANSFER_MISSION_STATUS'],
                    'Duration (min)': round(row['duration_minutes'], 2),
                    'Reason': row['outlier_reason'],
                    'Date': row['CDATE']
                })
            
            outlier_df = pd.DataFrame(outlier_table_data)
            
            # Sort by duration (highest first)
            outlier_df = outlier_df.sort_values('Duration (min)', ascending=False)
            
            st.dataframe(
                outlier_df,
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            st.caption(f"Total outliers: {len(outlier_df):,}")
    else:
        st.info("No outliers found in the selected data")

# ========== TAB 4: STOCK DASHBOARD ==========
with tab4:
    st.subheader("Stock Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['sky_blue']} 0%, #3A9BD6 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Total Pallets</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{total_pallets:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['blue_green']} 0%, #027859 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Full Pallets</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{full_pallets:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['orange']} 0%, #C57A04 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">Empty Pallets</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{empty_pallets:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['vermillion']} 0%, #B34D00 100%); 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 8px;">High Ageing</div>
            <div style="color: #FFFFFF; font-size: 36px; font-weight: 700;">{high_ageing:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Stock Ageing Chart
    st.subheader("Stock Ageing Distribution")
    
    def get_age_range(age):
        if age <= 7:
            return '0-7 days'
        elif age <= 15:
            return '8-15 days'
        elif age <= 30:
            return '16-30 days'
        else:
            return '30+ days'
    
    stock_df['AGE_RANGE'] = stock_df['AGEING_DAYS'].apply(get_age_range)
    age_counts = stock_df['AGE_RANGE'].value_counts().reindex(['0-7 days', '8-15 days', '30+ days'], fill_value=0)
    
    fig_ageing = go.Figure(data=[go.Bar(
        x=age_counts.index,
        y=age_counts.values,
        marker_color=COLORS['sky_blue'],
        width=0.4
    )])
    fig_ageing.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
        font=dict(family="Times New Roman, Times, serif", size=12)
    )
    st.plotly_chart(fig_ageing, use_container_width=True, config=PLOT_CONFIG)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("Data upto 8th November 2025")