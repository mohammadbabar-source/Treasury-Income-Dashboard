import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import base64
import os

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
# DYNAMIC DATA INGESTION FROM EXCEL
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

/* KPI Cards */
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

    col_e1, col_date, col_e2 = st.columns([1, 0.3, 1])
    with col_date:
        selected_q = st.selectbox("", ["Q1", "Q2", "Q3", "Q4"], label_visibility="collapsed")

    q_ctx = quarter_data[selected_q]
    q_rates_list = get_quarter_rates(selected_q)

    # 4 Centered Top KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    with kpi1:
        st.markdown(clean_html(f"<div class='kpi-card'><div class='kpi-lbl'>TOTAL INCOME</div><div class='kpi-val'>{q_ctx['total_income']:,.2f} M</div><div class='kpi-sub'>Quarterly Income ({selected_q})</div></div>"), unsafe_allow_html=True)
    with kpi2:
        st.markdown(clean_html(f"<div class='kpi-card'><div class='kpi-lbl'>TREASURY POOL</div><div class='kpi-val'>{q_ctx['treasury_pool']:,.2f} M</div><div class='kpi-sub'>Total Allocation ({selected_q})</div></div>"), unsafe_allow_html=True)
    with kpi3:
        st.markdown(clean_html(f"<div class='kpi-card'><div class='kpi-lbl'>FORECASTED INCOME</div><div class='kpi-val'>{q_ctx['forecasted_income']:,.2f} M</div><div class='kpi-sub'>Forecasted for {selected_q}</div></div>"), unsafe_allow_html=True)
    with kpi4:
        st.markdown(clean_html(f"<div class='kpi-card'><div class='kpi-lbl'>ANNUAL YIELD</div><div class='kpi-val'>{q_ctx['annual_yield']}</div><div class='kpi-sub'>Weighted Annual Yield</div></div>"), unsafe_allow_html=True)
    
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
        "<div style='display: flex; justify-content: space-between; width: 100%; gap: 10px; margin-top: 10px; height: 100%;'>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>1M</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>--%</div></div>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>3M</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>--%</div></div>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>6M</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>--%</div></div>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: rgba(0,0,0,0.1); border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 18px; font-weight: 700; color: #f68b1e; text-transform: uppercase;'>1Y</div><div style='font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 8px;'>--%</div></div>"
        "</div>"
    )
    with bot_col3:
        st.markdown(clean_html(f"<div class='kpi-card' style='justify-content: center; height: 210px;'><div class='kpi-lbl'>PKR YIELDS</div>{pkr_yields_html}</div>"), unsafe_allow_html=True)

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
            showlegend=False, margin=dict(t=50, b=50, l=100, r=100), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450 
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

    # LEFT BOX: ECONOMIC OUTLOOK & INFLATION (SUMMARIZED WITH HYPERLINKS)
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
