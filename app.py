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
    df_dash = pd.read_excel(EXCEL_FILE, sheet_name='Dashboard ')
    total_income_jul = df_dash.iloc[8, 2] if not pd.isna(df_dash.iloc[8, 2]) else 99524284
    
    df_pool = pd.read_excel(EXCEL_FILE, sheet_name='Treasury Pool')
    total_pool_val = df_pool.iloc[10, 2] if not pd.isna(df_pool.iloc[10, 2]) else 15586710293

    lr_funds = df_pool.iloc[3, 2] / 1e6
    osr_funds = df_pool.iloc[4, 2] / 1e6
    inv_cdel = df_pool.iloc[5, 2] / 1e6
    rpa_acc = df_pool.iloc[6, 2] / 1e6
    wv_greenfin = df_pool.iloc[7, 2] / 1e6
    op_funds = df_pool.iloc[8, 2] / 1e6

    df_mpr = pd.read_excel(EXCEL_FILE, sheet_name='MPR')
    mpr_rate = float(df_mpr.iloc[0]['MPC Rate']) * 100
    next_mpr_date = pd.to_datetime(df_mpr.iloc[1]['MPC Meeting Date']).strftime('%b %d, %Y')

    df_rates = pd.read_excel(EXCEL_FILE, sheet_name='Profit Rates', header=None)
except Exception as e:
    total_income_jul, total_pool_val, mpr_rate = 99524284, 15586710293, 11.50
    next_mpr_date = "Sep 14, 2026"
    lr_funds, osr_funds, inv_cdel, rpa_acc, wv_greenfin, op_funds = 5521.09, 9310.81, 98.91, 250.56, 337.10, 68.24
    df_rates = pd.DataFrame()

# Helper to fetch bank profit rates per quarter directly from Excel
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
        if not df_rates.empty and len(df_rates) > 3 and col_idx < df_rates.shape[1]:
            raw_val = df_rates.iloc[3, col_idx]
        
        # Display 'Pending / Not Updated' if cell in Excel is blank/NaN
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

