import streamlit as st
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
            <div style='display: flex; justify-content: center; align-items: center; height: 80vh; flex-direction: column; text-align: center; animation: fadeOut 0.5s ease-in 2s forwards;'>
                <h1 style='color: #000000; font-size: 56px; letter-spacing: 1.5px; margin-bottom: 10px; font-weight: 900;'>KARANDAAZ TREASURY</h1>
                <p style='color: #64748B; font-size: 20px; font-weight: 600; letter-spacing: 1px;'>Loading Portfolio Summary...</p>
                <div class="loader"></div>
            </div>
            <style>
            .loader { border: 4px solid #F1F5F9; border-top: 4px solid #2563EB; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-top: 20px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
            .stApp { background-color: #FFFFFF; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
    splash.empty()
    st.session_state.first_load = False

# 3. Custom CSS
st.markdown("""
    <style>
    /* Global Settings */
    * { font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important; }
    .stApp { background-color: #FFFFFF !important; }
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; max-width: 96%; animation: smoothLoad 0.8s ease-out forwards; }
    @keyframes smoothLoad { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }

    /* Top Glowing Header */
    .header-container { display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; margin-top: 0.5rem; }
    .glow-line { height: 2px; flex-grow: 1; max-width: 350px; background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent); box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }
    .header-card { background: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 8px; padding: 15px 40px; margin: 0 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); font-weight: 900; font-size: 24px; color: #000000; letter-spacing: 1px; text-transform: uppercase; }

    /* Clean Shadow Cards for Metrics */
    .stage-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px 20px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); transition: transform 0.2s ease; height: 100%;}
    .stage-card:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.08); }
    .stage-card-title { font-size: 13px; font-weight: 800; color: #000000; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .stage-card-value { font-size: 24px; font-weight: 900; color: #000000; }
    .stage-card-sub { font-size: 12px; font-weight: 600; color: #64748B; margin-top: 4px; }
    .stage-card hr { border-top: 1px solid #F1F5F9; margin: 8px 0; }

    /* Blue Bordered Cards for Charts */
    .center-card { background: #FFFFFF; border: 2px solid #2563EB; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.10); margin-bottom: 15px; height: 100%; }
    .center-title { font-size: 14px; font-weight: 800; color: #000000; letter-spacing: 1px; margin-bottom: 2px; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

CHART_FONT = dict(family="Segoe UI, Roboto, sans-serif", color="#000000", size=12)
BLUE_ACCENT = '#2563EB'
GREEN_ACCENT = '#10B981'

with st.spinner("Rendering Visualizations..."):
    
    # Glowing Header
    st.markdown("""
        <div class="header-container">
            <div class="glow-line"></div>
            <div class="header-card">Treasury Portfolio Summary</div>
            <div class="glow-line"></div>
        </div>
    """, unsafe_allow_html=True)

    # Date Dropdown
    col_empty1, col_date, col_empty2 = st.columns([1, 0.2, 1])
    with col_date:
        st.selectbox("", ["Q2 (Apr-Jun)", "Q1 (Jan-Mar)", "Q4 (Oct-Dec)"], label_visibility="collapsed")
    st.write("")

    # --- TOP ROW (Metrics) ---
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown("<div class='stage-card'><div class='stage-card-title'>Total Income</div><hr><div class='stage-card-value'>250 PKR Mns</div><div class='stage-card-sub'>Quarterly Earnings</div></div>", unsafe_allow_html=True)
    with m2: st.markdown("<div class='stage-card'><div class='stage-card-title'>Treasury Pool</div><hr><div class='stage-card-value'>180 PKR Mns</div><div class='stage-card-sub'>Current Allocation</div></div>", unsafe_allow_html=True)
    with m3: st.markdown("<div class='stage-card'><div class='stage-card-title'>Net Profit</div><hr><div class='stage-card-value'>70 PKR Mns</div><div class='stage-card-sub'>After Expenses</div></div>", unsafe_allow_html=True)
    with m4: st.markdown("<div class='stage-card'><div class='stage-card-title'>Expense Ratio</div><hr><div class='stage-card-value'>72.0%</div><div class='stage-card-sub'>Operational Cost</div></div>", unsafe_allow_html=True)

    # --- MIDDLE ROW (Charts in Blue Border Cards) ---
    chart_col1, chart_col2 = st.columns([1, 1.8])

    with chart_col1:
        st.markdown("<div class='center-card'><div class='center-title'>Income Margin Distribution</div><hr style='border-top:1px solid #E2E8F0; margin: 4px 0 0 0;'>", unsafe_allow_html=True)
        fig_margin = go.Figure(data=[go.Pie(
            labels=['Core Ops', 'New Proj', 'Invest Yields'], values=[70, 20, 10], hole=0.75,
            marker_colors=[BLUE_ACCENT, '#60A5FA', GREEN_ACCENT], textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2)), pull=[0.05, 0, 0] 
        )])
        fig_margin.update_layout(
            annotations=[dict(text="Margin<br><b style='font-size:24px; color:#000;'>28.0%</b>", x=0.5, y=0.5, font=CHART_FONT, showarrow=False)],
            showlegend=False, margin=dict(t=15, b=15, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=240, font=CHART_FONT
        )
        st.plotly_chart(fig_margin, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("<div class='center-card'><div class='center-title'>Profit & Loss Quarterly Trend</div><hr style='border-top:1px solid #E2E8F0; margin: 4px 0 0 0;'>", unsafe_allow_html=True)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[65000, 78000, 87000], name='Total Income', line=dict(color=BLUE_ACCENT, width=3, shape='spline'), mode='lines+markers', marker=dict(size=8)))
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[48000, 55000, 65000], name='Total Expenses', line=dict(color=GREEN_ACCENT, width=3, shape='spline'), mode='lines+markers', marker=dict(size=8)))
        
        # High contrast axes and gridlines added here
        fig_trend.update_layout(
            margin=dict(t=15, b=25, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#111111", size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(color="#333333", size=12)), 
            yaxis=dict(showgrid=True, gridcolor='#CBD5E1', tickfont=dict(color="#333333", size=12), zeroline=False), 
            height=240, font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- BOTTOM ROW (More Charts & KPIs) ---
    bot_col1, bot_col2, bot_col3, bot_col4 = st.columns([1.2, 1.2, 1, 1.8])

    with bot_col1:
        st.markdown("<div class='stage-card'><div class='stage-card-title'>Portfolio Split</div><hr style='margin: 4px 0 0 0;'>", unsafe_allow_html=True)
        fig_treasury = go.Figure(data=[go.Pie(labels=['T-Bills', 'Corp Bonds', 'Cash/Equiv', 'Sov Bonds', 'REITs'], values=[35, 25, 20, 15, 5], hole=0.6, marker_colors=[BLUE_ACCENT, '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE'], textinfo='label', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2)))])
        fig_treasury.update_layout(showlegend=False, margin=dict(t=15, b=25, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=230, font=CHART_FONT)
        st.plotly_chart(fig_treasury, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bot_col2:
        st.markdown("<div class='stage-card'><div class='stage-card-title'>Expense Breakdown</div><hr style='margin: 4px 0 0 0;'>", unsafe_allow_html=True)
        fig_exp = go.Figure(data=[go.Pie(labels=['Salaries', 'R&D', 'Rent', 'Marketing', 'Infra'], values=[40, 18, 15, 12, 15], hole=0.6, marker_colors=[GREEN_ACCENT, '#34D399', '#6EE7B7', '#A7F3D0', '#D1FAE5'], textinfo='label', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2)))])
        fig_exp.update_layout(showlegend=False, margin=dict(t=15, b=25, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=230, font=CHART_FONT)
        st.plotly_chart(fig_exp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bot_col3:
        st.markdown("""
            <div class='stage-card' style='padding: 20px 10px; margin-bottom: 12px;'>
                <div class='stage-card-title'>Highest Profit Rate</div><hr style='margin: 6px 0;'>
                <div class='stage-card-value' style='color:#2563EB;'>5.35%</div>
                <div class='stage-card-sub'>Premier Trust Bank (Jul)</div>
            </div>
            <div class='stage-card' style='padding: 20px 10px;'>
                <div class='stage-card-title'>MhePR</div><hr style='margin: 6px 0;'>
                <div class='stage-card-value' style='color:#2563EB;'>4.80%</div>
                <div class='stage-card-sub'>Next Date: Aug 14, 2024</div>
            </div>
        """, unsafe_allow_html=True)

    with bot_col4:
        st.markdown("<div class='stage-card'><div class='stage-card-title'>Budget vs. Actual</div><hr style='margin: 4px 0 0 0;'>", unsafe_allow_html=True)
        fig_bar = go.Figure()
        categories = ['Others', 'Infra', 'Market', 'Rent', 'R&D', 'Salaries']
        fig_bar.add_trace(go.Bar(y=categories, x=[3253, 17800, 13300, 5820, 9200, 28500], name='Budget', orientation='h', marker_color='#94A3B8'))
        fig_bar.add_trace(go.Bar(y=categories, x=[7048, 22030, 10488, 11343, 15580, 25580], name='Actual', orientation='h', marker_color=BLUE_ACCENT))
        fig_bar.update_layout(
            barmode='group', margin=dict(t=15, b=30, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=0.95, font=dict(color="#111111")), 
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0', tickfont=dict(color="#333333")), 
            yaxis=dict(showgrid=False, tickfont=dict(color="#333333")), 
            height=230, font=CHART_FONT
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
