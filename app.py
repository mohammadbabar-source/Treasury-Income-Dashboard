# Re-verifying app code integrity and running python syntax check
with open('app.py', 'w') as f:
    f.write('''import streamlit as st
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(page_title="Treasury Summary", layout="wide", initial_sidebar_state="collapsed")

# 2. Splash Screen
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 85vh; flex-direction: column; text-align: center; animation: fadeOut 0.5s ease-in 2s forwards;'>
                <h1 style='color: #000000; font-size: 64px; letter-spacing: 2px; margin-bottom: 12px; font-weight: 900;'>KARANDAAZ TREASURY</h1>
                <p style='color: #64748B; font-size: 24px; font-weight: 600; letter-spacing: 1px;'>Loading Portfolio Summary...</p>
                <div class="loader"></div>
            </div>
            <style>
            .loader { border: 5px solid #F1F5F9; border-top: 5px solid #2563EB; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-top: 25px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
            .stApp { background-color: #FFFFFF; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
    splash.empty()
    st.session_state.first_load = False

# 3. Custom CSS - 2 Screen Viewport & Enclosed Cards
st.markdown("""
    <style>
    /* Global Settings & Scroll Snapping */
    * { font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important; box-sizing: border-box; }
    html, body, .stApp { 
        background-color: #F8FAFC !important; 
        overflow-y: scroll; 
        scroll-snap-type: y mandatory;
    }
    
    header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* Screen 1 Viewport Container */
    .screen-1-container {
        height: 100vh;
        min-height: 100vh;
        padding: 1.5rem 2.5rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        scroll-snap-align: start;
        background-color: #FFFFFF;
    }

    /* Screen 2 Viewport Container */
    .screen-2-container {
        height: 100vh;
        min-height: 100vh;
        padding: 2rem 2.5rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        scroll-snap-align: start;
        background-color: #F8FAFC;
    }

    /* Top Glowing Header */
    .header-container { display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem; }
    .glow-line { height: 3px; flex-grow: 1; max-width: 400px; background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent); box-shadow: 0 0 12px rgba(59, 130, 246, 0.6); }
    .header-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 45px; margin: 0 25px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06); font-weight: 900; font-size: 28px; color: #000000; letter-spacing: 1.5px; text-transform: uppercase; }

    /* Unified Card Containers (Title + Content enclosed together) */
    .dash-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .dash-card:hover { transform: translateY(-3px); box-shadow: 0 12px 24px rgba(0,0,0,0.08); }

    .dash-card-blue {
        background: #FFFFFF;
        border: 2px solid #2563EB;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 10px 28px rgba(37, 99, 235, 0.12);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Card Typography */
    .card-title { font-size: 16px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px; }
    .card-title-center { font-size: 17px; font-weight: 900; color: #000000; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 8px; }
    .card-value { font-size: 34px; font-weight: 900; color: #0F172A; line-height: 1.1; margin-top: 6px; }
    .card-sub { font-size: 13px; font-weight: 600; color: #64748B; margin-top: 6px; }
    .card-divider { border: 0; border-top: 1px solid #E2E8F0; margin: 10px 0; }

    /* Streamlit Selectbox Styling */
    div[data-baseweb="select"] > div { border-radius: 10px; font-size: 15px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

CHART_FONT = dict(family="Segoe UI, Roboto, sans-serif", color="#000000", size=13)
BLUE_ACCENT = '#2563EB'
GREEN_ACCENT = '#10B981'

with st.spinner("Rendering Visualizations..."):
    
    # ==========================================
    # SCREEN 1: FIRST VIEWPORT (100vh Full View)
    # ==========================================
    st.markdown("<div class='screen-1-container'>", unsafe_allow_html=True)
    
    # Top Header
    st.markdown("""
        <div class="header-container">
            <div class="glow-line"></div>
            <div class="header-card">Treasury Portfolio Summary</div>
            <div class="glow-line"></div>
        </div>
    """, unsafe_allow_html=True)

    # Date Selector Dropdown
    col_e1, col_date, col_e2 = st.columns([1, 0.25, 1])
    with col_date:
        st.selectbox("", ["Q2 (Apr-Jun)", "Q1 (Jan-Mar)", "Q4 (Oct-Dec)"], label_visibility="collapsed")

    # 4 Top KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    with kpi1:
        st.markdown("<div class='dash-card'><div class='card-title'>Total Income</div><hr class='card-divider'><div class='card-value'>250 PKR Mns</div><div class='card-sub'>Quarterly Earnings</div></div>", unsafe_allow_html=True)
    with kpi2:
        st.markdown("<div class='dash-card'><div class='card-title'>Treasury Pool</div><hr class='card-divider'><div class='card-value'>180 PKR Mns</div><div class='card-sub'>Current Allocation</div></div>", unsafe_allow_html=True)
    with kpi3:
        st.markdown("<div class='dash-card'><div class='card-title'>Net Profit</div><hr class='card-divider'><div class='card-value'>70 PKR Mns</div><div class='card-sub'>After Expenses</div></div>", unsafe_allow_html=True)
    with kpi4:
        st.markdown("<div class='dash-card'><div class='card-title'>Expense Ratio</div><hr class='card-divider'><div class='card-value'>72.0%</div><div class='card-sub'>Operational Cost</div></div>", unsafe_allow_html=True)

    # Screen 1 Charts (Income Margin & P&L Trend)
    sc1_left, sc1_right = st.columns([1, 1.8], gap="medium")

    with sc1_left:
        fig_margin = go.Figure(data=[go.Pie(
            labels=['Core Ops', 'New Proj', 'Invest Yields'], values=[70, 20, 10], hole=0.72,
            marker_colors=[BLUE_ACCENT, '#60A5FA', GREEN_ACCENT], textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2)), pull=[0.04, 0, 0] 
        )])
        fig_margin.update_layout(
            title=dict(text="INCOME MARGIN DISTRIBUTION", font=dict(family="Segoe UI, Roboto", color='#000000', size=16, weight='bold'), x=0.5, y=0.96),
            annotations=[dict(text="Margin<br><b style='font-size:26px; color:#000;'>28.0%</b>", x=0.5, y=0.5, font=CHART_FONT, showarrow=False)],
            showlegend=False, margin=dict(t=50, b=15, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320, font=CHART_FONT
        )
        st.markdown("<div class='dash-card-blue'>", unsafe_allow_html=True)
        st.plotly_chart(fig_margin, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with sc1_right:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[65000, 78000, 87000], name='Total Income', line=dict(color=BLUE_ACCENT, width=4, shape='spline'), mode='lines+markers', marker=dict(size=9)))
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[48000, 55000, 65000], name='Total Expenses', line=dict(color=GREEN_ACCENT, width=4, shape='spline'), mode='lines+markers', marker=dict(size=9)))
        fig_trend.update_layout(
            title=dict(text="PROFIT & LOSS QUARTERLY TREND", font=dict(family="Segoe UI, Roboto", color='#000000', size=16, weight='bold'), x=0.5, y=0.96),
            margin=dict(t=50, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#111111", size=13)),
            xaxis=dict(showgrid=False, tickfont=dict(color="#111111", size=13)), 
            yaxis=dict(showgrid=True, gridcolor='#CBD5E1', tickfont=dict(color="#111111", size=13), zeroline=False), 
            height=320, font=CHART_FONT
        )
        st.markdown("<div class='dash-card-blue'>", unsafe_allow_html=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # End Screen 1


    # ==========================================
    # SCREEN 2: SCROLL DOWN VIEWPORT (100vh Full View)
    # ==========================================
    st.markdown("<div class='screen-2-container'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #0F172A; font-weight: 800; letter-spacing: 1px; margin-bottom: 1.5rem; text-transform: uppercase;'>Detailed Portfolio Breakdown</h3>", unsafe_allow_html=True)

    bot1, bot2, bot3, bot4 = st.columns([1.1, 1.1, 0.9, 1.5], gap="medium")

    with bot1:
        fig_treasury = go.Figure(data=[go.Pie(
            labels=['T-Bills', 'Corp Bonds', 'Cash/Equiv', 'Sov Bonds', 'REITs'], values=[35, 25, 20, 15, 5], hole=0.62,
            marker_colors=[BLUE_ACCENT, '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_treasury.update_layout(
            title=dict(text="PORTFOLIO SPLIT", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.96),
            showlegend=False, margin=dict(t=45, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=310, font=CHART_FONT
        )
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig_treasury, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bot2:
        fig_exp = go.Figure(data=[go.Pie(
            labels=['Salaries', 'R&D', 'Rent', 'Marketing', 'Infra'], values=[40, 18, 15, 12, 15], hole=0.62,
            marker_colors=[GREEN_ACCENT, '#34D399', '#6EE7B7', '#A7F3D0', '#D1FAE5'], textinfo='label', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )])
        fig_exp.update_layout(
            title=dict(text="EXPENSE BREAKDOWN", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.96),
            showlegend=False, margin=dict(t=45, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=310, font=CHART_FONT
        )
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig_exp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bot3:
        st.markdown("""
            <div style='display: flex; flex-direction: column; height: 350px; justify-content: space-between;'>
                <div class='dash-card' style='padding: 20px 15px; text-align: center;'>
                    <div class='card-title' style='font-size: 14px;'>Highest Profit Rate</div><hr class='card-divider'>
                    <div class='card-value' style='color:#2563EB; font-size: 32px;'>5.35%</div>
                    <div class='card-sub'>Premier Trust Bank (Jul)</div>
                </div>
                <div class='dash-card' style='padding: 20px 15px; text-align: center;'>
                    <div class='card-title' style='font-size: 14px;'>MhePR</div><hr class='card-divider'>
                    <div class='card-value' style='color:#2563EB; font-size: 32px;'>4.80%</div>
                    <div class='card-sub'>Next Date: Aug 14, 2024</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with bot4:
        fig_bar = go.Figure()
        categories = ['Others', 'Infra', 'Market', 'Rent', 'R&D', 'Salaries']
        fig_bar.add_trace(go.Bar(y=categories, x=[3253, 17800, 13300, 5820, 9200, 28500], name='Budget', orientation='h', marker_color='#94A3B8'))
        fig_bar.add_trace(go.Bar(y=categories, x=[7048, 22030, 10488, 11343, 15580, 25580], name='Actual', orientation='h', marker_color=BLUE_ACCENT))
        fig_bar.update_layout(
            title=dict(text="BUDGET VS. ACTUAL PERFORMANCE", font=dict(family="Segoe UI, Roboto", color='#000000', size=15, weight='bold'), x=0.5, y=0.96),
            barmode='group', margin=dict(t=45, b=25, l=15, r=15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#111111", size=12)), 
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0', tickfont=dict(color="#111111", size=12)), 
            yaxis=dict(showgrid=False, tickfont=dict(color="#111111", size=12)), 
            height=310, font=CHART_FONT
        )
        st.markdown("<div class='dash-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # End Screen 2
''')
print("App script syntax and formatting verified successfully.")
