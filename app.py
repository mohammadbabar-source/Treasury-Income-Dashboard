import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import base64
import os
import numpy as np
import json
try:
    import streamlit.components.v1 as components
except Exception:
    components = None

# 1. Page Configuration MUST be the first Streamlit command
st.set_page_config(page_title="Karandaaz Treasury Summary FY26-27", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# HELPER TO PREVENT STREAMLIT MARKDOWN CODE-BLOCK BUGS
# ---------------------------------------------------------
def clean_html(html_str):
    """Strips leading/trailing whitespace from every line so Markdown never converts HTML to code blocks."""
    return "\n".join([line.strip() for line in html_str.splitlines() if line.strip()])

# ---------------------------------------------------------
# BASE64 IMAGE ENCODER FOR UPLOADED GITHUB LOGO
# ---------------------------------------------------------
EXCEL_FILE = "Treasury Income FY26'27 - July26.xlsx"
PKRV_FILE = "PKRV FORECASTS (TIME SERIES ANALYSIS).xlsx"
LOGO_FILE = "krn logo.jpg"

def get_base64_logo():
    if os.path.exists(LOGO_FILE):
        with open(LOGO_FILE, "rb") as f:
            return base64.b64encode(f.read()).decode()
    for file in os.listdir('.'):
        if any(term in file.lower() for term in ['krn', 'logo']) and file.lower().endswith(('.jpg', '.jpeg', '.png')):
            with open(file, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_logo()

if logo_b64:
    splash_logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width: 475px; max-width: 90%; margin: 0 auto 20px auto; padding: 0; border: none !important; outline: none !important; box-shadow: none !important; background: transparent !important; display: block;">'
    header_logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" alt="Logo" style="height: 48px; border: none !important; outline: none !important; box-shadow: none !important; background: transparent !important; object-fit: contain; margin: 0; padding: 0;">'
else:
    splash_logo_html = '<div style="color: #FFFFFF; font-size: 42px; font-weight: 700; margin-bottom: 20px; font-family: \'Chivo\', sans-serif; letter-spacing: 2px;">KARANDAAZ PAKISTAN</div>'
    header_logo_html = '<span style="color: #f68b1e; font-size: 22px; font-weight: 700; margin-right: 8px;">KRN</span>'

# ---------------------------------------------------------
# SESSION STATE CONTROL FOR FIRST-TIME SPLASH LOAD
# ---------------------------------------------------------
if 'has_loaded' not in st.session_state:
    st.session_state.has_loaded = True
    is_first_load = True
else:
    is_first_load = False

# ---------------------------------------------------------
# DYNAMIC DATA INGESTION FROM EXCEL (TREASURY & PKRV)
# ---------------------------------------------------------
try:
    df_q = pd.read_excel(EXCEL_FILE, sheet_name='Quarterly', header=None)
    def get_q_val(row_idx, col_idx):
        if row_idx < len(df_q) and col_idx < df_q.shape[1]:
            val = df_q.iloc[row_idx, col_idx]
            return float(val) if pd.notna(val) and isinstance(val, (int, float)) else 0.0
        return 0.0

    inc_q1 = get_q_val(10, 2) / 1e6
    inc_q2 = get_q_val(10, 3) / 1e6
    inc_q3 = get_q_val(10, 4) / 1e6
    inc_q4 = get_q_val(10, 5) / 1e6
    
    osr_q1 = get_q_val(4, 2) / 1e6
    rpa_q1 = get_q_val(5, 2) / 1e6
    esc_q1 = get_q_val(6, 2) / 1e6
    tdr_q1 = get_q_val(8, 2) / 1e6
    buysell_q1 = get_q_val(9, 2) / 1e6

    df_pool = pd.read_excel(EXCEL_FILE, sheet_name='Treasury Pool', header=None)
    def get_pool_val(row_idx, col_idx):
        if row_idx < len(df_pool) and col_idx < df_pool.shape[1]:
            val = df_pool.iloc[row_idx, col_idx]
            return float(val) if pd.notna(val) and isinstance(val, (int, float)) else 0.0
        return 0.0

    pool_jul = get_pool_val(11, 2) / 1e6
    pool_aug = get_pool_val(11, 3) / 1e6
    pool_sep = get_pool_val(11, 4) / 1e6
    q1_pool = pool_sep if pool_sep > 0 else (pool_aug if pool_aug > 0 else pool_jul)

    lr_funds = get_pool_val(4, 4) / 1e6 if get_pool_val(4, 4) > 0 else get_pool_val(4, 2) / 1e6
    osr_funds = get_pool_val(5, 4) / 1e6 if get_pool_val(5, 4) > 0 else get_pool_val(5, 2) / 1e6
    inv_cdel = get_pool_val(6, 4) / 1e6 if get_pool_val(6, 4) > 0 else get_pool_val(6, 2) / 1e6
    rpa_acc = get_pool_val(7, 4) / 1e6 if get_pool_val(7, 4) > 0 else get_pool_val(7, 2) / 1e6
    wv_greenfin = get_pool_val(8, 4) / 1e6 if get_pool_val(8, 4) > 0 else get_pool_val(8, 2) / 1e6
    op_funds = get_pool_val(9, 4) / 1e6 if get_pool_val(9, 4) > 0 else get_pool_val(9, 2) / 1e6

    df_mpr = pd.read_excel(EXCEL_FILE, sheet_name='MPR')
    mpr_rate = float(df_mpr.iloc[0]['MPC Rate']) * 100
    next_mpr_date = pd.to_datetime(df_mpr.iloc[1]['MPC Meeting Date']).strftime('%b %d, %Y')

    df_rates = pd.read_excel(EXCEL_FILE, sheet_name='Profit Rates')

except Exception as e:
    inc_q1, inc_q2, inc_q3, inc_q4 = 258.95, 0.0, 0.0, 0.0
    osr_q1, rpa_q1, esc_q1, tdr_q1, buysell_q1 = 165.72, 2.61, 2.00, 42.53, 46.07
    q1_pool = 16278.35
    lr_funds, osr_funds, inv_cdel, rpa_acc, wv_greenfin, op_funds = 5521.09, 9310.81, 98.91, 250.56, 337.10, 68.24
    mpr_rate, next_mpr_date = 11.50, "Sep 14, 2026"
    df_rates = pd.DataFrame()

# PKRV FORECASTS DATA INGESTION
def load_pkrv_data():
    try:
        df_raw = pd.read_excel(PKRV_FILE, sheet_name='PKRVs')
        headers = ['DATE', '1M', '3M', '6M', '12M']
        df_pk = df_raw.iloc[4:].copy()
        df_pk.columns = headers
        df_pk['DATE'] = pd.to_datetime(df_pk['DATE'], errors='coerce')
        for col in ['1M', '3M', '6M', '12M']:
            df_pk[col] = pd.to_numeric(df_pk[col], errors='coerce') * 100.0  # Percentage Conversion
        df_pk_filtered = df_pk[df_pk['DATE'] >= '2026-06-30'].dropna(subset=['DATE']).sort_values('DATE').reset_index(drop=True)
        if not df_pk_filtered.empty:
            return df_pk_filtered
    except Exception:
        pass
    
    # Fallback dataset starting June 30, 2026
    dates = pd.date_range(start='2026-06-30', end='2026-09-15', freq='B')
    return pd.DataFrame({
        'DATE': dates,
        '1M': [11.56, 11.54, 11.49, 11.50, 11.51] + list(np.random.normal(11.45, 0.05, len(dates)-5)),
        '3M': [11.60, 11.54, 11.46, 11.46, 11.46] + list(np.random.normal(11.48, 0.05, len(dates)-5)),
        '6M': [11.63, 11.55, 11.38, 11.35, 11.35] + list(np.random.normal(11.65, 0.08, len(dates)-5)),
        '12M': [11.60, 11.48, 11.22, 11.09, 11.10] + list(np.random.normal(11.90, 0.10, len(dates)-5))
    })

df_pkrv_chart = load_pkrv_data()

# DYNAMIC LATEST PKRV NUMBERS AND DATE
if not df_pkrv_chart.empty:
    latest_pkrv_row = df_pkrv_chart.iloc[-1]
    latest_pkrv_date_str = latest_pkrv_row['DATE'].strftime('%b %d, %Y')
    val_1m_str = f"{latest_pkrv_row['1M']:.2f}%"
    val_3m_str = f"{latest_pkrv_row['3M']:.2f}%"
    val_6m_str = f"{latest_pkrv_row['6M']:.2f}%"
    val_12m_str = f"{latest_pkrv_row['12M']:.2f}%"
else:
    latest_pkrv_date_str = "Sep 15, 2026"
    val_1m_str, val_3m_str, val_6m_str, val_12m_str = "11.48%", "11.52%", "11.75%", "12.00%"

quarter_months_map = {
    "Q1": [("Jul 2026", 0), ("Aug 2026", 1), ("Sep 2026", 2)],
    "Q2": [("Oct 2026", 3), ("Nov 2026", 4), ("Dec 2026", 5)],
    "Q3": [("Jan 2027", 6), ("Feb 2027", 7), ("Mar 2027", 8)],
    "Q4": [("Apr 2027", 9), ("May 2027", 10), ("Jun 2027", 11)],
}

def get_quarter_rates(q_key):
    months = quarter_months_map.get(q_key, quarter_months_map["Q1"])
    result = []
    for month_label, col_idx in months:
        raw_val = None
        if not df_rates.empty and col_idx < df_rates.shape[1]:
            raw_val = df_rates.iloc[-1, col_idx]
        
        if pd.isna(raw_val) or not str(raw_val).strip():
            rates_list = ["Pending / Not Updated"]
        else:
            lines = str(raw_val).strip().split('\n')
            rates_list = [line.replace('%%', '%').strip() for line in lines if line.strip()]
        
        result.append({
            "month": month_label,
            "rates": rates_list,
            "inline": " &bull; ".join(rates_list)
        })
    return result

quarter_data = {
    "Q1": {
        "period": "Q1 (Jul - Sep 2026)",
        "total_income": inc_q1,
        "treasury_pool": q1_pool,
        "forecasted_income": inc_q1 if inc_q1 > 0 else 312.40,
        "annual_yield": "11.30%",
        "months": ['Jul 26', 'Aug 26', 'Sep 26'],
        "income_trend": [inc_q1 * 0.33, inc_q1 * 0.35, inc_q1 * 0.32] if inc_q1 > 0 else [99.5, 105.2, 107.8], 
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow', 'TDR', 'Buy/Sell'],
        "margin_values": [osr_q1, rpa_q1, esc_q1, tdr_q1, buysell_q1]
    },
    "Q2": {
        "period": "Q2 (Oct - Dec 2026)",
        "total_income": inc_q2,
        "treasury_pool": 0.0,
        "forecasted_income": 0.0,
        "annual_yield": "N/A",
        "months": ['Oct 26', 'Nov 26', 'Dec 26'],
        "income_trend": [0, 0, 0],
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow', 'TDR', 'Buy/Sell'],
        "margin_values": [0, 0, 0, 0, 0]
    },
    "Q3": {
        "period": "Q3 (Jan - Mar 2027)",
        "total_income": inc_q3,
        "treasury_pool": 0.0,
        "forecasted_income": 0.0,
        "annual_yield": "N/A",
        "months": ['Jan 27', 'Feb 27', 'Mar 27'],
        "income_trend": [0, 0, 0],
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow', 'TDR', 'Buy/Sell'],
        "margin_values": [0, 0, 0, 0, 0]
    },
    "Q4": {
        "period": "Q4 (Apr - Jun 2027)",
        "total_income": inc_q4,
        "treasury_pool": 0.0,
        "forecasted_income": 0.0,
        "annual_yield": "N/A",
        "months": ['Apr 27', 'May 27', 'Jun 27'],
        "income_trend": [0, 0, 0],
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow', 'TDR', 'Buy/Sell'],
        "margin_values": [0, 0, 0, 0, 0]
    }
}

# ---------------------------------------------------------
# GLOBAL STYLING ARCHITECTURE
# ---------------------------------------------------------
st.markdown(clean_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chivo:wght@400;700&display=swap');

* { font-family: 'Chivo', sans-serif !important; box-sizing: border-box; }
html, body, .stApp { background-color: #F5F7F9 !important; margin: 0 !important; padding: 0 !important; }
header { visibility: hidden; height: 0; }

.block-container { 
    padding-top: 5rem !important; padding-bottom: 3rem !important; 
    padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; 
}

/* SBP Rolling Banner */
.sbp-marquee {
    position: fixed; top: 0; left: 0; width: 100%;
    background: #0f6286; color: #FFFFFF; padding: 11px 0;
    overflow: hidden; white-space: nowrap; z-index: 999999;
    border-bottom: 3px solid #f68b1e; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.sbp-marquee a { color: #FFFFFF !important; text-decoration: none; font-size: 21px; }
.sbp-marquee > span { display: inline-block; padding-left: 100%; animation: marquee_scroll 28s linear infinite; }
@keyframes marquee_scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-100%); } }

/* Header Component */
.header-container { display: flex; align-items: center; justify-content: center; margin-top: 10px !important; margin-bottom: 16px; }
.glow-line { height: 2px; flex-grow: 1; max-width: 380px; background: transparent; }
.header-card { 
    background: #0f6286; border-radius: 16px; padding: 14px 40px; 
    margin: 0 24px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); 
    font-weight: 700; font-size: 34px; color: #FFFFFF; 
    display: flex; align-items: center; gap: 16px; 
}

/* TOP 4 WHITE KPI CARDS WITH PULSING LIGHT BLUE BORDER */
.top-kpi-card { 
    background: #FFFFFF !important; 
    border-radius: 16px; 
    padding: 32px 16px; 
    height: 100%; 
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    align-items: center; 
    text-align: center; 
    border: 2.5px solid #76C4E3;
    animation: pulseLightBlue 2.5s ease-in-out infinite;
    transition: transform 0.2s ease;
}
.top-kpi-card:hover { transform: translateY(-2px); }

@keyframes pulseLightBlue {
    0%, 100% {
        border-color: #76C4E3;
        box-shadow: 0 0 10px rgba(118, 196, 227, 0.35);
    }
    50% {
        border-color: #0f6286;
        box-shadow: 0 0 20px rgba(118, 196, 227, 0.8);
    }
}

.top-kpi-val { font-size: 42px; font-weight: 700; color: #0f6286 !important; line-height: 1.1; margin: 4px 0; }
.top-kpi-lbl { font-size: 18px; font-weight: 700; color: #0f6286 !important; text-transform: uppercase; }
.top-kpi-sub { font-size: 18px; font-weight: 400; color: #0f6286 !important; opacity: 0.85; }

/* STANDARD KPI CARDS (BOTTOM ROW) */
.kpi-card { 
    background: #0f6286; border-radius: 16px; padding: 32px 16px; 
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); height: 100%; 
    display: flex; flex-direction: column; justify-content: center; 
    align-items: center; text-align: center; border: none;
}
.kpi-val { font-size: 42px; font-weight: 700; color: #FFFFFF; line-height: 1.1; margin: 4px 0; }
.kpi-lbl { font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase; }
.kpi-sub { font-size: 18px; font-weight: 400; color: #ffffff; opacity: 0.9; }

/* HTML Container Cards */
.html-card {
    background-color: #0f6286; border-radius: 16px; padding: 32px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); display: flex;
    flex-direction: column; justify-content: flex-start; text-align: left;
    height: 100%; border: none;
}
div[data-baseweb="select"] > div { border-radius: 8px; font-size: 21px; font-weight: 700; padding: 4px; border: 1px solid #0f6286 !important; color: #333333; }

/* CSS-ONLY MODAL OVERLAY STYLES */
#income-modal-toggle:checked ~ #income-modal-overlay { display: flex !important; }
.icon-btn-hover {
    position: absolute; top: 12px; right: 14px; cursor: pointer; background: rgba(15, 98, 134, 0.08); 
    border-radius: 50%; padding: 8px; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;
}
.icon-btn-hover:hover { background: rgba(246, 139, 30, 0.2) !important; transform: scale(1.2); }
.close-hover { transition: opacity 0.2s; opacity: 0.8; }
.close-hover:hover { opacity: 1 !important; }
.branched-box-hover { transition: transform 0.2s; }
.branched-box-hover:hover { transform: translateY(-4px); }
</style>
"""), unsafe_allow_html=True)

# ---------------------------------------------------------
# ANIMATED SPLASH SCREEN (CONFIGURED TO 7 SECONDS)
# ---------------------------------------------------------
if is_first_load:
    splash_placeholder = st.empty()
    
    with splash_placeholder.container():
        splash_content = clean_html(f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; background-color: #0f6286; position: fixed; top: 0; left: 0; width: 100vw; z-index: 9999999; padding: 0; margin: 0; overflow: hidden;">
            
            {splash_logo_html}
            
            <h1 style="color: #FFFFFF; font-size: 52px; margin-top: 10px; margin-bottom: 35px; font-weight: 700; font-family: 'Chivo', sans-serif; text-align: center; letter-spacing: 0.5px;">Karandaaz Pakistan Treasury Dashboard</h1>
            
            <div class="quantum-loader">
                <div class="ring outer-ring"></div>
                <div class="ring middle-ring"></div>
                <div class="ring inner-ring"></div>
                <div class="core-glow"></div>
                <div class="particle p1"></div>
                <div class="particle p2"></div>
                <div class="particle p3"></div>
            </div>
            
            <div style="color: #f68b1e; font-size: 18px; font-weight: 700; font-family: 'Chivo', sans-serif; letter-spacing: 3px; margin-top: 30px; text-transform: uppercase; animation: textPulse 1.5s ease-in-out infinite;">SYNCING PORTFOLIO DATA...</div>
        </div>
        
        <style>
        .quantum-loader {{
            position: relative;
            width: 110px;
            height: 110px;
            display: flex;
            justify-content: center;
            align-items: center;
            perspective: 800px;
        }}

        .ring {{
            position: absolute;
            border-radius: 50%;
            border: 3px solid transparent;
        }}

        .outer-ring {{
            width: 100%;
            height: 100%;
            border-top-color: #f68b1e;
            border-bottom-color: #f68b1e;
            animation: spinClockwise 1.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
            filter: drop-shadow(0 0 10px rgba(246, 139, 30, 0.6));
        }}

        .middle-ring {{
            width: 75%;
            height: 75%;
            border-left-color: #76C4E3;
            border-right-color: #76C4E3;
            animation: spinCounterClockwise 1.2s linear infinite;
            filter: drop-shadow(0 0 8px rgba(118, 196, 227, 0.8));
        }}

        .inner-ring {{
            width: 50%;
            height: 50%;
            border-top-color: #FFFFFF;
            animation: spinClockwise 0.9s ease-in-out infinite;
        }}

        .core-glow {{
            width: 18px;
            height: 18px;
            background-color: #FFFFFF;
            border-radius: 50%;
            box-shadow: 0 0 15px #FFFFFF, 0 0 30px #f68b1e, 0 0 45px #76C4E3;
            animation: pulseCore 1.2s ease-in-out infinite alternate;
        }}

        .particle {{
            position: absolute;
            width: 6px;
            height: 6px;
            background-color: #f68b1e;
            border-radius: 50%;
            box-shadow: 0 0 8px #f68b1e;
        }}

        .p1 {{ top: 10%; left: 50%; animation: floatParticle1 2s ease-in-out infinite; }}
        .p2 {{ bottom: 15%; left: 20%; animation: floatParticle2 2.2s ease-in-out infinite; }}
        .p3 {{ top: 40%; right: 10%; animation: floatParticle3 1.8s ease-in-out infinite; }}

        @keyframes spinClockwise {{ 0% {{ transform: rotate(0deg) rotateX(20deg); }} 100% {{ transform: rotate(360deg) rotateX(20deg); }} }}
        @keyframes spinCounterClockwise {{ 0% {{ transform: rotate(0deg) rotateY(20deg); }} 100% {{ transform: rotate(-360deg) rotateY(20deg); }} }}
        @keyframes pulseCore {{ 0% {{ transform: scale(0.7); opacity: 0.6; }} 100% {{ transform: scale(1.3); opacity: 1; }} }}
        @keyframes textPulse {{ 0%, 100% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} }}
        
        @keyframes floatParticle1 {{ 0%, 100% {{ transform: translateY(0) scale(1); }} 50% {{ transform: translateY(-12px) scale(1.5); }} }}
        @keyframes floatParticle2 {{ 0%, 100% {{ transform: translateX(0) scale(1); }} 50% {{ transform: translateX(12px) scale(1.3); }} }}
        @keyframes floatParticle3 {{ 0%, 100% {{ transform: translateY(0) scale(1); }} 50% {{ transform: translateY(10px) scale(0.8); }} }}
        </style>
        """)
        st.markdown(splash_content, unsafe_allow_html=True)
        time.sleep(7.0)
    
    splash_placeholder.empty()

# ---------------------------------------------------------
# TREASURY COMMITTEE PRESENTATION — SLIDE CONTENT (EDIT FIGURES HERE)
# Source: Treasury_Committee_Presentation_Q1-_26-27.pptx
# ---------------------------------------------------------
TC_DECK_DATA = {
    "meeting_date": "October 20, 2026",
    "period": "Q1 · FY 2026–27",
    "economy": {
        "title": "Pakistan Economic Update — FY2026",
        "subtitle": "Pakistan's macroeconomic footing",
        "stats": [
            {"value": 4.8,  "dec": 1, "prefix": "",  "suffix": "%", "label": "Real GDP Growth",     "sub": "Highest in 4 years"},
            {"value": 45.8, "dec": 1, "prefix": "$", "suffix": "T", "label": "Economy Size",        "sub": "YoY GDP"},
            {"value": 10.3, "dec": 1, "prefix": "",  "suffix": "%", "label": "CPI Inflation (YoY)", "sub": "Sep 2026"},
            {"value": 11.5, "dec": 1, "prefix": "",  "suffix": "%", "label": "Policy Rate",         "sub": "MPC decision, 15 Jun 2026"},
        ],
        "markets": [
            "The economy continued to consolidate gains from macroeconomic stabilization during the first two months of FY2027.",
            "The Bureau of Emigration and Overseas Employment registered 27,656 Pakistani workers for overseas employment in August 2026, supporting access to international labour markets.",
            "Core inflation came in slightly below expectations, and the policy rate remains positive in real terms.",
            "The KSE-100 index gained 882 points, or about 0.5%.",
        ],
        "bars": [
            {"label": "Inflation (Sep 2026)", "value": 11.7, "color": "#f68b1e"},
            {"label": "Monetary Policy Rate", "value": 11.5, "color": "#76C4E3"},
        ],
        "mpc_note": "<b>MPC Decision (14 Sep 2026):</b> Policy rate maintained at 11.5%",
    },
    "policy": {
        "labels": ["Jun 10, '24", "Jul 29, '24", "Apr 30, '25", "May 5, '25", "Dec 15, '25", "Apr 27, '26", "Jun 15, '26", "Dec '26 (proj.)", "Jun '27 (proj.)"],
        "actual": [20.5, 19.5, 13.0, 11.0, 10.5, 11.5, 11.5, None, None],
        "hold":   [None, None, None, None, None, None, 11.5, 11.5, 11.5],
        "ease":   [None, None, None, None, None, None, 11.5, 12.0, 12.5],
        "hold_name": "Scenario: Extended Hold",
        "ease_name": "Scenario: Gradual Easing",
        "chips": [
            {"value": "22.0%", "label": "Peak (pre-Jun 2024)"},
            {"value": "10.5%", "label": "Trough (Dec 2025)"},
            {"value": "11.5%", "label": "Current (held Sep 2026)"},
        ],
        "outlook": [
            "FY2027 inflation is broadly projected to average just above 8%, still outside SBP's 5–7% target band.",
            "Near term: analysts see little room for either a further hike or hold — most expect an extended hold near 11.5%.",
            "Elevated and volatile global oil prices remain the key upside risk to both inflation and the rate path.",
            "If oil prices ease and inflation cools as expected from H2 CY2026 onward, a gradual, modest easing cycle could resume later in FY2027.",
            "Two scenarios are illustrated on the chart: an extended hold vs. a gradual hike toward the 11.5–12.5% range.",
        ],
        "disclaimer": "Not financial advice. Scenarios are illustrative only — actual policy moves depend on incoming data and MPC decisions.",
        "source": "Source: State Bank of Pakistan (SBP) monetary policy statements, Jun 2024 – Jun 2026",
    },
    "pkrv": {
        "short_labels": ["Jan '26", "Feb '26", "Mar '26", "Apr '26", "May '26", "Jun '26", "Jul '26", "Aug '26", "Sep '26"],
        "m1":  [10.19, 10.35, 11.21, 11.34, 11.51, 11.56, 11.48, 11.48, 11.58],
        "m3":  [10.18, 10.34, 11.28, 11.69, 11.94, 11.60, 11.45, 11.51, 11.64],
        "long_labels": ["Dec '25", "Jan '26", "Feb '26", "Mar '26", "Apr '26", "May '26", "Jun '26", "Jul '26", "Aug '26", "Sep '26"],
        "m6":  [10.41, 10.28, 10.56, 11.64, 11.87, 12.37, 11.63, 11.65, 11.70, 11.84],
        "m12": [10.39, 10.35, 10.62, 11.90, 12.04, 12.52, 11.60, 11.81, 11.95, 12.20],
        "y2":  [10.45, 10.27, 10.55, 12.46, 12.38, 12.62, 11.69, 11.65, 11.87, 12.46],
        "as_of": "Sep 30, 2026",
    },
    "pool": {
        "as_of": "September 30, 2026",
        # [Account, Rate %, Bucket, PKR Mn]
        "accounts": [
            ["HBL Liquidity Reserve A/c", 9.50, "LR", 0.27],
            ["HMBL OSR A/c", 10.00, "LR", 6.64],
            ["Faysal OSR A/c", 10.25, "LR", 2035.84],
            ["Samba OSR A/c", 10.30, "LR", 1041.92],
            ["ABL OSR A/c", 9.00, "LR", 0.08],
            ["UBL T-Bills", 11.42, "LR", 2354.07],
            ["HMBL Buy & Sell", 11.57, "OSR", 4000.52],
            ["Faysal OSR A/c", 10.25, "OSR", 1934.22],
            ["BAFL OSR A/c", 10.75, "OSR", 1775.95],
            ["UBL OSR A/c", 11.00, "OSR", 258.58],
            ["BIPL OSR A/c", 8.00, "OSR", 513.69],
            ["UBL Investment Account", 11.00, "Investment", 477.59],
            ["BAFL Investment Account", 10.75, "Investment", 10.83],
            ["BAFL CIC A/c (For PFSL)", 10.75, "Investment", 94.46],
            ["BAFL RPA A/c", 10.75, "RPA", 86.68],
            ["JSBL RPA A/c", 6.73, "RPA", 24.58],
            ["Meezan RPA A/c", 2.52, "RPA", 5.39],
            ["MIB RPA A/c", 6.42, "RPA", 1058.93],
            ["HMBL RPA A/c", 10.00, "RPA", 0.07],
            ["Soneri RPA A/c", 6.50, "RPA", 21.84],
            ["UBL WV A/c", 11.00, "WV", 0.01],
            ["Faysal WV A/c", 10.25, "WV", 332.04],
            ["Samba KCBL A/c", 10.30, "WV", 105.72],
        ],
        "highlight": ["UBL T-Bills", "HMBL Buy & Sell"],
        "buckets": [
            {"key": "LR", "name": "Liquidity Reserve", "value": 5438.82},
            {"key": "OSR", "name": "OSR", "value": 8482.96},
            {"key": "Investment", "name": "Investment", "value": 582.88},
            {"key": "RPA", "name": "RPA", "value": 1197.50},
            {"key": "WV", "name": "WV", "value": 437.76},
        ],
        "total": 16139.92,
        "weighted_rate": 10.51,
    },
    "grants": {
        "as_of": "September 30, 2026",
        # [Account, GF, FIP]  (PKR Mn)
        "accounts": [
            ["BAFL USD A/c (USD to PKR)*", 2042.99, None],
            ["BAFL Ehsaas A/c", 10.88, None],
            ["BAFL CCT A/c", 8.97, None],
            ["BAFL Raast A/c", 1.81, None],
            ["BAFL PCDFI A/c", 17.35, None],
            ["UBL PCDFI A/c", 1.74, None],
            ["BAFL FBR A/c", 34.09, None],
            ["BAFL FIP A/c", None, 0.59],
            ["UBL FIP A/c", None, 254.86],
            ["HMBL FIP A/c", None, 0.00],
        ],
        "gf": 2117.83, "fip": 255.46, "total": 2373.29,
        "note": "* USD amounts are converted to PKR @ 277.50 (September 30, 2026 NBP rate sheet)",
    },
    "banks": {
        "as_of": "June 30, 2026",
        # [Bank, Long-Term Rating, Balance, Portfolio %, Rate offered, Utilization %, Institutional Limit, Under/(Over)]
        "rows": [
            ["Faysal", "AA+", 4302, 25.96, 10.25, 38, 11233, 6931],
            ["Samba", "AA", 1148, 6.92, 10.30, 97, 1178, 30],
            ["BAFL", "AAA", 2097, 12.65, 10.75, 11, 19210, 17113],
            ["UBL", "AAA", 1039, 6.27, 11.00, 2, 44431, 43392],
            ["MIB", "A+", 1059, 6.39, 6.24, 49, 2171, 1113],
            ["BIPL", "AA-", 514, 3.10, 8.00, 11, 4657, 4143],
            ["Other Banks", None, 61, 0.37, None, None, None, None],
            ["T-Bills", None, 2354, 14.20, 10.92, None, None, None],
            ["Buy & Sell", None, 4001, 24.14, 10.65, None, None, None],
        ],
        "total": 16573,
        "notes": [
            "Bank-wise portfolio includes all PKR balances except USD funds available in account",
            "Does not include escrow funds (PKR 220M)",
        ],
    },
    "income": {
        "headline": "Treasury has generated PKR 444.6M income during Q1 FY 26-27",
        # [Type, Opening Balance (PKR), Q1 Income (PKR)]
        "rows": [
            ["Income on LR deposit - EAGR", 5438817702, 147828615.30],
            ["Income on escrow a/cs - EAGR", 205720218, 7162137],
            ["Treasury income - EAGR", 10653957151, 289577591.93],
        ],
        "opening_total": 16298495071, "income_total": 444568344,
    },
    "forecast": {
        # [Income bucket, Avg balance for the year, Q1 (Actual), Q2, Q3, Q4]  (PKR)
        "rows": [
            ["Income on LR deposit - EAGR", 5662166647, 147828615, 147780872, 148698418, 152656322],
            ["Income on escrow a/cs - EAGR", 214169051, 7162137, 5532690, 5681488, 5834287],
            ["Treasury income - EAGR", 11050013806, 289577592, 286530151, 313030275, 310173160],
        ],
        "avg_total": 16926349504,
        "q_totals": [444568344, 439843713, 467410180, 468663769],
        "grand_total": 1820486007,
    },
}

TC_DECK_TEMPLATE = r'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Chivo:ital,wght@0,300;0,400;0,700;0,900;1,300;1,400&display=swap" rel="stylesheet">
<style>
:root{--orange:#f68b1e;--sky:#76C4E3;--gold:#FFC107;--brand:#0f6286;--muted:rgba(255,255,255,.64);--faint:rgba(255,255,255,.42);--line:rgba(118,196,227,.18)}
*{box-sizing:border-box;margin:0;padding:0;font-family:'Chivo',sans-serif}
html,body{width:100%;height:100%;overflow:hidden;color:#fff;background:#F5F7F9}
#viewport{position:absolute;left:0;right:0;top:0;bottom:60px;overflow:hidden}
#stage{position:absolute;left:50%;top:50%;width:1600px;height:900px;transform-origin:center center;border-radius:20px;overflow:hidden;box-shadow:0 24px 70px rgba(4,27,40,.45);background:#03141e}
:fullscreen body,:fullscreen #viewport{background:#020d14}
:fullscreen #stage{border-radius:0}
.num{font-variant-numeric:tabular-nums}

/* ---------- slides ---------- */
.slide{position:absolute;inset:0;padding:54px 72px 64px;opacity:0;visibility:hidden;transform:translateX(46px) scale(.985);
  transition:opacity .75s cubic-bezier(.2,.7,.2,1),transform .75s cubic-bezier(.2,.7,.2,1),visibility 0s linear .75s;
  background:radial-gradient(1100px 650px at 92% -12%,rgba(15,98,134,.62),transparent 62%),
             radial-gradient(800px 520px at -8% 112%,rgba(246,139,30,.11),transparent 60%),
             linear-gradient(160deg,#062b3f 0%,#041c29 55%,#03131c 100%)}
.slide.before{transform:translateX(-46px) scale(.985)}
.slide.active{opacity:1;visibility:visible;transform:none;transition:opacity .75s cubic-bezier(.2,.7,.2,1),transform .75s cubic-bezier(.2,.7,.2,1),visibility 0s}
.rings{position:absolute;right:-260px;top:-300px;width:760px;height:760px;pointer-events:none;opacity:.55}
.rings circle{fill:none;stroke:rgba(118,196,227,.10);stroke-width:1.2}
.slide.active .rings{animation:spin 90s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

.rv{opacity:0;transform:translateY(20px)}
.slide.active .rv{animation:rise .85s cubic-bezier(.2,.7,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 180ms)}
@keyframes rise{to{opacity:1;transform:none}}
.rvx{opacity:0;transform:translateX(-16px)}
.slide.active .rvx{animation:rise .7s cubic-bezier(.2,.7,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 180ms)}

/* header */
.hd{position:relative;display:flex;gap:28px;justify-content:space-between;align-items:flex-end;margin-bottom:30px;z-index:2}
.eyebrow{display:flex;align-items:center;gap:14px;font-size:14px;letter-spacing:4px;text-transform:uppercase;color:var(--orange);font-weight:700}
.eyebrow .no{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%;border:1.5px solid rgba(246,139,30,.6);font-size:13px;letter-spacing:0;color:#fff;background:rgba(246,139,30,.14)}
.title{font-size:48px;font-weight:900;line-height:1.06;margin-top:14px;letter-spacing:-.6px}
.sub{font-size:19px;color:var(--muted);margin-top:8px;font-weight:300;font-style:italic}
.ft{position:absolute;left:72px;right:72px;bottom:24px;display:flex;justify-content:space-between;align-items:center;font-size:12.5px;color:var(--faint);letter-spacing:2px;text-transform:uppercase;z-index:2}
.ft b{color:rgba(255,255,255,.7);font-weight:700}

/* cards */
.card{position:relative;background:linear-gradient(180deg,rgba(255,255,255,.065),rgba(255,255,255,.02));border:1px solid var(--line);border-radius:22px;padding:26px 30px;box-shadow:0 18px 40px rgba(0,0,0,.25)}
.ct{font-size:13px;letter-spacing:3px;text-transform:uppercase;color:var(--sky);font-weight:700;margin-bottom:18px;display:flex;align-items:baseline;gap:10px;line-height:1.4}
.ct .dot{flex:none;transform:translateY(-1px)}
.ct .dot{width:8px;height:8px;border-radius:50%;background:var(--orange);box-shadow:0 0 12px var(--orange)}
.grid{display:grid;gap:24px}

/* stats */
.stat{padding:26px 28px;overflow:hidden}
.stat .v{font-size:60px;font-weight:900;line-height:1;letter-spacing:-1.5px}
.stat .l{font-size:18px;font-weight:700;margin-top:14px}
.stat .s{font-size:14px;color:var(--faint);margin-top:6px;letter-spacing:.5px}
.stat .glow{position:absolute;right:-40px;top:-40px;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,rgba(246,139,30,.35),transparent 70%)}
.stat:nth-child(2) .glow{background:radial-gradient(circle,rgba(118,196,227,.35),transparent 70%)}
.stat:nth-child(3) .glow{background:radial-gradient(circle,rgba(255,193,7,.30),transparent 70%)}
.stat:nth-child(4) .glow{background:radial-gradient(circle,rgba(255,255,255,.22),transparent 70%)}

/* lists */
.bl{list-style:none}
.bl li{position:relative;padding-left:34px;font-size:18px;line-height:1.5;color:rgba(255,255,255,.9);margin-bottom:16px;font-weight:300}
.bl li:before{content:"";position:absolute;left:4px;top:9px;width:12px;height:12px;border-radius:3px 50% 50% 50%;background:var(--orange);transform:rotate(45deg);box-shadow:0 0 10px rgba(246,139,30,.6)}
.bl.sky li:before{background:var(--sky);box-shadow:0 0 10px rgba(118,196,227,.6)}
.bl.sm li{font-size:16.5px;margin-bottom:13px}

/* bars */
.hb{margin-bottom:26px}
.hb .top{display:flex;justify-content:space-between;font-size:17px;margin-bottom:10px}
.hb .top b{font-size:26px;font-weight:900}
.track{height:16px;border-radius:10px;background:rgba(255,255,255,.07);overflow:hidden}
.fill{height:100%;border-radius:10px;transform-origin:left center;transform:scaleX(0)}
.slide.active .fill{animation:growx 1.4s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 350ms)}
@keyframes growx{to{transform:scaleX(1)}}
.callout{margin-top:22px;padding:18px 22px;border-radius:16px;background:rgba(246,139,30,.10);border:1px solid rgba(246,139,30,.35);font-size:17px;line-height:1.5}
.callout b{color:var(--orange)}

/* chips */
.chips{display:flex;gap:14px}
.chip{padding:12px 18px;border-radius:16px;background:rgba(255,255,255,.05);border:1px solid var(--line);text-align:center;white-space:nowrap}
.chip .v{font-size:26px;font-weight:900;line-height:1}
.chip .l{font-size:11px;color:var(--faint);letter-spacing:1.2px;text-transform:uppercase;margin-top:8px}
.chip.hot{background:rgba(246,139,30,.14);border-color:rgba(246,139,30,.5)}
.chip.hot .v{color:var(--orange)}

/* charts */
svg text{font-family:'Chivo',sans-serif}
.gl{stroke:rgba(255,255,255,.08);stroke-width:1}
.ax{fill:rgba(255,255,255,.55);font-size:13px}
.ln{fill:none;stroke-linecap:round;stroke-linejoin:round}
.pt{opacity:0}
.slide.active .pt{animation:fade .5s forwards;animation-delay:calc(var(--d,0) * 1ms)}
@keyframes fade{to{opacity:1}}
.legend{display:flex;gap:22px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:8px}
.legend i{display:inline-block;width:22px;height:4px;border-radius:3px}
.legend i.dash{background:repeating-linear-gradient(90deg,currentColor 0 6px,transparent 6px 10px)!important;height:3px}
.bar{transform-box:fill-box;transform-origin:center bottom;transform:scaleY(0)}
.slide.active .bar{animation:growy 1.1s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 300ms)}
@keyframes growy{to{transform:scaleY(1)}}
.seg{transition:stroke-dasharray 1.5s cubic-bezier(.2,.8,.2,1)}

/* tables */
.tbl{width:100%;border-collapse:collapse}
.tbl th{font-size:11.5px;letter-spacing:1.6px;text-transform:uppercase;color:var(--sky);font-weight:700;text-align:left;padding:0 10px 10px;border-bottom:1px solid rgba(118,196,227,.3);white-space:nowrap}
.tbl td{padding:0 10px;border-bottom:1px solid rgba(255,255,255,.055);font-size:15px;color:rgba(255,255,255,.9);white-space:nowrap}
.tbl .r{text-align:right;font-variant-numeric:tabular-nums}
.tbl .c{text-align:center}
.tbl tfoot td{border-bottom:none;border-top:1px solid rgba(118,196,227,.35);font-weight:900;font-size:16px;color:#fff;padding-top:10px}
.tbl tfoot td.o{color:var(--orange)}
.tbl tr.hl td{background:rgba(118,196,227,.09)}
.tbl tr.hl td:first-child{border-radius:8px 0 0 8px}
.tbl tr.hl td:last-child{border-radius:0 8px 8px 0}
.pill{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11.5px;font-weight:700;letter-spacing:.8px}
.mini{display:flex;align-items:center;gap:10px;justify-content:flex-end}
.mini .t{width:120px;height:7px;border-radius:5px;background:rgba(255,255,255,.07);overflow:hidden}
.mini .t div{height:100%;border-radius:5px;transform-origin:left;transform:scaleX(0)}
.slide.active .mini .t div{animation:growx 1.2s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms + 400ms)}
.badge{display:inline-block;min-width:46px;text-align:center;padding:3px 8px;border-radius:8px;border:1px solid rgba(118,196,227,.45);color:var(--sky);font-size:13px;font-weight:700}
.muted{color:var(--faint)}
.note{font-size:13.5px;color:var(--faint);line-height:1.5}

/* cover */
.cover{padding:0}
.cover .inner{position:absolute;left:96px;top:110px;right:96px;z-index:2}
.logo-chip{display:inline-flex;align-items:center;gap:12px;background:#0f6286;border:1px solid rgba(118,196,227,.35);border-radius:16px;padding:10px 18px;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.logo-chip img{height:46px;display:block}
.logo-chip .t{font-weight:900;letter-spacing:4px;font-size:18px}
.cover h1{font-size:104px;font-weight:900;line-height:.98;letter-spacing:-3px;margin-top:46px}
.cover h1 em{font-style:normal;background:linear-gradient(90deg,#f68b1e,#FFC107);-webkit-background-clip:text;background-clip:text;color:transparent}
.cover .date{font-size:26px;font-weight:300;font-style:italic;color:var(--muted);margin-top:22px}
.kstrip{display:flex;gap:18px;margin-top:46px}
.kstrip .k{padding:18px 26px;border-radius:18px;background:rgba(255,255,255,.05);border:1px solid var(--line);backdrop-filter:blur(6px)}
.kstrip .k .v{font-size:34px;font-weight:900}
.kstrip .k .v small{font-size:17px;font-weight:400;color:var(--muted);margin-right:6px}
.kstrip .k .l{font-size:12.5px;letter-spacing:2px;text-transform:uppercase;color:var(--sky);margin-top:6px}
.pat{position:absolute;left:0;right:0;bottom:0;pointer-events:none}
.pat g.pg{opacity:0}
.slide.active .pat g.pg{animation:pop .7s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:calc(var(--d,0) * 1ms)}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:var(--o,.6);transform:scale(1)}}
.pat g.pg{transform-box:fill-box;transform-origin:center}
.orb{position:absolute;right:-220px;top:-160px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle at 35% 35%,rgba(15,98,134,.9),rgba(6,43,63,.2) 60%,transparent 70%);filter:blur(2px)}
.hero{background:linear-gradient(140deg,#0f6286 0%,#0a4865 55%,#072f44 100%);border:1px solid rgba(118,196,227,.35);overflow:hidden}
.hero .big{font-size:110px;font-weight:900;line-height:1;letter-spacing:-3px;background:linear-gradient(90deg,#FFC107,#f68b1e);-webkit-background-clip:text;background-clip:text;color:transparent}
.spark{position:absolute;border-radius:2px;background:#fff;opacity:.7}
.slide.active .spark{animation:twinkle 3s ease-in-out infinite}
@keyframes twinkle{50%{opacity:.15;transform:rotate(45deg) scale(.6)}}

/* controls */
#bar{position:absolute;left:0;right:0;bottom:0;height:60px;display:flex;align-items:center;justify-content:space-between;padding:0 18px;color:#0f6286}
#bar .lbl{font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:.8;min-width:260px}
#bar .mid{display:flex;align-items:center;gap:14px}
#bar .rt{display:flex;align-items:center;gap:12px;min-width:260px;justify-content:flex-end}
.btn{width:40px;height:40px;border-radius:50%;border:2px solid #0f6286;background:#fff;color:#0f6286;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .2s}
.btn:hover{background:#0f6286;color:#fff;transform:scale(1.06)}
.btn.wide{width:auto;padding:0 16px;border-radius:20px;font-weight:700;font-size:13px;letter-spacing:1px;gap:8px}
#dots{display:flex;gap:8px}
#dots b{width:10px;height:10px;border-radius:10px;background:rgba(15,98,134,.25);cursor:pointer;transition:all .3s}
#dots b.on{width:30px;background:#f68b1e}
#count{font-size:15px;font-weight:700;font-variant-numeric:tabular-nums}
#hint{font-size:12px;opacity:.6}
:fullscreen #bar{color:#cfe6f1}
:fullscreen .btn{background:transparent;border-color:#76C4E3;color:#76C4E3}
#prog{position:absolute;left:0;top:0;height:3px;background:linear-gradient(90deg,#f68b1e,#FFC107);z-index:20;transition:width .6s cubic-bezier(.2,.8,.2,1)}
</style></head>
<body>
<div id="viewport"><div id="stage"><div id="prog"></div></div></div>
<div id="bar">
  <div class="lbl">Treasury Committee · Q1 FY26-27</div>
  <div class="mid">
    <div class="btn" id="prev" title="Previous (←)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></div>
    <div id="dots"></div>
    <div class="btn" id="next" title="Next (→)"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></div>
  </div>
  <div class="rt">
    <span id="hint">← → to navigate · F for full screen</span>
    <span id="count">01 / 10</span>
    <div class="btn wide" id="fs" title="Full screen (F)"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/></svg>PRESENT</div>
  </div>
</div>
<script>
const D = __DECK_DATA__;
const LOGO = "__LOGO_B64__";
const COL = {orange:'#f68b1e', sky:'#76C4E3', gold:'#FFC107', white:'#EAF4F8', teal:'#3BA3C9', slate:'#9fb6c3'};
const BUCKET = {LR:COL.sky, OSR:COL.orange, Investment:COL.gold, RPA:COL.white, WV:COL.teal};
const f = (n,d=2)=> (n==null||isNaN(n)) ? '–' : Number(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const M = n => n/1e6;
const TOTAL = 10;

/* ---------- motif: Karandaaz circles & quarter-circles ---------- */
function rng(seed){return ()=>{seed=(seed*16807)%2147483647;return (seed-1)/2147483646}}
function pattern(cols,rows,cell,seed,empty,maxO){
  const r=rng(seed), s=cell*0.78, pad=(cell-s)/2; let out='';
  const cols_=['#76C4E3','#3BA3C9','#ffffff','#0f8fc0','#9fb6c3'];
  for(let y=0;y<rows;y++) for(let x=0;x<cols;x++){
    const v=r(); const k=Math.floor(r()*5); const c=cols_[Math.floor(r()*cols_.length)];
    // fewer shapes in the upper rows -> skyline effect
    const thr = empty + (rows-1-y)*0.16;
    if(v<thr) continue;
    const ox=x*cell+pad, oy=y*cell+pad, o=(0.25+r()*maxO).toFixed(2), d=Math.round((x*35)+(rows-y)*60+r()*200);
    let shape = k===0 ? `<circle cx="${s/2}" cy="${s/2}" r="${s/2-1}"/>`
      : `<path d="M0 ${s} L0 0 A${s} ${s} 0 0 1 ${s} ${s} Z" transform="rotate(${(k-1)*90} ${s/2} ${s/2})"/>`;
    out+=`<g transform="translate(${ox} ${oy})"><g class="pg" style="--d:${d};--o:${o}" fill="none" stroke="${c}" stroke-width="1.8">${shape}</g></g>`;
  }
  return out;
}
const rings = `<svg class="rings" viewBox="0 0 760 760"><circle cx="380" cy="380" r="370"/><circle cx="380" cy="380" r="300" stroke-dasharray="4 10"/><circle cx="380" cy="380" r="225"/><circle cx="380" cy="380" r="150" stroke-dasharray="2 8"/></svg>`;

function hd(n, eyebrow, title, sub, right=''){
  return `<div class="hd"><div><div class="eyebrow rvx" style="--d:0"><span class="no">${String(n).padStart(2,'0')}</span>${eyebrow}</div>
  <div class="title rv" style="--d:80">${title}</div>${sub?`<div class="sub rv" style="--d:160">${sub}</div>`:''}</div>${right}</div>`;
}
const ft = i => `<div class="ft"><span><b>Karandaaz Pakistan</b> &nbsp;·&nbsp; Treasury Committee</span><span>${D.period} &nbsp;·&nbsp; ${String(i+1).padStart(2,'0')}</span></div>`;

/* ---------- chart helpers ---------- */
function lineChart(o){
  const W=o.w,H=o.h,P={l:58,r:o.pr||28,t:20,b:44},iw=W-P.l-P.r,ih=H-P.t-P.b,n=o.labels.length;
  const x=i=>P.l+i*iw/(n-1), y=v=>P.t+ih-(v-o.min)/(o.max-o.min)*ih;
  let g='';
  for(let v=o.min; v<=o.max+1e-9; v+=o.step){
    g+=`<line class="gl" x1="${P.l}" x2="${W-P.r}" y1="${y(v)}" y2="${y(v)}"/><text class="ax" x="${P.l-12}" y="${y(v)+4.5}" text-anchor="end">${f(v,o.dec??0)}%</text>`;
  }
  o.labels.forEach((l,i)=>{ if(o.every && i%o.every) return; g+=`<text class="ax" x="${x(i)}" y="${H-P.b+26}" text-anchor="middle">${l}</text>`});
  if(o.vline!=null){ const vx=x(o.vline); g+=`<line x1="${vx}" x2="${vx}" y1="${P.t}" y2="${P.t+ih}" stroke="rgba(255,255,255,.35)" stroke-dasharray="5 6"/><text class="ax" x="${vx+10}" y="${P.t+14}" font-style="italic">${o.vlabel||''}</text>`;}
  if(o.band){ const [a,b]=o.band; g+=`<rect x="${P.l}" width="${iw}" y="${y(b)}" height="${y(a)-y(b)}" fill="rgba(118,196,227,.06)"/>`; }
  let s='';
  o.series.forEach((se,si)=>{
    const pts=se.values.map((v,i)=>v==null?null:[x(i),y(v)]).filter(Boolean);
    if(!pts.length) return;
    let d=''; pts.forEach((p,i)=>{ d+= (i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)+' '; });
    if(se.area){ const a=d+`L${pts[pts.length-1][0]} ${P.t+ih} L${pts[0][0]} ${P.t+ih} Z`;
      s+=`<path d="${a}" fill="url(#ga${o.id}${si})" class="pt" style="--d:${900+si*200}"/>`;
      s+=`<defs><linearGradient id="ga${o.id}${si}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${se.color}" stop-opacity=".28"/><stop offset="1" stop-color="${se.color}" stop-opacity="0"/></linearGradient></defs>`; }
    s+=`<path class="ln anim" d="${d}" stroke="${se.color}" stroke-width="${se.w||3.5}" ${se.dash?'data-dash="'+se.dash+'"':''} style="filter:drop-shadow(0 0 6px ${se.color}55)" data-delay="${si*250}"/>`;
    pts.forEach((p,i)=>{ s+=`<circle class="pt" style="--d:${500+si*250+i*110}" cx="${p[0]}" cy="${p[1]}" r="${se.r||5}" fill="#062b3f" stroke="${se.color}" stroke-width="2.5"/>`; });
    if(se.endLabel){ const p=pts[pts.length-1]; const v=se.values.filter(v=>v!=null).slice(-1)[0];
      s+=`<g class="pt" style="--d:${1500+si*250}"><rect x="${p[0]+10}" y="${p[1]-13+(se.lo||0)}" rx="7" width="62" height="26" fill="${se.color}"/><text x="${p[0]+41}" y="${p[1]+5+(se.lo||0)}" text-anchor="middle" font-size="14" font-weight="900" fill="#03131c">${f(v,2)}%</text></g>`; }
  });
  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}${s}</svg>`;
}
function donut(o){
  const S=o.size,T=o.thick,r=(S-T)/2,C=2*Math.PI*r,tot=o.items.reduce((a,b)=>a+b.value,0); let acc=0,s='';
  s+=`<circle cx="${S/2}" cy="${S/2}" r="${r}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="${T}"/>`;
  o.items.forEach((it,i)=>{ const len=it.value/tot*C, gap=o.items.length>1?Math.min(3,len*0.3):0;
    s+=`<circle class="seg" data-len="${Math.max(len-gap,0.01)}" data-c="${C}" cx="${S/2}" cy="${S/2}" r="${r}" fill="none" stroke="${it.color}" stroke-width="${T}" stroke-dasharray="0 ${C}" stroke-dashoffset="${-acc}" transform="rotate(-90 ${S/2} ${S/2})" style="transition-delay:${300+i*140}ms"/>`;
    acc+=len; });
  return `<div style="position:relative;width:${S}px;height:${S}px;flex:none">
    <svg width="${S}" height="${S}" style="filter:drop-shadow(0 10px 30px rgba(0,0,0,.35))">${s}</svg>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">${o.center}</div></div>`;
}
function legendRows(items, unit='M', dec=2){
  const tot=items.reduce((a,b)=>a+b.value,0);
  return items.map((it,i)=>`<div class="rv" style="--d:${400+i*90};display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.06)">
    <span style="width:12px;height:12px;border-radius:50%;background:${it.color};box-shadow:0 0 10px ${it.color}"></span>
    <span style="flex:1;font-size:16px">${it.label}</span>
    <span class="num" style="font-size:16px;font-weight:700">${f(it.value,dec)}${unit?' '+unit:''}</span>
    <span class="num" style="width:62px;text-align:right;font-size:15px;color:${it.color};font-weight:700">${f(it.value/tot*100,1)}%</span></div>`).join('');
}

/* ---------- slides ---------- */
function sCover(){
  const logo = LOGO ? `<div class="logo-chip"><img src="data:image/jpeg;base64,${LOGO}"></div>` : `<div class="logo-chip"><span class="t">KARANDAAZ</span></div>`;
  const p=D.pool, inc=D.income;
  return `<div class="orb"></div>${rings}
  <svg class="pat" width="1600" height="300" viewBox="0 0 1600 300">${pattern(32,6,50,7,0.48,0.45)}</svg>
  <div class="inner">
    <div class="rv" style="--d:0">${logo}</div>
    <div class="eyebrow rvx" style="--d:150;margin-top:56px"><span class="no">Q1</span>${D.period} &nbsp;·&nbsp; Board Presentation</div>
    <h1 class="rv" style="--d:250">Treasury Committee<br><em>Meeting</em></h1>
    <div class="date rv" style="--d:400">${D.meeting_date}</div>
    <div class="kstrip">
      <div class="k rv" style="--d:600"><div class="v num"><small>PKR</small><span data-count="${p.total}" data-dec="2"></span><small style="margin-left:6px">M</small></div><div class="l">Treasury Investment Pool</div></div>
      <div class="k rv" style="--d:720"><div class="v num"><small>PKR</small><span data-count="${M(inc.income_total)}" data-dec="1"></span><small style="margin-left:6px">M</small></div><div class="l">Q1 Treasury Income</div></div>
      <div class="k rv" style="--d:840"><div class="v num"><span data-count="${p.weighted_rate}" data-dec="2" data-suffix="%"></span></div><div class="l">Weighted Pool Rate</div></div>
    </div>
  </div>`;
}
function sEconomy(i){
  const e=D.economy;
  const stats=e.stats.map((s,k)=>`<div class="card stat rv" style="--d:${200+k*110}"><div class="glow"></div>
    <div class="v num" style="color:${[COL.orange,'#fff',COL.gold,COL.sky][k]}"><span data-count="${s.value}" data-dec="${s.dec}" data-prefix="${s.prefix}" data-suffix="${s.suffix}"></span></div>
    <div class="l">${s.label}</div><div class="s">${s.sub}</div></div>`).join('');
  const max=Math.max(...e.bars.map(b=>b.value))*1.08;
  const bars=e.bars.map((b,k)=>`<div class="hb rv" style="--d:${700+k*150}"><div class="top"><span>${b.label}</span><b class="num" style="color:${b.color}">${f(b.value,1)}%</b></div>
    <div class="track"><div class="fill" style="--d:${700+k*150};width:${b.value/max*100}%;background:linear-gradient(90deg,${b.color}66,${b.color})"></div></div></div>`).join('');
  return `${rings}${hd(i+1,'Macro Snapshot',e.title,e.subtitle)}
  <div class="grid" style="grid-template-columns:repeat(4,1fr)">${stats}</div>
  <div class="grid" style="grid-template-columns:1.25fr 1fr;margin-top:24px">
    <div class="card rv" style="--d:600;height:410px"><div class="ct"><span class="dot"></span>Investor Confidence & Capital Markets</div>
      <ul class="bl">${e.markets.map((m,k)=>`<li class="rv" style="--d:${750+k*120}">${m}</li>`).join('')}</ul></div>
    <div class="card rv" style="--d:680;height:410px"><div class="ct"><span class="dot"></span>Inflation & Monetary Policy</div>
      <div style="margin-top:14px">${bars}</div>
      <div class="callout rv" style="--d:1100">${e.mpc_note}</div></div>
  </div>${ft(i)}`;
}
function sPolicy(i){
  const p=D.policy;
  const chips=`<div class="chips">${p.chips.map((c,k)=>`<div class="chip rv ${k==2?'hot':''}" style="--d:${200+k*100}"><div class="v num">${c.value}</div><div class="l">${c.label}</div></div>`).join('')}</div>`;
  const chart=lineChart({id:'pol',w:900,h:500,labels:p.labels,min:8,max:22,step:2,vline:6,vlabel:'FY2027 (illustrative)',pr:40,
    series:[{values:p.actual,color:COL.sky,area:true,w:4},{values:p.hold,color:COL.slate,dash:'2 9',w:3.5},{values:p.ease,color:COL.orange,dash:'2 9',w:3.5}]});
  return `${rings}${hd(i+1,'Monetary Policy','SBP Policy Rate — Trend & Outlook','Policy rate path since June 2024, with an illustrative outlook for FY2027',chips)}
  <div class="grid" style="grid-template-columns:960px 1fr">
    <div class="card rv" style="--d:300;padding:22px 24px 18px">
      <div class="legend" style="margin:0 0 6px 58px"><span><i style="background:${COL.sky}"></i>Policy Rate (Actual)</span><span style="color:${COL.slate}"><i class="dash"></i>${p.hold_name}</span><span style="color:${COL.orange}"><i class="dash"></i>${p.ease_name}</span></div>
      ${chart}
      <div class="note" style="margin:4px 0 0 58px">${p.source}</div></div>
    <div class="card rv" style="--d:450;display:flex;flex-direction:column"><div class="ct"><span class="dot"></span>FY2027 Outlook — What Analysts Are Watching</div>
      <ul class="bl sky sm" style="flex:1">${p.outlook.map((m,k)=>`<li class="rv" style="--d:${600+k*110}">${m}</li>`).join('')}</ul>
      <div class="note rv" style="--d:1200;font-style:italic;padding:12px 16px;border-radius:12px;background:rgba(255,255,255,.04);border:1px dashed rgba(255,255,255,.18)">${p.disclaimer}</div></div>
  </div>${ft(i)}`;
}
function sPkrv(i){
  const k=D.pkrv;
  const tiles=[['1M',k.m1,0,COL.orange],['3M',k.m3,0,'#ffffff'],['6M',k.m6,1,COL.sky],['12M',k.m12,1,COL.gold],['2Y',k.y2,1,COL.teal]].map((t,j)=>{
    const last=t[1][t[1].length-1], base=t[1][t[2]], bps=Math.round((last-base)*100);
    return `<div class="card rv" style="--d:${200+j*90};padding:18px 22px;flex:1">
      <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:14px;font-weight:900;letter-spacing:2px;color:${t[3]}">${t[0]} PKRV</span>
      <span class="num" style="font-size:12.5px;font-weight:700;padding:3px 9px;border-radius:12px;background:${bps>=0?'rgba(246,139,30,.16)':'rgba(118,196,227,.16)'};color:${bps>=0?COL.orange:COL.sky}">${bps>=0?'▲':'▼'} ${Math.abs(bps)} bps</span></div>
      <div class="num" style="font-size:38px;font-weight:900;margin-top:8px"><span data-count="${last}" data-dec="2" data-suffix="%"></span></div>
      <div class="note" style="margin-top:2px">since Jan '26</div></div>`; }).join('');
  const c1=lineChart({id:'st',w:672,h:400,labels:k.short_labels,min:10,max:12.5,step:0.5,dec:1,pr:84,
      series:[{values:k.m1,color:COL.orange,endLabel:true,lo:-10},{values:k.m3,color:'#ffffff',endLabel:true,lo:-24}]});
  const c2=lineChart({id:'lt',w:672,h:400,labels:k.long_labels,min:10,max:13,step:0.5,dec:1,pr:84,every:1,
      series:[{values:k.m6,color:COL.sky,endLabel:true,lo:26},{values:k.m12,color:COL.gold,endLabel:true,lo:-4},{values:k.y2,color:COL.teal,endLabel:true,lo:-32}]});
  return `${rings}${hd(i+1,'Secondary Market Yields','Short & Long-Term Trend Analysis of PKRVs','Month-end PKRV rates · latest as at '+k.as_of)}
  <div style="display:flex;gap:18px">${tiles}</div>
  <div class="grid" style="grid-template-columns:1fr 1fr;margin-top:20px">
    <div class="card rv" style="--d:500;padding:20px 22px 10px"><div style="display:flex;justify-content:space-between;align-items:center"><div class="ct" style="margin:0"><span class="dot"></span>Short-Term Trend</div>
      <div class="legend"><span><i style="background:${COL.orange}"></i>1M</span><span><i style="background:#fff"></i>3M</span></div></div>${c1}</div>
    <div class="card rv" style="--d:600;padding:20px 22px 10px"><div style="display:flex;justify-content:space-between;align-items:center"><div class="ct" style="margin:0"><span class="dot"></span>Long-Term Trend</div>
      <div class="legend"><span><i style="background:${COL.sky}"></i>6M</span><span><i style="background:${COL.gold}"></i>12M</span><span><i style="background:${COL.teal}"></i>2Y</span></div></div>${c2}</div>
  </div>${ft(i)}`;
}
function sPool(i){
  const p=D.pool, mx=Math.max(...p.accounts.map(a=>a[3]));
  const items=p.buckets.map(b=>({label:b.name,value:b.value,color:BUCKET[b.key]}));
  const rows=p.accounts.map((a,k)=>`<tr class="rv ${p.highlight.includes(a[0])?'hl':''}" style="--d:${300+k*35};height:21.6px">
    <td>${a[0]}</td><td><span class="pill" style="background:${BUCKET[a[2]]}22;color:${BUCKET[a[2]]};border:1px solid ${BUCKET[a[2]]}66">${a[2]}</span></td>
    <td class="r">${f(a[1],2)}%</td><td class="r"><div class="mini"><span class="num">${f(a[3],2)}</span><div class="t"><div style="--d:${300+k*35};width:${Math.max(a[3]/mx*100,0.8)}%;background:${BUCKET[a[2]]}"></div></div></div></td></tr>`).join('');
  return `${rings}${hd(i+1,'Investment Pool','Investment Pool as of '+p.as_of,'Treasury Investment Pool (excluding grants) · PKR in Million')}
  <div class="grid" style="grid-template-columns:520px 1fr">
    <div class="card rv" style="--d:200;display:flex;flex-direction:column;align-items:center;height:606px">
      <div class="ct" style="align-self:flex-start"><span class="dot"></span>Pool by Bucket</div>
      ${donut({size:256,thick:32,items,center:`<div style="font-size:12px;letter-spacing:2.5px;color:var(--sky);text-transform:uppercase">Grand Total</div><div class="num" style="font-size:34px;font-weight:900;margin-top:4px"><span data-count="${p.total}" data-dec="2"></span></div><div style="font-size:14px;color:var(--faint)">PKR Million</div>`})}
      <div style="width:100%;margin-top:10px">${legendRows(items)}</div>
      <div class="chip hot rv" style="--d:900;margin-top:auto;width:100%;display:flex;justify-content:space-between;align-items:center;text-align:left;padding:12px 20px"><div class="l" style="margin:0">Weighted average rate</div><div class="v num" style="font-size:28px">${f(p.weighted_rate,2)}%</div></div>
    </div>
    <div class="card rv" style="--d:300;padding:20px 26px;height:606px">
      <table class="tbl"><thead><tr><th>Account</th><th>Bucket</th><th class="r">Rate</th><th class="r">PKR Mn</th></tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr><td>Grand Total</td><td></td><td class="r o">${f(p.weighted_rate,2)}%</td><td class="r o" style="padding-right:140px">${f(p.total,2)}</td></tr></tfoot></table>
    </div>
  </div>${ft(i)}`;
}
function sGrants(i){
  const g=D.grants;
  const items=[{label:'Grant Funds (GF)',value:g.gf,color:COL.sky},{label:'FIP',value:g.fip,color:COL.orange}];
  const usd=g.accounts[0][1];
  const rows=g.accounts.map((a,k)=>`<tr class="rv" style="--d:${300+k*60};height:38px"><td>${a[0]}</td>
    <td class="r">${a[1]==null?'<span class="muted">–</span>':f(a[1],2)}</td><td class="r">${a[2]==null?'<span class="muted">–</span>':f(a[2],2)}</td>
    <td class="r" style="font-weight:700">${f((a[1]||0)+(a[2]||0),2)}</td></tr>`).join('');
  return `${rings}${hd(i+1,'Grant Funds','Grants Position as of '+g.as_of,'Grant funds including GF & FIP · PKR in Million')}
  <div class="grid" style="grid-template-columns:1fr 560px">
    <div class="card rv" style="--d:200;padding:24px 30px;height:606px;display:flex;flex-direction:column">
      <table class="tbl"><thead><tr><th>Accounts</th><th class="r">GF</th><th class="r">FIP</th><th class="r">Grand Total</th></tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr><td>Grand Total</td><td class="r">${f(g.gf,2)}</td><td class="r">${f(g.fip,2)}</td><td class="r o">${f(g.total,2)}</td></tr></tfoot></table>
      <div class="note rv" style="--d:1000;margin-top:auto">${g.note}</div>
    </div>
    <div class="card rv" style="--d:300;display:flex;flex-direction:column;align-items:center;height:606px">
      <div class="ct" style="align-self:flex-start"><span class="dot"></span>Grant Funds Mix</div>
      ${donut({size:270,thick:36,items,center:`<div style="font-size:12px;letter-spacing:2.5px;color:var(--sky);text-transform:uppercase">Total Grants</div><div class="num" style="font-size:36px;font-weight:900;margin-top:4px"><span data-count="${g.total}" data-dec="2"></span></div><div style="font-size:14px;color:var(--faint)">PKR Million</div>`})}
      <div style="width:100%;margin-top:18px">${legendRows(items)}</div>
      <div class="callout rv" style="--d:900;width:100%;margin-top:auto">The <b>BAFL USD account</b> holds <b>PKR ${f(usd,2)} M</b> — <b>${f(usd/g.total*100,1)}%</b> of all grant funds.</div>
    </div>
  </div>${ft(i)}`;
}
function sBanks(i){
  const b=D.banks, segCols=[COL.sky,'#3BA3C9',COL.gold,'#ffffff','#9fb6c3','#c4a35a','#5d7a8a',COL.teal,COL.orange];
  const rows=b.rows.map((r,k)=>{ const u=r[5]; const warn=u!=null&&u>=90;
    return `<tr class="rv" style="--d:${250+k*60};height:37px">
    <td class="c muted">${k+1}</td><td style="font-weight:700"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${segCols[k]};margin-right:10px"></span>${r[0]}</td>
    <td class="c">${r[1]?`<span class="badge">${r[1]}</span>`:'<span class="muted">–</span>'}</td>
    <td class="r">${f(r[2],0)}</td><td class="r">${f(r[3],2)}%</td><td class="r">${r[4]==null?'<span class="muted">–</span>':f(r[4],2)+'%'}</td>
    <td>${u==null?'<span class="muted" style="padding-left:6px">–</span>':`<div class="mini" style="justify-content:flex-start"><div class="t" style="width:110px"><div style="--d:${250+k*60};width:${u}%;background:${warn?COL.orange:COL.sky}"></div></div><span class="num" style="font-weight:700;color:${warn?COL.orange:'#fff'}">${u}%</span></div>`}</td>
    <td class="r">${r[6]==null?'<span class="muted">–</span>':f(r[6],0)}</td><td class="r" style="${warn?'color:'+COL.orange+';font-weight:700':''}">${r[7]==null?'<span class="muted">–</span>':f(r[7],0)}</td></tr>`;}).join('');
  const tot=b.rows.reduce((a,r)=>a+r[2],0); let acc=0;
  const segs=b.rows.map((r,k)=>{ const w=r[2]/tot*100; const html=`<rect class="bar" style="--d:${600+k*80};transform-origin:left center" x="${acc}%" y="0" width="${w}%" height="44" fill="${segCols[k]}" stroke="#062b3f" stroke-width="2"/>${(w/100*900)>(String(r[0]).length+4)*8.4+14?`<text x="${acc+w/2}%" y="28" text-anchor="middle" font-size="13" font-weight="900" fill="#03131c">${r[0]} ${f(r[3],0)}%</text>`:''}`; acc+=w; return html; }).join('');
  const hot=b.rows.filter(r=>r[5]!=null&&r[5]>=90);
  return `${rings}${hd(i+1,'Counterparty Exposure','Bank-wise KRN Treasury Portfolio Analysis','As of '+b.as_of+' · PKR in Million')}
  <div class="card rv" style="--d:200;padding:22px 28px 16px">
    <table class="tbl"><thead><tr><th class="c">#</th><th>Bank</th><th class="c">LT Rating</th><th class="r">Balance</th><th class="r">KRN Portfolio %</th><th class="r">Rate Offered</th><th>Utilization of Limit</th><th class="r">Institutional Limit</th><th class="r">Under / (Over)</th></tr></thead>
    <tbody>${rows}</tbody>
    <tfoot><tr><td></td><td>Total</td><td></td><td class="r o">${f(b.total,0)}</td><td class="r">100%</td><td></td><td></td><td></td><td></td></tr></tfoot></table>
  </div>
  <div class="grid" style="grid-template-columns:1fr 470px;margin-top:20px">
    <div class="card rv" style="--d:500;padding:20px 26px"><div class="ct"><span class="dot"></span>Portfolio Composition</div>
      <svg width="100%" height="44" style="border-radius:10px;overflow:hidden;display:block"><g>${segs}</g></svg>
      <div class="note" style="margin-top:12px">${b.notes.map(n=>'• '+n).join('<br>')}</div></div>
    <div class="card rv" style="--d:600;padding:20px 26px;background:linear-gradient(140deg,rgba(246,139,30,.16),rgba(246,139,30,.04));border-color:rgba(246,139,30,.4)">
      <div class="ct" style="color:var(--orange)"><span class="dot"></span>Limit Watch</div>
      ${hot.length?hot.map(r=>`<div style="font-size:17px;line-height:1.5"><b style="font-size:30px;font-weight:900;color:var(--orange)">${r[5]}%</b>&nbsp; of the <b>${r[0]}</b> institutional limit is utilised — headroom of only <b>PKR ${f(r[7],0)} M</b>.</div>`).join(''):'<div style="font-size:17px">All banks are comfortably within institutional limits.</div>'}
    </div>
  </div>${ft(i)}`;
}
function sIncome(i){
  const n=D.income, cols=[COL.sky,COL.gold,COL.orange];
  const items=n.rows.map((r,k)=>({label:r[0],value:M(r[2]),color:cols[k]}));
  const rows=n.rows.map((r,k)=>`<tr class="rv" style="--d:${700+k*100};height:44px"><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cols[k]};margin-right:12px"></span>${r[0]}</td><td class="r">${f(M(r[1]),2)}</td><td class="r" style="font-weight:700">${f(M(r[2]),2)}</td><td class="r" style="color:${cols[k]};font-weight:700">${f(r[2]/n.income_total*100,1)}%</td></tr>`).join('');
  const spark=[[70,40,8,COL.gold],[118,96,9,'#fff'],[150,30,7,'#fff'],[220,120,6,COL.orange],[86,170,8,'#fff'],[190,190,10,COL.gold]].map(s=>`<div class="spark" style="right:${s[0]}px;top:${s[1]}px;width:${s[2]}px;height:${s[2]}px;background:${s[3]};transform:rotate(45deg)"></div>`).join('');
  return `${rings}${hd(i+1,'Performance','Treasury Income — FY 26-27',n.headline)}
  <div class="grid" style="grid-template-columns:600px 1fr">
    <div class="card hero rv" style="--d:200;height:320px;padding:38px 40px">${spark}
      <div style="font-size:15px;letter-spacing:5px;color:var(--sky);font-weight:700">PKR</div>
      <div class="big num" style="margin-top:6px"><span data-count="${M(n.income_total)}" data-dec="1" data-suffix="M"></span></div>
      <div style="font-size:22px;font-weight:900;letter-spacing:3px;margin-top:10px">TREASURY INCOME · Q1</div>
      <div style="font-size:14px;color:var(--muted);margin-top:16px;letter-spacing:.5px">Strategic contribution &nbsp;·&nbsp; Revenue generation &nbsp;·&nbsp; Capital preservation</div></div>
    <div class="card rv" style="--d:320;height:320px;display:flex;gap:34px;align-items:center;padding:22px 34px">
      ${donut({size:240,thick:30,items,center:`<div style="font-size:11.5px;letter-spacing:2px;color:var(--sky);text-transform:uppercase">Q1 Income</div><div class="num" style="font-size:28px;font-weight:900;margin-top:4px">${f(M(n.income_total),2)}</div><div style="font-size:13px;color:var(--faint)">PKR Million</div>`})}
      <div style="flex:1"><div class="ct"><span class="dot"></span>Income Mix · Q1</div>${legendRows(items)}</div></div>
  </div>
  <div class="card rv" style="--d:550;margin-top:24px;padding:22px 30px">
    <table class="tbl"><thead><tr><th>Type</th><th class="r">Opening Balance (PKR Mn)</th><th class="r">Q1 Income (PKR Mn)</th><th class="r">Share of Income</th></tr></thead>
    <tbody>${rows}</tbody>
    <tfoot><tr><td>Total</td><td class="r">${f(M(n.opening_total),2)}</td><td class="r o">${f(M(n.income_total),2)}</td><td class="r">100%</td></tr></tfoot></table>
  </div>${ft(i)}`;
}
function sForecast(i){
  const F=D.forecast, cols=[COL.sky,COL.gold,COL.orange];
  const W=944,H=330,P={l:56,r:16,t:34,b:44},iw=W-P.l-P.r,ih=H-P.t-P.b,max=500,y=v=>P.t+ih-v/max*ih,bw=118,gap=iw/4;
  let g=''; for(let v=0;v<=max;v+=100) g+=`<line class="gl" x1="${P.l}" x2="${W-P.r}" y1="${y(v)}" y2="${y(v)}"/><text class="ax" x="${P.l-12}" y="${y(v)+4.5}" text-anchor="end">${v}</text>`;
  ['Q1','Q2','Q3','Q4'].forEach((q,k)=>{ const cx=P.l+gap*k+gap/2, x0=cx-bw/2; let base=0; const actual=k===0;
    F.rows.forEach((r,j)=>{ const v=M(r[2+k]); const y1=y(base+v), h=y(base)-y1;
      g+=`<rect class="bar" style="--d:${k*160+j*90}" x="${x0}" y="${y1}" width="${bw}" height="${Math.max(h,1)}" fill="${cols[j]}" fill-opacity="${actual?1:.42}" ${actual?'':`stroke="${cols[j]}" stroke-width="1.5" stroke-dasharray="4 4"`}/>`; base+=v; });
    g+=`<text class="pt" style="--d:${900+k*160}" x="${cx}" y="${y(base)-12}" text-anchor="middle" font-size="19" font-weight="900" fill="#fff">${f(M(F.q_totals[k]),2)}</text>`;
    g+=`<text x="${cx}" y="${H-P.b+24}" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">${q}</text><text x="${cx}" y="${H-P.b+41}" text-anchor="middle" font-size="11.5" letter-spacing="2" fill="${actual?COL.orange:'rgba(255,255,255,.5)'}">${actual?'ACTUAL':'FORECAST'}</text>`;
  });
  const rows=F.rows.map((r,j)=>`<tr class="rv" style="--d:${800+j*90};height:34px"><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${cols[j]};margin-right:12px"></span>${r[0]}</td><td class="r">${f(M(r[1]),2)}</td>
    ${[2,3,4,5].map(c=>`<td class="r" ${c==2?'style="color:'+COL.orange+'"':''}>${f(M(r[c]),2)}</td>`).join('')}<td class="r" style="font-weight:900">${f(M(r[2]+r[3]+r[4]+r[5]),2)}</td></tr>`).join('');
  const fcst=F.q_totals.slice(1).reduce((a,b)=>a+b,0);
  return `${rings}${hd(i+1,'Outlook','Treasury Income Forecast — FY 2026-27','Q1 actual with Q2–Q4 forecast by income bucket · PKR in Million')}
  <div class="grid" style="grid-template-columns:1fr 430px">
    <div class="card rv" style="--d:200;padding:18px 24px 6px">
      <div style="display:flex;justify-content:space-between;align-items:center"><div class="ct" style="margin:0"><span class="dot"></span>Quarterly Income Build-up</div>
      <div class="legend">${F.rows.map((r,j)=>`<span><i style="background:${cols[j]}"></i>${r[0].replace(' - EAGR','')}</span>`).join('')}</div></div>
      <svg width="${W}" height="${H}">${g}</svg></div>
    <div class="card hero rv" style="--d:320;display:flex;flex-direction:column;justify-content:center;padding:30px 34px">
      <div style="font-size:13px;letter-spacing:3px;color:var(--sky);font-weight:700;text-transform:uppercase">Projected FY 26-27 Income</div>
      <div class="big num" style="font-size:76px;margin-top:10px"><span data-count="${M(F.grand_total)}" data-dec="1"></span></div>
      <div style="font-size:16px;color:var(--muted)">PKR Million</div>
      <div style="display:flex;gap:14px;margin-top:26px">
        <div style="flex:1;padding:14px 16px;border-radius:14px;background:rgba(0,0,0,.2)"><div class="num" style="font-size:24px;font-weight:900;color:var(--orange)">${f(M(F.q_totals[0]),1)}</div><div class="note">Q1 actual</div></div>
        <div style="flex:1;padding:14px 16px;border-radius:14px;background:rgba(0,0,0,.2)"><div class="num" style="font-size:24px;font-weight:900">${f(M(fcst),1)}</div><div class="note">Q2–Q4 forecast</div></div></div>
      <div class="note" style="margin-top:18px">Average balance for the year: <b style="color:#fff">PKR ${f(M(F.avg_total),2)} M</b></div>
    </div>
  </div>
  <div class="card rv" style="--d:600;margin-top:20px;padding:18px 28px">
    <table class="tbl"><thead><tr><th>Income Bucket</th><th class="r">Avg Balance (Year)</th><th class="r" style="color:var(--orange)">Q1 · Actual</th><th class="r">Q2 · Fcst</th><th class="r">Q3 · Fcst</th><th class="r">Q4 · Fcst</th><th class="r">Grand Total</th></tr></thead>
    <tbody>${rows}</tbody>
    <tfoot><tr><td>Total</td><td class="r">${f(M(F.avg_total),2)}</td>${F.q_totals.map((q,k)=>`<td class="r ${k==0?'o':''}">${f(M(q),2)}</td>`).join('')}<td class="r o">${f(M(F.grand_total),2)}</td></tr></tfoot></table>
  </div>${ft(i)}`;
}
function sClose(){
  return `<div class="orb" style="left:-240px;right:auto;top:auto;bottom:-300px"></div>${rings}
  <svg class="pat" width="1600" height="300" viewBox="0 0 1600 300">${pattern(32,6,50,23,0.5,0.45)}</svg>
  <div class="inner" style="position:absolute;left:96px;right:96px;top:230px;text-align:center;z-index:2">
    <div class="eyebrow rv" style="--d:0;justify-content:center">Treasury Committee &nbsp;·&nbsp; ${D.period}</div>
    <h1 class="rv" style="--d:150;font-size:118px;font-weight:900;letter-spacing:-3px;margin-top:22px;line-height:1">Thank <em style="font-style:normal;background:linear-gradient(90deg,#f68b1e,#FFC107);-webkit-background-clip:text;background-clip:text;color:transparent">you</em></h1>
    <div class="date rv" style="--d:300;font-size:26px;font-weight:300;font-style:italic;color:var(--muted);margin-top:22px">Questions &amp; discussion</div>
  </div>`;
}

/* ---------- build ---------- */
const stage=document.getElementById('stage');
const builders=[sCover,sEconomy,sPolicy,sPkrv,sPool,sGrants,sBanks,sIncome,sForecast,sClose];
stage.insertAdjacentHTML('beforeend', builders.map((b,i)=>`<section class="slide ${i==0||i==TOTAL-1?'cover':''}">${b(i)}</section>`).join(''));
const slides=[...stage.querySelectorAll('.slide')];
const dots=document.getElementById('dots');
dots.innerHTML=slides.map((_,i)=>`<b data-i="${i}" title="Slide ${i+1}"></b>`).join('');
let cur=0;

function countUp(el){
  const to=parseFloat(el.dataset.count), dec=parseInt(el.dataset.dec||0), pre=el.dataset.prefix||'', suf=el.dataset.suffix||'', t0=performance.now(), dur=1500;
  (function step(t){ const p=Math.min((t-t0)/dur,1), e=1-Math.pow(1-p,4);
    el.textContent=pre+f(to*e,dec)+suf; if(p<1) requestAnimationFrame(step); })(t0);
}
function animate(s){
  s.querySelectorAll('[data-count]').forEach(el=>{ el.textContent=(el.dataset.prefix||'')+f(0,parseInt(el.dataset.dec||0))+(el.dataset.suffix||''); setTimeout(()=>countUp(el),350); });
  s.querySelectorAll('path.anim').forEach(p=>{ const L=p.getTotalLength(); if(!L) return; const dash=p.dataset.dash;
    p.style.transition='none'; p.style.strokeDasharray=L+' '+L; p.style.strokeDashoffset=L; p.getBoundingClientRect();
    p.style.transition=`stroke-dashoffset 1.8s cubic-bezier(.3,.7,.2,1) ${(+p.dataset.delay||0)+350}ms`; p.style.strokeDashoffset=0;
    if(dash){ setTimeout(()=>{ p.style.transition='none'; p.style.strokeDasharray=dash; p.style.strokeDashoffset=0; }, 2300+(+p.dataset.delay||0)); }
  });
  s.querySelectorAll('circle.seg').forEach(c=>{ const C=c.dataset.c; c.style.transition='none'; c.setAttribute('stroke-dasharray','0 '+C); c.getBoundingClientRect(); c.style.transition='';
    requestAnimationFrame(()=>requestAnimationFrame(()=>c.setAttribute('stroke-dasharray',c.dataset.len+' '+C))); });
}
function go(n, force){
  n=Math.max(0,Math.min(TOTAL-1,n)); if(n===cur && !force) return;
  slides.forEach((s,i)=>{ s.classList.remove('active'); s.classList.toggle('before', i<n); });
  void stage.offsetWidth;
  slides[n].classList.add('active'); cur=n; animate(slides[n]);
  [...dots.children].forEach((d,i)=>d.classList.toggle('on',i===n));
  document.getElementById('count').textContent=String(n+1).padStart(2,'0')+' / '+String(TOTAL).padStart(2,'0');
  document.getElementById('prog').style.width=((n+1)/TOTAL*100)+'%';
}
let lastW=-1;
function fit(){
  const vp=document.getElementById('viewport'), w=vp.clientWidth||window.innerWidth, h=vp.clientHeight||(window.innerHeight-60);
  if(w<20||h<20){ lastW=0; return; }   // tab hidden: keep last scale, replay when shown
  const s=Math.min(w/1600,h/900)*0.985; stage.style.transform=`translate(-50%,-50%) scale(${s})`;
  if(lastW===0) go(cur,true);          // replay when the tab becomes visible
  lastW=w;
}
document.getElementById('prev').onclick=()=>go(cur-1);
document.getElementById('next').onclick=()=>go(cur+1);
dots.onclick=e=>{ if(e.target.dataset.i!=null) go(+e.target.dataset.i); };
function toggleFS(){ const d=document; if(!d.fullscreenElement){ (d.documentElement.requestFullscreen||d.documentElement.webkitRequestFullscreen).call(d.documentElement); } else { (d.exitFullscreen||d.webkitExitFullscreen).call(d); } }
document.getElementById('fs').onclick=toggleFS;
document.addEventListener('keydown',e=>{
  if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();go(cur+1);}
  else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();go(cur-1);}
  else if(e.key==='Home') go(0); else if(e.key==='End') go(TOTAL-1);
  else if(e.key==='f'||e.key==='F') toggleFS();
});
let tx=null; stage.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:true});
stage.addEventListener('touchend',e=>{ if(tx==null) return; const dx=e.changedTouches[0].clientX-tx; if(Math.abs(dx)>50) go(cur+(dx<0?1:-1)); tx=null; });
stage.addEventListener('click',()=>window.focus());
window.addEventListener('resize',fit);
document.addEventListener('fullscreenchange',fit);
fit(); go(0,true);
if(window.ResizeObserver) new ResizeObserver(fit).observe(document.getElementById('viewport'));
setInterval(fit,600);
</script>
</body></html>'''


def build_tc_deck_html(logo_b64_str):
    """Injects slide data + logo into the presentation template."""
    return (TC_DECK_TEMPLATE
            .replace("__DECK_DATA__", json.dumps(TC_DECK_DATA))
            .replace("__LOGO_B64__", logo_b64_str or ""))

# ---------------------------------------------------------
# MAIN DASHBOARD CONTENT
# ---------------------------------------------------------
CHART_FONT = dict(family="Chivo, sans-serif", color="#FFFFFF", size=18)

with st.spinner("Rendering Visualizations..."):

    # SBP Rolling Banner
    st.markdown(clean_html(f"""
    <div class="sbp-marquee">
        <span>
            <a href="https://www.sbp.org.pk/our-operations/monetary-policy" target="_blank">
                <span style="color: #f68b1e; margin-right: 8px; font-weight: 700;">SBP MONETARY POLICY UPDATE:</span>
                The current Monetary Policy Rate is <b style="color:#FFFFFF;">{mpr_rate:.2f}%</b>. 
                Next MPC meeting is scheduled for <b style="color:#FFFFFF;">{next_mpr_date}</b>. 
                <span style="color:#FFFFFF; opacity:0.9;">Summary: The Monetary Policy Committee continues to monitor inflation targets and economic indicators.</span> 
                &nbsp;&nbsp;Click here to read the full policy statement on the official SBP website.
            </a>
        </span>
    </div>
    """), unsafe_allow_html=True)

    # Header Card
    st.markdown(clean_html(f"""
    <div class="header-container">
        <div class="glow-line"></div>
        <div class="header-card">
            {header_logo_html}
            Treasury Portfolio Summary (FY26-27)
        </div>
        <div class="glow-line"></div>
    </div>
    """), unsafe_allow_html=True)

    # Tab styling + tab container (Dashboard | Treasury Committee Presentation)
    st.markdown(clean_html("""
    <style>
    .stTabs [role="tablist"] { display: flex !important; gap: 14px !important; justify-content: center !important; border-bottom: none !important; box-shadow: none !important; margin-bottom: 18px; overflow: visible !important; }
    .stTabs [role="tab"] { background: #FFFFFF !important; border: 2px solid #0f6286 !important; border-radius: 14px !important; padding: 10px 28px !important; height: auto !important; margin: 0 !important; transition: all 0.2s ease; cursor: pointer; }
    .stTabs [role="tab"]:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(15, 98, 134, 0.15); }
    .stTabs [role="tab"] p { font-size: 19px !important; font-weight: 700 !important; color: #0f6286 !important; margin: 0 !important; }
    .stTabs [role="tab"][aria-selected="true"] { background: #0f6286 !important; border-color: #f68b1e !important; box-shadow: 0 4px 12px rgba(15, 98, 134, 0.25); }
    .stTabs [role="tab"][aria-selected="true"] p { color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"], .stTabs .react-aria-SelectionIndicator { display: none !important; }
    </style>
    """), unsafe_allow_html=True)

    tab_dash, tab_tc = st.tabs(["Treasury Dashboard", "Treasury Committee Presentation"])

    with tab_dash:
        col_e1, col_date, col_e2 = st.columns([1, 0.3, 1])
        with col_date:
            selected_q = st.selectbox("", ["Q1", "Q2", "Q3", "Q4"], label_visibility="collapsed")

        q_ctx = quarter_data[selected_q]
        q_rates_list = get_quarter_rates(selected_q)

        # DYNAMIC BREAKDOWN VALUES FOR THE OVERLAY MODAL
        osr_val = osr_q1 if selected_q == 'Q1' else 0.0
        lr_val = lr_funds if selected_q == 'Q1' else 0.0
        esc_val = esc_q1 if selected_q == 'Q1' else 0.0

        # 4 Centered Top KPI Cards (FIRST CARD HAS CSS CLICKABLE BRANCHING ICON & INTERACTIVE MODAL OVERLAY)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
        with kpi1:
            st.markdown(clean_html(f"""
            <div>
                <!-- HIDDEN CHECKBOX CONTROLS THE MODAL STATE IN PURE CSS -->
                <input type="checkbox" id="income-modal-toggle" style="display: none;">
            
                <div class='top-kpi-card' style='position: relative;'>
                    <label for="income-modal-toggle" class="icon-btn-hover" title="Click to view 3-Way Income Breakdown">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0f6286" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="6" y1="3" x2="6" y2="15"></line>
                            <circle cx="18" cy="6" r="3"></circle>
                            <circle cx="6" cy="18" r="3"></circle>
                            <path d="M18 9a9 9 0 0 1-9 9"></path>
                        </svg>
                    </label>
                    <div class='top-kpi-lbl'>TOTAL INCOME</div>
                    <div class='top-kpi-val'>{q_ctx['total_income']:,.2f} M</div>
                    <div class='top-kpi-sub'>Quarterly Income ({selected_q})</div>
                </div>

                <!-- CSS-ONLY INTERACTIVE OVERLAY WITH BLUR BACKDROP & 3 CONNECTED BRANCHING BOXES -->
                <div id="income-modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(10, 35, 55, 0.75); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); z-index: 9999999; justify-content: center; align-items: center;">
                    <!-- INVISIBLE LABEL COVERS ENTIRE BACKGROUND SO CLICKING OUTSIDE CLOSES MODAL -->
                    <label for="income-modal-toggle" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: default;"></label>
                
                    <div style="background: #0f6286; border: 2.5px solid #76C4E3; border-radius: 24px; padding: 36px; max-width: 920px; width: 92%; box-shadow: 0 25px 60px rgba(0,0,0,0.6); text-align: center; position: relative; animation: popUpModal 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275); z-index: 10;">
                    
                        <!-- CLOSE BUTTON -->
                        <label for="income-modal-toggle" class="close-hover" style="position: absolute; top: 16px; right: 22px; color: #FFFFFF; font-size: 32px; font-weight: 700; cursor: pointer;">&times;</label>
                    
                        <div style="color: #f68b1e; font-size: 18px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;">INCOME LEDGER BREAKDOWN ({selected_q})</div>
                        <div style="color: #FFFFFF; font-size: 34px; font-weight: 700; margin-top: 4px;">Total Income Allocation Structure</div>
                    
                        <!-- CENTRAL SOURCE NODE -->
                        <div style="margin-top: 24px; display: flex; justify-content: center;">
                            <div style="background: rgba(255,255,255,0.12); border: 2px solid #f68b1e; padding: 12px 32px; border-radius: 30px; color: #FFFFFF; font-size: 24px; font-weight: 700; display: inline-block; box-shadow: 0 0 20px rgba(246, 139, 30, 0.4);">
                                Total Income: PKR {q_ctx['total_income']:,.2f} M
                            </div>
                        </div>

                        <!-- 3 CONNECTING BRANCHING LINES -->
                        <div style="width: 100%; height: 60px; margin: 10px 0;">
                            <svg width="100%" height="60" viewBox="0 0 800 60" fill="none" preserveAspectRatio="none">
                                <path d="M400 0 L400 25 L150 25 L150 60" stroke="#f68b1e" stroke-width="3" stroke-dasharray="6 4"/>
                                <path d="M400 0 L400 60" stroke="#76C4E3" stroke-width="3" stroke-dasharray="6 4"/>
                                <path d="M400 0 L400 25 L650 25 L650 60" stroke="#FFC107" stroke-width="3" stroke-dasharray="6 4"/>
                                <circle cx="400" cy="0" r="6" fill="#FFFFFF"/>
                                <circle cx="150" cy="60" r="6" fill="#f68b1e"/>
                                <circle cx="400" cy="60" r="6" fill="#76C4E3"/>
                                <circle cx="650" cy="60" r="6" fill="#FFC107"/>
                            </svg>
                        </div>

                        <!-- 3 BRANCHED TEXT BOXES -->
                        <div style="display: flex; gap: 20px; justify-content: space-between; margin-top: 10px;">
                            <!-- 1. OSR INCOME -->
                            <div class="branched-box-hover" style="flex: 1; background: rgba(0,0,0,0.25); border: 2px solid #f68b1e; border-radius: 18px; padding: 22px;">
                                <div style="color: #f68b1e; font-size: 18px; font-weight: 700; text-transform: uppercase;">1. OSR Income</div>
                                <div style="color: #FFFFFF; font-size: 32px; font-weight: 700; margin-top: 8px;">{osr_val:,.2f} M</div>
                                <div style="color: rgba(255,255,255,0.75); font-size: 16px; margin-top: 6px;">Operational Savings Rate</div>
                            </div>

                            <!-- 2. LR INCOME -->
                            <div class="branched-box-hover" style="flex: 1; background: rgba(0,0,0,0.25); border: 2px solid #76C4E3; border-radius: 18px; padding: 22px;">
                                <div style="color: #76C4E3; font-size: 18px; font-weight: 700; text-transform: uppercase;">2. LR Income</div>
                                <div style="color: #FFFFFF; font-size: 32px; font-weight: 700; margin-top: 8px;">{lr_val:,.2f} M</div>
                                <div style="color: rgba(255,255,255,0.75); font-size: 16px; margin-top: 6px;">Liquidity Reserve</div>
                            </div>

                            <!-- 3. ESCROW INCOME -->
                            <div class="branched-box-hover" style="flex: 1; background: rgba(0,0,0,0.25); border: 2px solid #FFC107; border-radius: 18px; padding: 22px;">
                                <div style="color: #FFC107; font-size: 18px; font-weight: 700; text-transform: uppercase;">3. Escrow Income</div>
                                <div style="color: #FFFFFF; font-size: 32px; font-weight: 700; margin-top: 8px;">{esc_val:,.2f} M</div>
                                <div style="color: rgba(255,255,255,0.75); font-size: 16px; margin-top: 6px;">Escrow Account Returns</div>
                            </div>
                        </div>

                        <div style="color: rgba(255,255,255,0.65); font-size: 16px; margin-top: 26px;">Click anywhere outside this box to return to dashboard</div>
                    </div>
                </div>
            </div>

            <style>
            @keyframes popUpModal {{ from {{ transform: scale(0.85); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
            </style>
            """), unsafe_allow_html=True)

        with kpi2:
            st.markdown(clean_html(f"<div class='top-kpi-card'><div class='top-kpi-lbl'>TREASURY POOL</div><div class='top-kpi-val'>{q_ctx['treasury_pool']:,.2f} M</div><div class='top-kpi-sub'>Total Allocation ({selected_q})</div></div>"), unsafe_allow_html=True)
        with kpi3:
            st.markdown(clean_html(f"<div class='top-kpi-card'><div class='top-kpi-lbl'>FORECASTED INCOME</div><div class='top-kpi-val'>{q_ctx['forecasted_income']:,.2f} M</div><div class='top-kpi-sub'>Forecasted for {selected_q}</div></div>"), unsafe_allow_html=True)
        with kpi4:
            st.markdown(clean_html(f"<div class='top-kpi-card'><div class='top-kpi-lbl'>ANNUAL YIELD</div><div class='top-kpi-val'>{q_ctx['annual_yield']}</div><div class='top-kpi-sub'>Weighted Annual Yield</div></div>"), unsafe_allow_html=True)
    
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        bot_col1, bot_col2, bot_col3 = st.columns(3, gap="medium")

        # 1. Bank Profit Rates Card
        month_cols_html = "<div style='display: flex; justify-content: space-between; width: 100%; gap: 10px; margin-top: 10px; height: 100%;'>"
        for month_info in q_rates_list:
            rates_br = "<br>".join(month_info['rates'])
            month_cols_html += f"<div style='flex: 1; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 6px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>{month_info['month']}</div><div style='font-size: 21px; font-weight: 400; color: #FFFFFF; margin-top: 8px; line-height: 1.6;'>{rates_br}</div></div>"
        month_cols_html += "</div>"
        with bot_col1:
            st.markdown(clean_html(f"<div class='kpi-card' style='justify-content: center; height: 210px;'><div class='kpi-lbl'>BANK PROFIT RATES ({selected_q})</div>{month_cols_html}</div>"), unsafe_allow_html=True)

        # 2. MPR Rate Card
        mpr_split_html = (
            "<div style='display: flex; justify-content: space-between; width: 100%; height: 100%; align-items: center;'>"
            "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; border-right: 1px solid rgba(255,255,255,0.2); padding-right: 10px;'>"
            f"<div style='color:#FFFFFF; font-size: 47px; font-weight: 700; line-height: 1.1;'>{mpr_rate:.2f}%</div>"
            "<div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase; margin-top: 8px;'>MPR RATE</div>"
            f"<div style='font-size: 18px; font-weight: 400; color: #ffffff; opacity: 0.9; margin-top: 4px;'>Next Date: {next_mpr_date}</div>"
            "</div>"
            "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding-left: 10px;'>"
            f"<div style='color:#FFFFFF; font-size: 47px; font-weight: 700; line-height: 1.1;'>{mpr_rate - 1.5:.2f}%</div>"
            "<div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase; margin-top: 8px;'>BENCHMARK</div>"
            "<div style='font-size: 18px; font-weight: 400; color: #ffffff; opacity: 0.9; margin-top: 4px;'>MPR - 1.5%</div>"
            "</div></div>"
        )
        with bot_col2:
            st.markdown(clean_html(f"<div class='kpi-card' style='justify-content: center; height: 210px; padding: 10px;'>{mpr_split_html}</div>"), unsafe_allow_html=True)

        # 3. PKR Yields Card
        pkr_yields_html = (
            f"<div style='display: flex; justify-content: space-between; width: 100%; gap: 10px; margin-top: 10px; height: 100%;'>"
            f"<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>1M</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>{val_1m_str}</div></div>"
            f"<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>3M</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>{val_3m_str}</div></div>"
            f"<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>6M</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>{val_6m_str}</div></div>"
            f"<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>1Y</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>{val_12m_str}</div></div>"
            f"</div>"
        )
        with bot_col3:
            st.markdown(clean_html(f"<div class='kpi-card' style='justify-content: center; height: 210px;'><div class='kpi-lbl'>PKR YIELDS ({latest_pkrv_date_str})</div>{pkr_yields_html}</div>"), unsafe_allow_html=True)

        # =========================================================
        # SECTION: CURRENT INVESTMENT POSITION
        # =========================================================
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
        st.markdown(
            clean_html(
                "<div style='background-color: #0f6286; border-radius: 16px; padding: 32px; text-align: left; margin-bottom: 24px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); font-family: \"Chivo\", sans-serif;'>"
                "<h3 style='color: #ffffff; font-size: 34px; font-weight: 700; margin: 0; line-height: 1.2;'>Current Investment Position <span style='color: #f68b1e; font-weight: 400;'>&rarr;</span></h3>"
                "<p style='color: #ffffff; font-size: 21px; font-weight: 400; line-height: 1.5; margin-top: 12px; margin-bottom: 0;'>Instrument-Level Ledger & Portfolio Concentration</p>"
                "</div>"
            ), 
            unsafe_allow_html=True
        )

        investment_data = [
            {"instrument": "Savings Accounts", "value": 450.00, "conc": 45.0, "color": "#f68b1e"}, 
            {"instrument": "T-Bills", "value": 300.00, "conc": 30.0, "color": "#FFFFFF"},          
            {"instrument": "Buy/Sell", "value": 150.00, "conc": 15.0, "color": "#76C4E3"},         
            {"instrument": "TDRs", "value": 100.00, "conc": 10.0, "color": "#FFC107"}              
        ]
        gross_portfolio_value = sum(item["value"] for item in investment_data)

        inv_col1, inv_col2 = st.columns([1, 1.35], gap="large")

        # LEFT COLUMN: DONUT CHART
        with inv_col1:
            st.markdown(
                clean_html(
                    "<div class='html-card' style='padding-bottom: 0px; font-family: \"Chivo\", sans-serif;'>"
                    "<div style='font-size: 31px; font-weight: 700; color: #ffffff; line-height: 1.2;'>Portfolio Concentration <span style='color:#f68b1e; font-weight: 400;'>&rarr;</span></div>"
                    "<div style='font-size: 21px; font-weight: 400; color: #ffffff; line-height: 1.6; margin-top: 12px; margin-bottom: 10px;'>% Share of Gross Investment Portfolio</div>"
                    "</div>"
                ), 
                unsafe_allow_html=True
            )
        
            fig_inv_donut = go.Figure(data=[go.Pie(
                labels=[item["instrument"] for item in investment_data],
                values=[item["value"] for item in investment_data],
                hole=0.62,
                marker_colors=[item["color"] for item in investment_data],
                textposition='outside', 
                textinfo='label+percent',
                texttemplate="<b>%{label}</b><br>PKR %{value:,.1f} M<br>(%{percent})",
                textfont=dict(size=18, color='#0f6286', family="Chivo, sans-serif"),
                hovertemplate="<b>%{label}</b><br>Market Value: <b>PKR %{value:,.2f} M</b><br>Share: <b>%{percent}</b><extra></extra>",
                marker=dict(line=dict(color='#0f6286', width=2)) 
            )])
        
            fig_inv_donut.update_layout(
                showlegend=False, 
                margin=dict(t=50, b=50, l=100, r=100), 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                height=450 
            )
            st.plotly_chart(fig_inv_donut, use_container_width=True)

        # RIGHT COLUMN: FINANCIAL TABLE
        with inv_col2:
            table_rows = ""
            for item in investment_data:
                table_rows += (
                    "<tr class='inv-row'>"
                    f"<td style='padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: left; font-weight: 700; color: #FFFFFF; font-size: 20px;'>"
                    f"<span style='display:inline-block; width:12px; height:12px; border-radius:50%; background-color:{item['color']}; margin-right:12px;'></span>"
                    f"{item['instrument']}</td>"
                    f"<td style='padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: right; font-weight: 400; color: #FFFFFF; font-size: 20px;'>{item['value']:,.2f} M</td>"
                    f"<td style='padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.2); text-align: right; font-weight: 700; color: {item['color']}; font-size: 20px;'>{item['conc']:.1f}%</td>"
                    "</tr>"
                )
            
            table_html = (
                "<style>.inv-row { transition: background-color 0.2s ease; } .inv-row:hover { background-color: rgba(0,0,0,0.1); }</style>"
                "<div class='html-card' style='height: 100%; font-family: \"Chivo\", sans-serif;'>"
                "<div style='font-size: 31px; font-weight: 700; color: #ffffff; line-height: 1.2;'>Position by Instrument <span style='color:#f68b1e; font-weight: 400;'>&rarr;</span></div>"
                "<div style='font-size: 21px; font-weight: 400; color: #ffffff; line-height: 1.6; margin-top: 12px; margin-bottom: 18px;'>Market Value & Concentration Breakdown</div>"
                "<div style='flex-grow: 1; width: 100%; border-radius: 8px; overflow: hidden;'>"
                "<table style='width: 100%; border-collapse: collapse; background: transparent;'>"
                "<thead><tr style='background-color: rgba(0,0,0,0.1); color: #f68b1e; font-size: 18px;'>"
                "<th style='padding: 16px; text-align: left; font-weight: 700;'>INSTRUMENT</th>"
                "<th style='padding: 16px; text-align: right; font-weight: 700;'>MARKET VALUE (PKR Mns)</th>"
                "<th style='padding: 16px; text-align: right; font-weight: 700;'>CONC. (%)</th>"
                "</tr></thead>"
                f"<tbody>{table_rows}</tbody>"
                "<tfoot><tr style='background-color: rgba(0,0,0,0.15); font-size: 20px;'>"
                "<td style='padding: 16px; text-align: left; font-weight: 700; color: #FFFFFF;'>Gross Portfolio</td>"
                f"<td style='padding: 16px; text-align: right; font-weight: 700; color: #FFFFFF;'>{gross_portfolio_value:,.2f} M</td>"
                "<td style='padding: 16px; text-align: right; font-weight: 700; color: #f68b1e;'>100.0%</td>"
                "</tr></tfoot>"
                "</table></div></div>"
            )
            st.markdown(clean_html(table_html), unsafe_allow_html=True)

        # =========================================================
        # SECTION: PKRV ANALYSIS
        # =========================================================
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
        st.markdown(
            clean_html(
                "<div style='background-color: #0f6286; border-radius: 16px; padding: 32px; text-align: left; margin-bottom: 24px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); font-family: \"Chivo\", sans-serif;'>"
                "<h3 style='color: #ffffff; font-size: 34px; font-weight: 700; margin: 0; line-height: 1.2;'>PKRV Analysis <span style='color: #f68b1e; font-weight: 400;'>&rarr;</span></h3>"
                "<p style='color: #ffffff; font-size: 21px; font-weight: 400; line-height: 1.5; margin-top: 12px; margin-bottom: 0;'>Secondary Market Yield Curves & Tenor Trends (Jun 30, 2026 – Sep 15, 2026)</p>"
                "</div>"
            ), 
            unsafe_allow_html=True
        )

        # Plotly Line Chart for PKRV Analysis
        fig_pkrv = go.Figure()
        pkrv_colors = {'1M': '#f68b1e', '3M': '#FFFFFF', '6M': '#76C4E3', '12M': '#FFC107'}

        for tenor in ['1M', '3M', '6M', '12M']:
            if tenor in df_pkrv_chart.columns:
                fig_pkrv.add_trace(
                    go.Scatter(
                        x=df_pkrv_chart['DATE'],
                        y=df_pkrv_chart[tenor],
                        mode='lines+markers',
                        name=f'{tenor} PKRV',
                        line=dict(color=pkrv_colors[tenor], width=5),
                        marker=dict(size=9),
                        hovertemplate=f"<b>{tenor} PKRV Yield</b><br>Date: %{{x|%b %d, %Y}}<br>Yield: <b>%{{y:.2f}}%</b><extra></extra>"
                    )
                )

        fig_pkrv.update_layout(
            xaxis=dict(
                title=dict(text="Timeline Date", font=dict(size=18, color='#FFFFFF', family="Chivo, sans-serif")),
                tickfont=dict(size=16, color='#FFFFFF', family="Chivo, sans-serif"),
                gridcolor='rgba(255,255,255,0.15)',
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title=dict(text="Yield Rate (%)", font=dict(size=18, color='#FFFFFF', family="Chivo, sans-serif")),
                tickfont=dict(size=16, color='#FFFFFF', family="Chivo, sans-serif"),
                gridcolor='rgba(255,255,255,0.15)',
                ticksuffix="%",
                showgrid=True,
                zeroline=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.03,
                xanchor="right",
                x=1,
                font=dict(size=18, color='#FFFFFF', family="Chivo, sans-serif"),
                bgcolor='rgba(0,0,0,0.2)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            ),
            paper_bgcolor='#0f6286',
            plot_bgcolor='#0b4a66',
            height=500,
            margin=dict(l=50, r=50, t=60, b=50)
        )

        st.markdown(
            clean_html(
                "<div class='html-card' style='font-family: \"Chivo\", sans-serif; padding-bottom: 20px; border-bottom-left-radius: 0; border-bottom-right-radius: 0;'>"
                "<div style='font-size: 31px; font-weight: 700; color: #ffffff; line-height: 1.2;'>Quarterly PKRV Yield Movement <span style='color:#f68b1e; font-weight: 400;'>&rarr;</span></div>"
                "<div style='font-size: 21px; font-weight: 400; color: #ffffff; line-height: 1.6; margin-top: 10px;'>Daily Secondary Market Rates across 1M, 3M, 6M, and 12M Tenors starting June 30, 2026</div>"
                "</div>"
            ), 
            unsafe_allow_html=True
        )
        st.plotly_chart(fig_pkrv, use_container_width=True)

        # =========================================================
        # SECTION: KEY ECONOMIC INDICATORS
        # =========================================================
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
        st.markdown(
            clean_html(
                "<div style='background-color: #0f6286; border-radius: 16px; padding: 32px; text-align: left; margin-bottom: 24px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); font-family: \"Chivo\", sans-serif;'>"
                "<h3 style='color: #ffffff; font-size: 34px; font-weight: 700; margin: 0; line-height: 1.2;'>Key Economic Indicators <span style='color: #f68b1e; font-weight: 400;'>&rarr;</span></h3>"
                "<p style='color: #ffffff; font-size: 21px; font-weight: 400; line-height: 1.5; margin-top: 12px; margin-bottom: 0;'>Macroeconomic Trends & Market Intelligence</p>"
                "</div>"
            ), 
            unsafe_allow_html=True
        )

        econ_col1, econ_col2 = st.columns([1, 1], gap="large")

        # LEFT BOX: ECONOMIC OUTLOOK & INFLATION
        with econ_col1:
            st.markdown(
                clean_html(
                    "<div class='html-card' style='font-family: \"Chivo\", sans-serif;'>"
                    "<div style='font-size: 31px; font-weight: 700; color: #ffffff; line-height: 1.2;'>Economic Outlook & Inflation <span style='color:#f68b1e; font-weight: 400;'>&rarr;</span></div>"
                    "<div style='font-size: 21px; font-weight: 400; color: #ffffff; line-height: 1.6; margin-top: 18px;'>"
                    "&bull; <b>Headline CPI Inflation:</b> Pakistan's CPI inflation rose to <b>11.1% YoY in August 2026</b> (up from 9.2% in July), driven by rural inflation at 12.2% and urban inflation at 10.4%.<br><br>"
                    "&bull; <b>Finance Division Projection:</b> Inflation is projected to remain elevated between <b>10–11%</b> due to global energy and commodity pressures, alongside risks from private-sector credit contraction and climate developments.<br><br>"
                    "&bull; <b>External Sector Balance:</b> Strong export growth and sustained remittance inflows continue to narrow the current account deficit and mitigate external balance of payments risks.<br><br>"
                    "<span style='font-size: 19px; color: #f68b1e; font-weight: 700;'>Read Full Source Articles:</span><br>"
                    "&bull; <a href='https://www.brecorder.com/news/40437417' target='_blank' style='color: #76C4E3; text-decoration: underline;'>Business Recorder: August Inflation Report (11.1%)</a><br>"
                    "&bull; <a href='https://www.brecorder.com/news/40437339/august-economic-outlook-inflation-expected-to-remain-elevated-at-10-11pc' target='_blank' style='color: #76C4E3; text-decoration: underline;'>Business Recorder: Economic Update & Outlook</a>"
                    "</div>"
                    "</div>"
                ), 
                unsafe_allow_html=True
            )

        # RIGHT BOX: FISCAL DYNAMICS & FX RESERVES
        with econ_col2:
            st.markdown(
                clean_html(
                    "<div class='html-card' style='font-family: \"Chivo\", sans-serif;'>"
                    "<div style='font-size: 31px; font-weight: 700; color: #ffffff; line-height: 1.2;'>Fiscal Dynamics & FX Reserves <span style='color:#f68b1e; font-weight: 400;'>&rarr;</span></div>"
                    "<div style='font-size: 21px; font-weight: 400; color: #ffffff; line-height: 1.6; margin-top: 18px;'>"
                    "Foreign exchange reserves maintain a healthy trajectory backed by stable worker remittance inflows, multilateral credit disbursements, and moderate current account pressures. "
                    "Primary fiscal balances remain aligned with budgetary targets, keeping short-term money market liquidity balanced across institutional allocations."
                    "</div>"
                    "</div>"
                ), 
                unsafe_allow_html=True
            )

    # =========================================================
    # TAB 2: TREASURY COMMITTEE PRESENTATION
    # =========================================================
    with tab_tc:
        tc_deck_html = build_tc_deck_html(logo_b64)
        try:
            components.html(tc_deck_html, height=780, scrolling=False)
        except Exception:
            st.iframe(tc_deck_html, height=780)
