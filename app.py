import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(page_title="Treasury Summary FY26-27", layout="wide", initial_sidebar_state="collapsed")

EXCEL_FILE = "Treasury Income FY26'27 - July26.xlsx"

# ---------------------------------------------------------
# DIRECT EXCEL PARSING ENGINE
# ---------------------------------------------------------
try:
    # --- 1. Dashboard Sheet Parsing ---
    df_dash = pd.read_excel(EXCEL_FILE, sheet_name='Dashboard ', header=None)
    # Row 9 in Excel (idx 8 in pandas) holds monthly total income
    # Col C = Jul (idx 2), Col D = Aug (idx 3), Col E = Sep (idx 4)
    inc_jul = df_dash.iloc[8, 2] if pd.notna(df_dash.iloc[8, 2]) else 0
    inc_aug = df_dash.iloc[8, 3] if pd.notna(df_dash.iloc[8, 3]) else 0
    inc_sep = df_dash.iloc[8, 4] if pd.notna(df_dash.iloc[8, 4]) else 0
    
    q1_actual_income_mns = (inc_jul + inc_aug + inc_sep) / 1e6

    # Margin Breakdown for July
    osr_jul = (df_dash.iloc[2, 2] if pd.notna(df_dash.iloc[2, 2]) else 0) / 1e6
    rpa_jul = (df_dash.iloc[3, 2] if pd.notna(df_dash.iloc[3, 2]) else 0) / 1e6
    esc_jul = (df_dash.iloc[4, 2] if pd.notna(df_dash.iloc[4, 2]) else 0) / 1e6

    # --- 2. Treasury Pool Sheet Parsing ---
    df_pool = pd.read_excel(EXCEL_FILE, sheet_name='Treasury Pool', header=None)
    # Row 11 in Excel (idx 11 in pandas) holds Total Pool
    pool_jul = (df_pool.iloc[11, 2] if pd.notna(df_pool.iloc[11, 2]) else 0) / 1e6
    pool_aug = (df_pool.iloc[11, 3] if pd.notna(df_pool.iloc[11, 3]) else 0) / 1e6
    pool_sep = (df_pool.iloc[11, 4] if pd.notna(df_pool.iloc[11, 4]) else 0) / 1e6
    
    # Latest available Pool figure in Q1
    q1_pool_mns = pool_sep if pool_sep > 0 else pool_jul

    # Pool Breakdown (July)
    lr_funds = (df_pool.iloc[4, 2] if pd.notna(df_pool.iloc[4, 2]) else 0) / 1e6
    osr_funds = (df_pool.iloc[5, 2] if pd.notna(df_pool.iloc[5, 2]) else 0) / 1e6
    inv_cdel = (df_pool.iloc[6, 2] if pd.notna(df_pool.iloc[6, 2]) else 0) / 1e6
    rpa_acc = (df_pool.iloc[7, 2] if pd.notna(df_pool.iloc[7, 2]) else 0) / 1e6
    wv_greenfin = (df_pool.iloc[8, 2] if pd.notna(df_pool.iloc[8, 2]) else 0) / 1e6
    op_funds = (df_pool.iloc[9, 2] if pd.notna(df_pool.iloc[9, 2]) else 0) / 1e6

    # --- 3. MPR Sheet Parsing ---
    df_mpr = pd.read_excel(EXCEL_FILE, sheet_name='MPR')
    mpr_rate = float(df_mpr.iloc[0]['MPC Rate']) * 100
    next_mpr_date = pd.to_datetime(df_mpr.iloc[1]['MPC Meeting Date']).strftime('%b %d, %Y')

    # --- 4. Profit Rates Sheet Parsing ---
    df_rates = pd.read_excel(EXCEL_FILE, sheet_name='Profit Rates', header=None)
    rate_str = str(df_rates.iloc[2, 0])  # Row 3, Col A
    top_bank_rate = rate_str.split('\n')[0] if '\n' in rate_str else "Samba 11.30%"

