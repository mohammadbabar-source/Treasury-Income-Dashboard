import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(page_title="Karandaaz Treasury Summary FY26-27", layout="wide", initial_sidebar_state="collapsed")

# File Reference
EXCEL_FILE = "Treasury Income FY26'27 - July26.xlsx"

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

# 2. Splash Screen (Karandaaz Teal & Taupe Branding)
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 85vh; flex-direction: column; text-align: center; animation: fadeOut 0.5s ease-in 2s forwards;'>
                <h1 style='color: #007982; font-size: 58px; letter-spacing: 3px; margin-bottom: 8px; font-weight: 900; text-transform: uppercase;'>Karandaaz Pakistan</h1>
                <p style='color: #8A7E77; font-size: 22px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;'>Treasury Management Dashboard</p>
                <div class="loader"></div>
            </div>
            <style>
            .loader { border: 4px solid #EAEBEB; border-top: 4px solid #007982; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-top: 28px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
            .stApp { background-color: #FAFAFA; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
    splash.empty()
    st.session_state.first_load = False

# 3. Custom CSS Architecture (Karandaaz Corporate Theme)
st.markdown("""
    <style>
    * { font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif !important; box-sizing: border-box; }
    
    /* Background & Structural Colors */
    html, body, .stApp { background-color: #F4F6F6 !important; margin: 0 !important; padding: 0 !important; }
    header { visibility: hidden; height: 0; }
    .block-container { padding-top: 5rem !important; padding-bottom: 3rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }

    /* SBP Rolling Banner CSS - Karandaaz Teal Gradient */
    .sbp-marquee {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(180deg, #00666d 0%, #007982 50%, #005a61 100%); 
        color: #FFFFFF;
        padding: 11px 0;
        overflow: hidden;
        white-space: nowrap;
        z-index: 999999;
        border-top: 1px solid #0098a3; 
        border-bottom: 3px solid #8A7E77; 
        box-shadow: 0 4px 12px rgba(0, 121, 130, 0.25);
    }
    .sbp-marquee a {
        color: #FFFFFF !important;
        text-decoration: none;
        font-size: 17px; 
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .sbp-marquee > span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee_scroll 28s linear infinite;
    }
    .sbp-marquee:hover > span {
        animation-play-state: paused;
    }
    @keyframes marquee_scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }
    
    .header-container { display: flex; align-items: center; justify-content: center; margin-top: 10px !important; margin-bottom: 16px; }
    .glow-line { height: 2px; flex-grow: 1; max-width: 380px; background: linear-gradient(90deg, transparent, rgba(0, 121, 130, 0.3), transparent); }
    .header-card { background: #FFFFFF; border: 1px solid #EAEBEB; border-top: 4px solid #007982; border-radius: 12px; padding: 16px 48px; margin: 0 24px; box-shadow: 0 4px 20px rgba(0, 121, 130, 0.05); font-weight: 800; font-size: 26px; color: #007982; letter-spacing: 1.5px; text-transform: uppercase; }

    /* Executive Top KPI Cards */
    .kpi-card { 
        background: #FFFFFF; 
        border: 1px solid #EAEBEB; 
        border-top: 4px solid #007982;
        border-radius: 12px; 
        padding: 22px 10px; 
        box-shadow: 0 4px 14px rgba(47, 51, 54, 0.04); 
        height: 100%; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        text-align: center; 
        transition: transform 0.2s ease, box-shadow 0.2s ease; 
        gap: 6px;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 121, 130, 0.1); }
    .kpi-val { font-size: 34px; font-weight: 900; color: #2F3336; line-height: 1.1; margin: 4px 0; }
    .kpi-lbl { font-size: 13px; font-weight: 800; color: #8A7E77; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-sub { font-size: 12px; font-weight: 700; color: #007982; }

    /* Executive HTML Containers */
    .html-card {
        background-color: #FFFFFF;
        border: 1px solid #EAEBEB;
        border-top: 4px solid #007982;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(47, 51, 54, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .html-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0, 121, 130, 0.08); }
    
    /* Clean Professional Fade Animation */
    @keyframes fadeInSmooth {
        0% { opacity: 0; transform: translateY(6px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .animated-chart-container {
        animation: fadeInSmooth 0.8s ease-out forwards;
    }

    div[data-baseweb="select"] > div { border-radius: 8px; font-size: 16px; font-weight: 600; padding: 4px; border-color: #007982 !important; color: #2F3336; }
    </style>
""", unsafe_allow_html=True)

CHART_FONT = dict(family="Segoe UI, Roboto, sans-serif", color="#2F3336", size=13)
KARANDAAZ_TEAL = '#007982'
KARANDAAZ_TAUPE = '#8A7E77'

with st.spinner("Rendering Visualizations..."):

    # SBP Rolling Banner
    st.markdown(f"""
        <div class="sbp-marquee">
            <span>
                <a href="https://www.sbp.org.pk/our-operations/monetary-policy" target="_blank">
                    <span style="color: #E2DBD6; margin-right: 8px; font-weight: 800;">🏛️ SBP MONETARY POLICY UPDATE:</span>
                    The current Monetary Policy Rate is <b style="color:#FFFFFF;">{mpr_rate:.2f}%</b>. 
                    Next MPC meeting is scheduled for <b style="color:#FFFFFF;">{next_mpr_date}</b>. 
                    <em style="color:#E2DBD6;">Summary: The Monetary Policy Committee continues to monitor inflation targets and economic indicators.</em> 
                    &nbsp;&nbsp;🔗 Click here to read the full policy statement on the official SBP website.
                </a>
            </span>
        </div>
    """, unsafe_allow_html=True)

    # SCREEN 1: TOP SECTION
    st.markdown("""
        <div class="header-container">
            <div class="glow-line"></div>
            <div class="header-card">Treasury Portfolio Summary (FY26-27)</div>
            <div class="glow-line"></div>
        </div>
    """, unsafe_allow_html=True)

    col_e1, col_date, col_e2 = st.columns([1, 0.3, 1])
    with col_date:
        selected_q = st.selectbox("", ["Q1", "Q2", "Q3", "Q4"], label_visibility="collapsed")

    q_ctx = quarter_data[selected_q]
    q_rates_list = get_quarter_rates(selected_q)

    # 4 Centered Top KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    with kpi1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>TOTAL INCOME</div><div class='kpi-val'>{q_ctx['total_income']:,.2f} M</div><div class='kpi-sub'>Quarterly Income ({selected_q})</div></div>", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>TREASURY POOL</div><div class='kpi-val'>{q_ctx['treasury_pool']:,.2f} M</div><div class='kpi-sub'>Total Allocation ({selected_q})</div></div>", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>FORECASTED INCOME</div><div class='kpi-val'>{q_ctx['forecasted_income']:,.2f} M</div><div class='kpi-sub'>Forecasted for {selected_q}</div></div>", unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>ANNUAL YIELD</div><div class='kpi-val'>{q_ctx['annual_yield']}</div><div class='kpi-sub'>Weighted Annual Yield</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    bot_col1, bot_col2, bot_col3 = st.columns(3, gap="medium")

    # 1. Bank Profit Rates Card
    month_cols_html = "<div style='display: flex; justify-content: space-between; width: 100%; gap: 10px; margin-top: 10px; height: 100%;'>"
    for month_info in q_rates_list:
        rates_br = "<br>".join(month_info['rates'])
        month_cols_html += f"<div style='flex: 1; background: #F9FAFA; border: 1px solid #EAEBEB; border-radius: 8px; padding: 14px 6px; text-align: center;'><div style='font-size: 12px; font-weight: 800; color: #007982; text-transform: uppercase;'>{month_info['month']}</div><div style='font-size: 13px; font-weight: 600; color: #2F3336; margin-top: 8px; line-height: 1.7;'>{rates_br}</div></div>"
    month_cols_html += "</div>"

    with bot_col1:
        st.markdown(f"<div class='kpi-card' style='justify-content: center; height: 210px;'><div class='kpi-lbl'>BANK PROFIT RATES ({selected_q})</div>{month_cols_html}</div>", unsafe_allow_html=True)

    # 2. MPR Rate Card
    mpr_split_html = (
        "<div style='display: flex; justify-content: space-between; width: 100%; height: 100%; align-items: center;'>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; border-right: 1px solid #EAEBEB; padding-right: 10px;'>"
        f"<div style='color:#007982; font-size: 38px; font-weight: 900; line-height: 1.1;'>{mpr_rate:.2f}%</div>"
        "<div style='font-size: 13px; font-weight: 800; color: #8A7E77; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 8px;'>MPR RATE</div>"
        f"<div style='font-size: 12px; font-weight: 700; color: #2F3336; margin-top: 4px;'>Next Date: {next_mpr_date}</div>"
        "</div>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding-left: 10px;'>"
        f"<div style='color:#2F3336; font-size: 38px; font-weight: 900; line-height: 1.1;'>{mpr_rate - 1.5:.2f}%</div>"
        "<div style='font-size: 13px; font-weight: 800; color: #8A7E77; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 8px;'>BENCHMARK</div>"
        "<div style='font-size: 12px; font-weight: 700; color: #007982; margin-top: 4px;'>MPR - 1.5%</div>"
        "</div></div>"
    )

    with bot_col2:
        st.markdown(f"<div class='kpi-card' style='justify-content: center; height: 210px; padding: 10px;'>{mpr_split_html}</div>", unsafe_allow_html=True)

    # 3. PKR Yields Card
    pkr_yields_html = (
        "<div style='display: flex; justify-content: space-between; width: 100%; gap: 10px; margin-top: 10px; height: 100%;'>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: #F9FAFA; border: 1px solid #EAEBEB; border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 13px; font-weight: 800; color: #8A7E77; text-transform: uppercase;'>1M</div><div style='font-size: 18px; font-weight: 900; color: #007982; margin-top: 8px;'>--%</div></div>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: #F9FAFA; border: 1px solid #EAEBEB; border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 13px; font-weight: 800; color: #8A7E77; text-transform: uppercase;'>3M</div><div style='font-size: 18px; font-weight: 900; color: #007982; margin-top: 8px;'>--%</div></div>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: #F9FAFA; border: 1px solid #EAEBEB; border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 13px; font-weight: 800; color: #8A7E77; text-transform: uppercase;'>6M</div><div style='font-size: 18px; font-weight: 900; color: #007982; margin-top: 8px;'>--%</div></div>"
        "<div style='flex: 1; display: flex; flex-direction: column; justify-content: center; background: #F9FAFA; border: 1px solid #EAEBEB; border-radius: 8px; padding: 14px 4px; text-align: center;'><div style='font-size: 13px; font-weight: 800; color: #8A7E77; text-transform: uppercase;'>1Y</div><div style='font-size: 18px; font-weight: 900; color: #007982; margin-top: 8px;'>--%</div></div>"
        "</div>"
    )

    with bot_col3:
        st.markdown(f"<div class='kpi-card' style='justify-content: center; height: 210px;'><div class='kpi-lbl'>PKR YIELDS</div>{pkr_yields_html}</div>", unsafe_allow_html=True)


    # =========================================================
    # NEW SECTION: CURRENT INVESTMENT POSITION (KARANDAAZ PALETTE)
    # =========================================================
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    st.markdown(
        "<div style='text-align: left; margin-bottom: 20px; padding-left: 12px; border-left: 4px solid #007982;'>"
        "<h3 style='font-size: 22px; font-weight: 800; color: #2F3336; letter-spacing: 1px; text-transform: uppercase; margin: 0;'>Current Investment Position</h3>"
        "<p style='color: #8A7E77; font-size: 14px; font-weight: 600; margin-top: 4px; margin-bottom: 0;'>Instrument-Level Ledger & Portfolio Concentration</p>"
        "</div>", 
        unsafe_allow_html=True
    )

    # Professional Karandaaz Palette extracted from Logo
    investment_data = [
        {"instrument": "Savings Accounts", "value": 450.00, "conc": 45.0, "color": "#007982"}, # Karandaaz Teal
        {"instrument": "T-Bills", "value": 300.00, "conc": 30.0, "color": "#8A7E77"},          # Karandaaz Taupe
        {"instrument": "Buy/Sell", "value": 150.00, "conc": 15.0, "color": "#004C52"},         # Dark Teal Accent
        {"instrument": "TDRs", "value": 100.00, "conc": 10.0, "color": "#B5ACA6"}              # Light Taupe Accent
    ]
    gross_portfolio_value = sum(item["value"] for item in investment_data)

    inv_col1, inv_col2 = st.columns([1, 1.35], gap="large")

    # LEFT COLUMN: EXECUTIVE DONUT CHART
    with inv_col1:
        st.markdown(
            "<div class='html-card' style='padding-bottom: 0px; border-top: 4px solid #007982;'>"
            "<div style='font-size: 14px; font-weight: 800; color: #8A7E77; text-transform: uppercase; letter-spacing: 1px;'>PORTFOLIO CONCENTRATION</div>"
            "<div style='font-size: 13px; font-weight: 600; color: #2F3336; margin-top: 4px; margin-bottom: 10px;'>% Share of Gross Investment Portfolio</div>"
            "</div>", 
            unsafe_allow_html=True
        )
        
        fig_inv_donut = go.Figure(data=[go.Pie(
            labels=[item["instrument"] for item in investment_data],
            values=[item["value"] for item in investment_data],
            hole=0.62,
            pull=[0.02, 0.02, 0.02, 0.02],
            marker_colors=[item["color"] for item in investment_data],
            textinfo='label+percent',
            textposition='outside',
            insidetextorientation='horizontal',
            textfont=dict(size=12, weight='bold', color='#2F3336', family="Segoe UI, sans-serif"),
            hovertemplate="<b>%{label}</b><br>Market Value: <b>PKR %{value:,.2f} M</b><br>Share: <b>%{percent}</b><extra></extra>",
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        
        fig_inv_donut.update_layout(
            showlegend=False,
            margin=dict(t=30, b=30, l=40, r=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=370
        )
        
        st.markdown("<div class='animated-chart-container'>", unsafe_allow_html=True)
        st.plotly_chart(fig_inv_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT COLUMN: EXECUTIVE FINANCIAL TABLE
    with inv_col2:
        table_rows = ""
        for item in investment_data:
            table_rows += (
                "<tr class='inv-row'>"
                f"<td style='padding: 15px 16px; border-bottom: 1px solid #F0F4F4; text-align: left; font-weight: 700; color: #2F3336;'>"
                f"<span style='display:inline-block; width:10px; height:10px; border-radius:50%; background-color:{item['color']}; margin-right:12px;'></span>"
                f"{item['instrument']}</td>"
                f"<td style='padding: 15px 16px; border-bottom: 1px solid #F0F4F4; text-align: right; font-weight: 600; color: #2F3336;'>{item['value']:,.2f} M</td>"
                f"<td style='padding: 15px 16px; border-bottom: 1px solid #F0F4F4; text-align: right; font-weight: 800; color: {item['color']};'>{item['conc']:.1f}%</td>"
                "</tr>"
            )
            
        table_html = (
            "<style>.inv-row { transition: background-color 0.2s ease; } .inv-row:hover { background-color: #F9FAFA; }</style>"
            "<div class='html-card' style='height: 100%; border-top: 4px solid #007982;'>"
            "<div style='font-size: 14px; font-weight: 800; color: #8A7E77; text-transform: uppercase; letter-spacing: 1px;'>POSITION BY INSTRUMENT</div>"
            "<div style='font-size: 13px; font-weight: 600; color: #2F3336; margin-top: 4px; margin-bottom: 18px;'>Market Value & Concentration Breakdown</div>"
            "<div style='flex-grow: 1; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid #EAEBEB; box-shadow: 0 2px 8px rgba(47, 51, 54, 0.02);'>"
            "<table style='width: 100%; border-collapse: collapse; font-size: 13px; background: white;'>"
            "<thead><tr style='background-color: #007982; color: #FFFFFF; font-size: 12px; letter-spacing: 0.8px; text-transform: uppercase;'>"
            "<th style='padding: 14px 16px; text-align: left; font-weight: 700;'>INSTRUMENT</th>"
            "<th style='padding: 14px 16px; text-align: right; font-weight: 700;'>MARKET VALUE (PKR Mns)</th>"
            "<th style='padding: 14px 16px; text-align: right; font-weight: 700;'>CONC. (%)</th>"
            "</tr></thead>"
            f"<tbody>{table_rows}</tbody>"
            "<tfoot><tr style='background-color: #F4F6F6; border-top: 2px solid #007982;'>"
            "<td style='padding: 16px 16px; text-align: left; font-weight: 800; color: #2F3336;'>Gross Portfolio</td>"
            f"<td style='padding: 16px 16px; text-align: right; font-weight: 800; color: #2F3336;'>{gross_portfolio_value:,.2f} M</td>"
            "<td style='padding: 16px 16px; text-align: right; font-weight: 900; color: #007982;'>100.0%</td>"
            "</tr></tfoot>"
            "</table></div></div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)