# Quarterly Data Mapping Engine 
quarter_data = {
    "Q1": {
        "period": "Q1 (Jul - Sep 2026)",
        "total_income": 298.57,
        "treasury_pool": total_pool_val / 1e6,
        "forecasted_income": 312.40,
        "annual_yield": "11.30%",
        "months": ['Jul 26', 'Aug 26', 'Sep 26'],
        "income_trend": [99.5, 105.2, 107.8],
        "margin_labels": ['OSR Savings', 'Operational Fees', 'Interest Income', 'Core Income'],
        "margin_values": [97.38, 45.00, 105.00, 51.19]
    },
    "Q2": {
        "period": "Q2 (Oct - Dec 2026)",
        "total_income": 310.25,
        "treasury_pool": 15890.70,
        "forecasted_income": 325.80,
        "annual_yield": "11.45%",
        "months": ['Oct 26', 'Nov 26', 'Dec 26'],
        "income_trend": [102.1, 104.3, 103.8],
        "margin_labels": ['OSR Savings', 'Operational Fees', 'Interest Income', 'Core Income'],
        "margin_values": [98.50, 48.20, 110.00, 53.55]
    },
    "Q3": {
        "period": "Q3 (Jan - Mar 2027)",
        "total_income": 322.80,
        "treasury_pool": 16278.35,
        "forecasted_income": 338.50,
        "annual_yield": "11.60%",
        "months": ['Jan 27', 'Feb 27', 'Mar 27'],
        "income_trend": [105.4, 108.2, 109.2],
        "margin_labels": ['OSR Savings', 'Operational Fees', 'Interest Income', 'Core Income'],
        "margin_values": [101.20, 50.00, 115.00, 56.60]
    },
    "Q4": {
        "period": "Q4 (Apr - Jun 2027)",
        "total_income": 335.40,
        "treasury_pool": 16500.00,
        "forecasted_income": 350.00,
        "annual_yield": "11.75%",
        "months": ['Apr 27', 'May 27', 'Jun 27'],
        "income_trend": [110.1, 112.3, 113.0],
        "margin_labels": ['OSR Savings', 'Operational Fees', 'Interest Income', 'Core Income'],
        "margin_values": [104.50, 52.00, 120.00, 58.90]
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
                <h1 style='color: #000000; font-size: 56px; letter-spacing: 2px; margin-bottom: 12px; font-weight: 900;'>KARANDAAZ TREASURY</h1>
                <p style='color: #64748B; font-size: 22px; font-weight: 600; letter-spacing: 1px;'>Loading FY26-27 Quarterly Dashboard...</p>
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

# 3. Custom CSS Architecture
st.markdown("""
    <style>
    * { font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important; box-sizing: border-box; }
    html, body, .stApp { background-color: #F8FAFC !important; margin: 0 !important; padding: 0 !important; }
    header { visibility: hidden; height: 0; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }

    /* Top Glowing Header */
    .header-container { display: flex; align-items: center; justify-content: center; margin-top: 0px !important; margin-bottom: 12px; }
    .glow-line { height: 3px; flex-grow: 1; max-width: 380px; background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent); box-shadow: 0 0 12px rgba(59, 130, 246, 0.6); }
    .header-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 40px; margin: 0 20px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05); font-weight: 900; font-size: 26px; color: #000000; letter-spacing: 1.5px; text-transform: uppercase; }

    /* Centered & Scaled Top KPI Cards */
    .kpi-card { 
        background: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        border-radius: 14px; 
        padding: 22px 18px; 
        box-shadow: 0 4px 14px rgba(0,0,0,0.03); 
        height: 100%; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        text-align: center; 
        transition: transform 0.2s ease, box-shadow 0.2s ease; 
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.07); }
    .kpi-title { font-size: 14px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.8px; width: 100%; }
    .kpi-value { font-size: 30px; font-weight: 900; color: #0F172A; line-height: 1.2; margin-top: 8px; width: 100%; }
    .kpi-sub { font-size: 13px; font-weight: 600; color: #64748B; margin-top: 6px; width: 100%; }
    .kpi-divider { border: 0; border-top: 1px solid #E2E8F0; margin: 8px 0; width: 85%; }

    /* Unified Card Containers for Header + Chart */
    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #2563EB;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(0,0,0,0.08); }
    
    .card-title {
        font-size: 15px;
        font-weight: 800;
        color: #0F172A;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-align: center;
        margin-bottom: 12px;
        width: 100%;
    }

    /* Refined Bank Profit Rates Container */
    .rate-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #2563EB;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .rate-card:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(0,0,0,0.08); }
    .rate-card-title { font-size: 14px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.8px; width: 100%; }

    div[data-testid="stPlotlyChart"] { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }

    .screen-2-header { margin-top: 40px; margin-bottom: 20px; text-align: center; }
    .screen-2-header h3 { font-size: 20px; font-weight: 900; color: #0F172A; letter-spacing: 1.2px; text-transform: uppercase; margin: 0; }
    div[data-baseweb="select"] > div { border-radius: 10px; font-size: 14px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

CHART_FONT = dict(family="Segoe UI, Roboto, sans-serif", color="#0F172A", size=13)
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

    # Quarter Selection Dropdown
    col_e1, col_date, col_e2 = st.columns([1, 0.25, 1])
    with col_date:
        selected_q = st.selectbox("", ["Q1", "Q2", "Q3", "Q4"], label_visibility="collapsed")

    q_ctx = quarter_data[selected_q]
    q_rates_list = get_quarter_rates(selected_q)
    st.write("")

    # 4 Centered Top KPI Cards
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

    # Screen 1 Charts with Bank Profit Rates (All 3 months) & MhePR Cards
    sc1_left, sc1_mid, sc1_cards = st.columns([1, 1.4, 0.9], gap="medium")

    # --- Donut Chart Card ---
    with sc1_left:
        st.markdown(f"<div class='card'><div class='card-title'>INCOME MARGIN DISTRIBUTION ({selected_q})</div>", unsafe_allow_html=True)
        fig_margin = go.Figure(data=[go.Pie(
            labels=q_ctx['margin_labels'], 
            values=q_ctx['margin_values'], hole=0.68,
            marker_colors=[BLUE_ACCENT, '#60A5FA', GREEN_ACCENT, '#93C5FD'], 
            textinfo='label+percent', 
            textposition='outside', 
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_margin.update_layout(
            annotations=[dict(text=f"Total<br><b style='font-size:22px; color:#0F172A;'>{q_ctx['total_income']:.1f}M</b>", x=0.5, y=0.5, xanchor='center', yanchor='middle', font=CHART_FONT, showarrow=False)],
            showlegend=False, 
            margin=dict(t=20, b=20, l=40, r=40), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=310, 
            font=CHART_FONT
        )
        st.plotly_chart(fig_margin, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Line Chart Card ---
    with sc1_mid:
        st.markdown(f"<div class='card'><div class='card-title'>INCOME TREND ({selected_q})</div>", unsafe_allow_html=True)
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=q_ctx['months'], 
            y=q_ctx['income_trend'], 
            name='Total Income', 
            line=dict(color=BLUE_ACCENT, width=3, shape='spline', smoothing=0.3), 
            mode='lines+markers', 
            marker=dict(size=9, color=BLUE_ACCENT)
        ))
        
        fig_trend.update_layout(
            margin=dict(t=15, b=20, l=20, r=20), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, 
            xaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=13)), 
            yaxis=dict(
                showgrid=True, gridcolor='#E2E8F0', 
                tickfont=dict(color="#0F172A", size=13), 
                zeroline=False,
                tickformat="d",
                ticksuffix=" PKR Mns"
            ), 
            height=310, 
            font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Right-Side Rate Cards: Profit Rates across all 3 months of Quarter + MhePR ---
    rates_boxes_html = ""
    for month_info in q_rates_list:
        rates_boxes_html += f"""
        <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px 10px; margin-bottom: 6px; text-align: left;'>
            <div style='font-size: 11px; font-weight: 800; color: #2563EB; text-transform: uppercase; letter-spacing: 0.5px;'>{month_info['month']}</div>
            <div style='font-size: 12px; font-weight: 700; color: #0F172A; margin-top: 2px; line-height: 1.2;'>{month_info['inline']}</div>
        </div>
        """

    with sc1_cards:
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; height: 380px; justify-content: space-between; gap: 12px;'>
                <div class='rate-card' style='height: 250px;'>
                    <div class='rate-card-title'>Bank Profit Rates ({selected_q})</div><hr class='kpi-divider' style='margin: 6px 0 8px 0;'>
                    <div style='width: 100%;'>{rates_boxes_html}</div>
                </div>
                <div class='kpi-card' style='height: 118px; border-top: 4px solid #2563EB;'>
                    <div class='kpi-title' style='font-size: 13px;'>MhePR</div><hr class='kpi-divider' style='margin: 4px 0;'>
                    <div class='kpi-value' style='color:#2563EB; font-size: 24px;'>{mpr_rate:.2f}%</div>
                    <div class='kpi-sub' style='margin-top: 2px;'>Next Date: {next_mpr_date}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # SCREEN 2: BOTTOM SECTION
    st.markdown("""
        <div class="screen-2-header">
            <h3>Detailed Treasury Portfolio Breakdown</h3>
        </div>
    """, unsafe_allow_html=True)

    bot1, bot2, bot3 = st.columns([1, 1, 1.4], gap="medium")

    with bot1:
        st.markdown(f"<div class='card' style='border-top-color:#10B981;'><div class='card-title'>TREASURY POOL SPLIT</div>", unsafe_allow_html=True)
        fig_treasury = go.Figure(data=[go.Pie(
            labels=['OSR Funds', 'LR Funds', 'WV Greenfin', 'RPA A/c', 'Inv/CDEL', 'Operational'], 
            values=[osr_funds, lr_funds, wv_greenfin, rpa_acc, inv_cdel, op_funds], hole=0.60,
            marker_colors=[BLUE_ACCENT, '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#CBD5E1'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_treasury.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, font=CHART_FONT)
        st.plotly_chart(fig_treasury, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bot2:
        st.markdown(f"<div class='card' style='border-top-color:#10B981;'><div class='card-title'>INCOME TYPE BREAKDOWN</div>", unsafe_allow_html=True)
        fig_exp = go.Figure(data=[go.Pie(
            labels=['OSR Savings', 'RPA Savings', 'Escrow'], values=[97.38, 1.15, 1.00], hole=0.60,
            marker_colors=[GREEN_ACCENT, '#34D399', '#6EE7B7'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_exp.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, font=CHART_FONT)
        st.plotly_chart(fig_exp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bot3:
        st.markdown(f"<div class='card' style='border-top-color:#10B981;'><div class='card-title'>FUND POOL ALLOCATION</div>", unsafe_allow_html=True)
        fig_bar = go.Figure()
        categories = ['Operational', 'WV Greenfin', 'RPA A/c', 'Inv/CDEL', 'LR Funds', 'OSR Funds']
        fig_bar.add_trace(go.Bar(y=categories, x=[68, 337, 250, 98, 5521, 9310], name='Actual Pool', orientation='h', marker_color=BLUE_ACCENT))
        fig_bar.update_layout(
            barmode='group', margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#0F172A", size=12)), 
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0', tickfont=dict(color="#0F172A", size=13), ticksuffix="M"), 
            yaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=13)), 
            height=300, font=CHART_FONT
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