except Exception as e:
    st.error(f"Error reading Excel file: {e}")
    q1_actual_income_mns, q1_pool_mns = 99.52, 15586.71
    inc_jul, inc_aug, inc_sep = 99.52, 0, 0
    osr_jul, rpa_jul, esc_jul = 97.38, 1.15, 1.00
    lr_funds, osr_funds, inv_cdel, rpa_acc, wv_greenfin, op_funds = 5521.09, 9310.81, 98.91, 250.56, 337.10, 68.24
    mpr_rate, next_mpr_date = 11.50, "Sep 14, 2026"
    top_bank_rate = "Samba 11.30%"

# Dynamic Quarter Dictionary mapped directly from Excel
quarter_data = {
    "Q1": {
        "period": "Q1 (Jul - Sep 2026)",
        "total_income": q1_actual_income_mns,
        "treasury_pool": q1_pool_mns,
        "forecasted_income": q1_actual_income_mns, # Currently actual filled in Excel
        "annual_yield": "11.30%",
        "months": ['Jul 26', 'Aug 26', 'Sep 26'],
        "income_trend": [inc_jul / 1e6, inc_aug / 1e6, inc_sep / 1e6],
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow Savings'],
        "margin_values": [osr_jul, rpa_jul, esc_jul]
    },
    "Q2": {
        "period": "Q2 (Oct - Dec 2026)",
        "total_income": 0.0,
        "treasury_pool": 0.0,
        "forecasted_income": 0.0,
        "annual_yield": "N/A",
        "months": ['Oct 26', 'Nov 26', 'Dec 26'],
        "income_trend": [0, 0, 0],
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow Savings'],
        "margin_values": [0, 0, 0]
    },
    "Q3": {
        "period": "Q3 (Jan - Mar 2027)",
        "total_income": 0.0,
        "treasury_pool": 0.0,
        "forecasted_income": 0.0,
        "annual_yield": "N/A",
        "months": ['Jan 27', 'Feb 27', 'Mar 27'],
        "income_trend": [0, 0, 0],
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow Savings'],
        "margin_values": [0, 0, 0]
    },
    "Q4": {
        "period": "Q4 (Apr - Jun 2027)",
        "total_income": 0.0,
        "treasury_pool": 0.0,
        "forecasted_income": 0.0,
        "annual_yield": "N/A",
        "months": ['Apr 27', 'May 27', 'Jun 27'],
        "income_trend": [0, 0, 0],
        "margin_labels": ['OSR Savings', 'RPA Savings', 'Escrow Savings'],
        "margin_values": [0, 0, 0]
    }
}

# ---------------------------------------------------------
# UI DISPLAY ENGINE
# ---------------------------------------------------------

