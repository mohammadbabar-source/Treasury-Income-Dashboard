import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(page_title="Treasury Summary FY26-27", layout="wide", initial_sidebar_state="collapsed")

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

# 2. Splash Screen
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 85vh; flex-direction: column; text-align: center; animation: fadeOut 0.5s ease-in 2s forwards;'>
                <h1 style='color: #000000; font-size: 64px; letter-spacing: 2px; margin-bottom: 12px; font-weight: 900;'>KARANDAAZ TREASURY</h1>
                <p style='color: #64748B; font-size: 26px; font-weight: 600; letter-spacing: 1px;'>Loading FY26-27 Quarterly Dashboard...</p>
                <div class="loader"></div>
            </div>
            <style>
            .loader { border: 5px solid #F1F5F9; border-top: 5px solid #2563EB; border-radius: 50%; width: 55px; height: 55px; animation: spin 1s linear infinite; margin-top: 24px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
            .stApp { background-color: #FFFFFF; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
    splash.empty()
    st.session_state.first_load = False

# 3. Custom CSS Architecture
st.markdown("""
    <style>
    * { font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important; box-sizing: border-box; }
    html, body, .stApp { background-color: #F8FAFC !important; margin: 0 !important; padding: 0 !important; }
    header { visibility: hidden; height: 0; }
    
    .block-container { padding-top: 5rem !important; padding-bottom: 3rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }

    /* SBP Rolling Banner CSS - Subtle 3D Effect */
    .sbp-marquee {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(180deg, #13612c 0%, #0F4C23 45%, #0a3819 100%); 
        color: #FFFFFF;
        padding: 12px 0;
        overflow: hidden;
        white-space: nowrap;
        z-index: 999999;
        border-top: 1px solid #1a873e; 
        border-bottom: 3px solid #D4AF37; 
        box-shadow: 0 6px 15px rgba(0,0,0,0.25), inset 0 2px 4px rgba(255,255,255,0.1);
    }
    .sbp-marquee a {
        color: #FFFFFF !important;
        text-decoration: none;
        font-size: 19px; 
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
    .glow-line { height: 4px; flex-grow: 1; max-width: 380px; background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent); box-shadow: 0 0 16px rgba(59, 130, 246, 0.6); }
    .header-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 48px; margin: 0 24px; box-shadow: 0 8px 24px rgba(30, 58, 138, 0.15); font-weight: 900; font-size: 32px; color: #000000; letter-spacing: 1.5px; text-transform: uppercase; }

    /* Centered & Scaled Top KPI Cards (IMAGE 2 STYLE) */
    .kpi-card { 
        background: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        border-radius: 12px; 
        padding: 24px 10px; 
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.08); 
        height: 100%; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        text-align: center; 
        transition: transform 0.2s ease, box-shadow 0.2s ease; 
        gap: 6px;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(30, 58, 138, 0.15); }
    .kpi-val { font-size: 38px; font-weight: 900; color: #003366; line-height: 1; }
    .kpi-lbl { font-size: 15px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-sub { font-size: 13px; font-weight: 700; color: #10B981; }

    /* Streamlit Plotly Chart Customization to act as the unified card container */
    div[data-testid="stPlotlyChart"] { 
        background-color: #FFFFFF !important; 
        border-radius: 16px !important; 
        border: 1px solid #E2E8F0 !important; 
        border-top: 5px solid #2563EB !important; 
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.12) !important; 
        padding: 15px !important; 
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stPlotlyChart"]:hover {
        transform: translateY(-3px); 
        box-shadow: 0 12px 32px rgba(30, 58, 138, 0.25) !important;
    }

    /* Refined Bank Profit Rates Container - Matches Plotly Containers */
    .html-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #2563EB;
        border-radius: 16px;
        padding: 24px 20px;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.12);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .html-card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(30, 58, 138, 0.25); }
    .html-card-title { font-size: 18px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.8px; width: 100%; margin-bottom: 16px;}

    .screen-2-header { margin-top: 50px; margin-bottom: 24px; text-align: center; }
    .screen-2-header h3 { font-size: 25px; font-weight: 900; color: #0F172A; letter-spacing: 1.2px; text-transform: uppercase; margin: 0; }
    div[data-baseweb="select"] > div { border-radius: 12px; font-size: 18px; font-weight: 600; padding: 4px; }
    </style>
""", unsafe_allow_html=True)

CHART_FONT = dict(family="Segoe UI, Roboto, sans-serif", color="#0F172A", size=15)
BLUE_ACCENT, GREEN_ACCENT = '#2563EB', '#10B981'

with st.spinner("Rendering Visualizations..."):

    # SBP Rolling Banner
    st.markdown(f"""
        <div class="sbp-marquee">
            <span>
                <a href="https://www.sbp.org.pk/our-operations/monetary-policy" target="_blank">
                    <span style="color: #D4AF37; margin-right: 8px;">🏛️ SBP MONETARY POLICY UPDATE:</span>
                    The current Monetary Policy Rate is <b style="color:#D4AF37;">{mpr_rate:.2f}%</b>. 
                    Next MPC meeting is scheduled for <b style="color:#D4AF37;">{next_mpr_date}</b>. 
                    <em>Summary: The Monetary Policy Committee continues to monitor inflation targets and economic indicators to ensure macroeconomic stability.</em> 
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

    # 4 Centered Top KPI Cards (IMAGE 2 STYLE)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    with kpi1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-val'>{q_ctx['total_income']:,.2f} M</div><div class='kpi-lbl'>Total Income</div><div class='kpi-sub'>Quarterly Income ({selected_q})</div></div>", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-val'>{q_ctx['treasury_pool']:,.2f} M</div><div class='kpi-lbl'>Treasury Pool</div><div class='kpi-sub'>Total Allocation ({selected_q})</div></div>", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-val'>{q_ctx['forecasted_income']:,.2f} M</div><div class='kpi-lbl'>Forecasted Income</div><div class='kpi-sub'>Forecasted for {selected_q}</div></div>", unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"<div class='kpi-card'><div class='kpi-val'>{q_ctx['annual_yield']}</div><div class='kpi-lbl'>Annual Yield</div><div class='kpi-sub'>Weighted Annual Yield</div></div>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    sc1_left, sc1_mid, sc1_cards = st.columns([1.1, 1.3, 0.95], gap="large")

    # --- Donut Chart Card (Title embedded in Plotly) ---
    with sc1_left:
        fig_margin = go.Figure(data=[go.Pie(
            labels=q_ctx['margin_labels'], 
            values=q_ctx['margin_values'], hole=0.68,
            marker_colors=[BLUE_ACCENT, '#60A5FA', GREEN_ACCENT, '#34D399', '#93C5FD'], 
            textinfo='label+percent', 
            textposition='outside', 
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_margin.update_layout(
            title=dict(text=f"INCOME MARGIN DISTRIBUTION ({selected_q})", x=0.5, font=dict(size=18, color="#0F172A", family="Arial Black")),
            annotations=[dict(text=f"Total<br><b style='font-size:26px; color:#0F172A;'>{q_ctx['total_income']:.1f}M</b>", x=0.5, y=0.5, xanchor='center', yanchor='middle', font=CHART_FONT, showarrow=False)],
            showlegend=False, 
            margin=dict(t=60, b=25, l=45, r=45), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=400, 
            font=CHART_FONT
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    # --- Line Chart Card (Title embedded in Plotly) ---
    with sc1_mid:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=q_ctx['months'], 
            y=q_ctx['income_trend'], 
            name='Total Income', 
            line=dict(color=BLUE_ACCENT, width=3, shape='spline', smoothing=0.3), 
            mode='lines+markers', 
            marker=dict(size=10, color=BLUE_ACCENT)
        ))
        fig_trend.update_layout(
            title=dict(text=f"INCOME TREND ({selected_q})", x=0.5, font=dict(size=18, color="#0F172A", family="Arial Black")),
            margin=dict(t=60, b=30, l=30, r=30), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, 
            xaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=16)), 
            yaxis=dict(
                showgrid=True, gridcolor='#E2E8F0', 
                tickfont=dict(color="#0F172A", size=16), 
                zeroline=False,
                tickformat="d",
                ticksuffix=" Mns"
            ), 
            height=400, 
            font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- Right-Side Rate Cards ---
    rates_boxes_html = ""
    for month_info in q_rates_list:
        rates_boxes_html += f"""
        <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; text-align: left;'>
            <div style='font-size: 14px; font-weight: 800; color: #2563EB; text-transform: uppercase; letter-spacing: 0.5px;'>{month_info['month']}</div>
            <div style='font-size: 15px; font-weight: 700; color: #0F172A; margin-top: 4px; line-height: 1.4;'>{month_info['inline']}</div>
        </div>
        """

    with sc1_cards:
        st.markdown(f"""
            <div class='html-card'>
                <div class='html-card-title'>BANK PROFIT RATES ({selected_q})</div>
                <div style='width: 100%;'>{rates_boxes_html}</div>
            </div>
        """, unsafe_allow_html=True)

    # SCREEN 2: BOTTOM SECTION
    st.markdown("""
        <div class="screen-2-header">
            <h3>Detailed Treasury Portfolio Breakdown</h3>
        </div>
    """, unsafe_allow_html=True)

    bot1, bot2, bot3 = st.columns([1, 1, 1.4], gap="large")

    with bot1:
        fig_treasury = go.Figure(data=[go.Pie(
            labels=['OSR Funds', 'LR Funds', 'WV Greenfin', 'RPA A/c', 'Inv/CDEL', 'Operational'], 
            values=[osr_funds, lr_funds, wv_greenfin, rpa_acc, inv_cdel, op_funds], hole=0.60,
            marker_colors=[BLUE_ACCENT, '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#CBD5E1'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_treasury.update_layout(
            title=dict(text="TREASURY POOL SPLIT", x=0.5, font=dict(size=18, color="#0F172A", family="Arial Black")),
            showlegend=False, margin=dict(t=60, b=25, l=25, r=25), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, font=CHART_FONT)
        st.plotly_chart(fig_treasury, use_container_width=True)

    with bot2:
        fig_exp = go.Figure(data=[go.Pie(
            labels=['OSR Savings', 'RPA Savings', 'Escrow'], values=[osr_q1, rpa_q1, esc_q1] if osr_q1 > 0 else [97.38, 1.15, 1.00], hole=0.60,
            marker_colors=[GREEN_ACCENT, '#34D399', '#6EE7B7'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_exp.update_layout(
            title=dict(text="INCOME TYPE BREAKDOWN", x=0.5, font=dict(size=18, color="#0F172A", family="Arial Black")),
            showlegend=False, margin=dict(t=60, b=25, l=25, r=25), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, font=CHART_FONT)
        st.plotly_chart(fig_exp, use_container_width=True)

    with bot3:
        fig_bar = go.Figure()
        categories = ['Operational', 'WV Greenfin', 'RPA A/c', 'Inv/CDEL', 'LR Funds', 'OSR Funds']
        fig_bar.add_trace(go.Bar(y=categories, x=[op_funds, wv_greenfin, rpa_acc, inv_cdel, lr_funds, osr_funds], name='Actual Pool', orientation='h', marker_color=BLUE_ACCENT))
        fig_bar.update_layout(
            title=dict(text="FUND POOL ALLOCATION", x=0.5, font=dict(size=18, color="#0F172A", family="Arial Black")),
            barmode='group', margin=dict(t=60, b=30, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#0F172A", size=15)), 
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0', tickfont=dict(color="#0F172A", size=16), ticksuffix="M"), 
            yaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=16)), 
            height=400, font=CHART_FONT
        )
        st.plotly_chart(fig_bar, use_container_width=True)