# Splash Screen
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 85vh; flex-direction: column; text-align: center; animation: fadeOut 0.5s ease-in 2s forwards;'>
                <h1 style='color: #000000; font-size: 56px; letter-spacing: 2px; margin-bottom: 12px; font-weight: 900;'>KARANDAAZ TREASURY</h1>
                <p style='color: #64748B; font-size: 22px; font-weight: 600; letter-spacing: 1px;'>Loading Direct Excel Portfolio Data...</p>
                <div class="loader"></div>
            </div>
            <style>
            .loader { border: 5px solid #F1F5F9; border-top: 5px solid #2563EB; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin-top: 20px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
            .stApp { background-color: #FFFFFF; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
    splash.empty()
    st.session_state.first_load = False

# CSS Architecture
st.markdown("""
    <style>
    * { font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important; box-sizing: border-box; }
    html, body, .stApp { background-color: #F8FAFC !important; margin: 0 !important; padding: 0 !important; }
    header { visibility: hidden; height: 0; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }

    .header-container { display: flex; align-items: center; justify-content: center; margin-top: 0px !important; margin-bottom: 12px; }
    .glow-line { height: 3px; flex-grow: 1; max-width: 380px; background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent); box-shadow: 0 0 12px rgba(59, 130, 246, 0.6); }
    .header-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 40px; margin: 0 20px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05); font-weight: 900; font-size: 26px; color: #000000; letter-spacing: 1.5px; text-transform: uppercase; }

    .kpi-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); height: 100%; display: flex; flex-direction: column; justify-content: center; transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.07); }
    .kpi-title { font-size: 14px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.8px; }
    .kpi-value { font-size: 28px; font-weight: 900; color: #0F172A; line-height: 1.1; margin-top: 6px; }
    .kpi-sub { font-size: 12px; font-weight: 600; color: #64748B; margin-top: 4px; }
    .kpi-divider { border: 0; border-top: 1px solid #E2E8F0; margin: 8px 0; }

    div[data-testid="stPlotlyChart"] { background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 16px !important; padding: 12px 14px 8px 14px !important; box-shadow: 0 6px 18px rgba(0,0,0,0.04) !important; }
    .blue-card div[data-testid="stPlotlyChart"] { border: 2px solid #2563EB !important; box-shadow: 0 10px 28px rgba(37, 99, 235, 0.12) !important; }

    .screen-2-header { margin-top: 45px; margin-bottom: 20px; text-align: center; }
    .screen-2-header h3 { font-size: 20px; font-weight: 900; color: #0F172A; letter-spacing: 1.2px; text-transform: uppercase; margin: 0; }
    div[data-baseweb="select"] > div { border-radius: 10px; font-size: 14px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

CHART_FONT = dict(family="Segoe UI, Roboto, sans-serif", color="#000000", size=13)
BLUE_ACCENT, GREEN_ACCENT = '#2563EB', '#10B981'

with st.spinner("Rendering Visualizations..."):
    
    # SCREEN 1: TOP SECTION
    st.markdown("""
        <div class="header-container">
            <div class="glow-line"></div>
            <div class="header-card">Treasury Portfolio Summary (FY26-27)</div>
            <div class="glow-line"></div>
        </div>
    """, unsafe_allow_html=True)

    col_e1, col_date, col_e2 = st.columns([1, 0.25, 1])
    with col_date:
        selected_q = st.selectbox("", ["Q1", "Q2", "Q3", "Q4"], label_visibility="collapsed")

    q_ctx = quarter_data[selected_q]

    st.write("")

    # 4 KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    with kpi1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Income</div><hr class='kpi-divider'><div class='kpi-value'>{q_ctx['total_income']:,.2f} PKR Mns</div><div class='kpi-sub'>Quarterly Income ({selected_q})</div></div>", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Treasury Pool</div><hr class='kpi-divider'><div class='kpi-value'>{q_ctx['treasury_pool']:,.2f} PKR Mns</div><div class='kpi-sub'>Total Allocation ({selected_q})</div></div>", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Forecasted Income</div><hr class='kpi-divider'><div class='kpi-value'>{q_ctx['forecasted_income']:,.2f} PKR Mns</div><div class='kpi-sub'>Forecasted Income for {selected_q}</div></div>", unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Annual Yield</div><hr class='kpi-divider'><div class='kpi-value'>{q_ctx['annual_yield']}</div><div class='kpi-sub'>Weighted Annual Yield</div></div>", unsafe_allow_html=True)

    st.write("")

    # Screen 1 Charts
    sc1_left, sc1_right = st.columns([1, 1.8], gap="medium")

    with sc1_left:
        fig_margin = go.Figure(data=[go.Pie(
            labels=q_ctx['margin_labels'], 
            values=q_ctx['margin_values'], hole=0.72,
            marker_colors=[BLUE_ACCENT, '#60A5FA', GREEN_ACCENT], textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2)), pull=[0.04, 0, 0] 
        )])
        fig_margin.update_layout(
            title=dict(text=f"INCOME MARGIN DISTRIBUTION ({selected_q})", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.95, xanchor='center', yanchor='top'),
            annotations=[dict(text=f"Total<br><b style='font-size:22px; color:#000;'>{q_ctx['total_income']:.1f}M</b>", x=0.5, y=0.5, font=CHART_FONT, showarrow=False)],
            showlegend=False, margin=dict(t=45, b=15, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, font=CHART_FONT
        )
        st.markdown("<div class='blue-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig_margin, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with sc1_right:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=q_ctx['months'], y=q_ctx['income_trend'], name='Total Income', line=dict(color=BLUE_ACCENT, width=4, shape='spline'), mode='lines+markers', marker=dict(size=9)))
        fig_trend.update_layout(
            title=dict(text=f"INCOME TREND ({selected_q})", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.95, xanchor='center', yanchor='top'),
            margin=dict(t=45, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#111111", size=12)),
            xaxis=dict(showgrid=False, tickfont=dict(color="#111111", size=12)), 
            yaxis=dict(showgrid=True, gridcolor='#CBD5E1', tickfont=dict(color="#111111", size=12), zeroline=False), 
            height=300, font=CHART_FONT
        )
        st.markdown("<div class='blue-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # SCREEN 2: BOTTOM SECTION
    st.markdown("""
        <div class="screen-2-header">
            <h3>Detailed Treasury Portfolio Breakdown</h3>
        </div>
    """, unsafe_allow_html=True)

    bot1, bot2, bot3, bot4 = st.columns([1.1, 1.1, 0.9, 1.5], gap="medium")

    with bot1:
        fig_treasury = go.Figure(data=[go.Pie(
            labels=['OSR Funds', 'LR Funds', 'WV Greenfin', 'RPA A/c', 'Inv/CDEL', 'Operational'], 
            values=[osr_funds, lr_funds, wv_greenfin, rpa_acc, inv_cdel, op_funds], hole=0.60,
            marker_colors=[BLUE_ACCENT, '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#CBD5E1'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_treasury.update_layout(
            title=dict(text="TREASURY POOL SPLIT", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.95, xanchor='center', yanchor='top'),
            showlegend=False, margin=dict(t=45, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=310, font=CHART_FONT
        )
        st.plotly_chart(fig_treasury, use_container_width=True)

    with bot2:
        fig_exp = go.Figure(data=[go.Pie(
            labels=['OSR Savings', 'RPA Savings', 'Escrow'], values=[osr_jul, rpa_jul, esc_jul], hole=0.60,
            marker_colors=[GREEN_ACCENT, '#34D399', '#6EE7B7'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_exp.update_layout(
            title=dict(text="INCOME TYPE BREAKDOWN", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.95, xanchor='center', yanchor='top'),
            showlegend=False, margin=dict(t=45, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=310, font=CHART_FONT
        )
        st.plotly_chart(fig_exp, use_container_width=True)

    with bot3:
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; height: 310px; justify-content: space-between;'>
                <div class='kpi-card' style='text-align: center; height: 148px;'>
                    <div class='kpi-title' style='font-size: 13px;'>Highest Profit Rate</div><hr class='kpi-divider'>
                    <div class='kpi-value' style='color:#2563EB; font-size: 26px;'>{top_bank_rate}</div>
                </div>
                <div class='kpi-card' style='text-align: center; height: 148px;'>
                    <div class='kpi-title' style='font-size: 13px;'>MhePR</div><hr class='kpi-divider'>
                    <div class='kpi-value' style='color:#2563EB; font-size: 26px;'>{mpr_rate:.2f}%</div>
                    <div class='kpi-sub'>Next Date: {next_mpr_date}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with bot4:
        fig_bar = go.Figure()
        categories = ['Operational', 'WV Greenfin', 'RPA A/c', 'Inv/CDEL', 'LR Funds', 'OSR Funds']
        fig_bar.add_trace(go.Bar(y=categories, x=[op_funds, wv_greenfin, rpa_acc, inv_cdel, lr_funds, osr_funds], name='Actual Pool (PKR M)', orientation='h', marker_color=BLUE_ACCENT))
        fig_bar.update_layout(
            title=dict(text="FUND POOL ALLOCATION (PKR M)", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.95, xanchor='center', yanchor='top'),
            barmode='group', margin=dict(t=45, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#111111", size=12)), 
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0', tickfont=dict(color="#111111", size=12)), 
            yaxis=dict(showgrid=False, tickfont=dict(color="#111111", size=12)), 
            height=310, font=CHART_FONT
        )
        st.plotly_chart(fig_bar, use_container_width=True)
