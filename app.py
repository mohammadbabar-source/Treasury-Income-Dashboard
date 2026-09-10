import streamlit as st
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(page_title="Quarterly Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Splash Screen (Refined for Light Theme)
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 80vh; flex-direction: column; text-align: center; animation: fadeOut 0.5s ease-in 2s forwards;'>
                <h1 style='color: #0B2545; font-size: 56px; letter-spacing: 1px; margin-bottom: 10px; font-weight: 700;'>KARANDAAZ PAKISTAN</h1>
                <p style='color: #64748B; font-size: 20px; font-weight: 400;'>Loading Treasury Financial Data...</p>
                <div class="loader"></div>
            </div>
            <style>
            .loader { border: 4px solid #F1F5F9; border-top: 4px solid #0B2545; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-top: 20px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
            .stApp { background-color: #F8FAFC; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
    splash.empty()
    st.session_state.first_load = False

# 3. Premium Light UI CSS
st.markdown("""
    <style>
    * { font-family: 'Inter', 'Roboto', 'Arial', sans-serif !important; font-style: normal !important; text-decoration: none !important; }

    @keyframes smoothLoad { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; max-width: 96%; animation: smoothLoad 0.8s ease-out forwards; }
    
    /* Soft Off-White Background */
    .stApp { background-color: #F8FAFC !important; }

    h1, h2, h3, h4, h5, h6 { color: #0B2545 !important; font-weight: 700 !important; }

    /* Floating White Cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border-color: #CBD5E1; }
    
    .metric-title { color: #64748B; font-size: 14px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
    .metric-value { color: #0F172A; font-size: 32px; font-weight: 700; margin: 0; }
    .metric-sub { color: #94A3B8; font-size: 13px; font-weight: 400; margin-top: 6px; line-height: 1.4; }
    </style>
""", unsafe_allow_html=True)

# Cohesive Palette for Charts (Navy, Royal, Sky, Teal)
CHART_COLORS = ['#0B2545', '#2563EB', '#38BDF8', '#10B981', '#94A3B8']
CHART_FONT = dict(family="Inter, Roboto, Arial, sans-serif", color="#475569", size=12)

with st.spinner("Rendering Visualizations..."):
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Quarterly Financial Performance Dashboard - Q2 Closing (Apr-Jun)</h2>", unsafe_allow_html=True)

    top_col1, top_col2, top_col3 = st.columns([1, 1.2, 1.8])

    with top_col1:
        r1c1, r1c2 = st.columns(2)
        with r1c1: st.markdown("<div class='metric-card'><div class='metric-title'>Total Income</div><div class='metric-value'>$ 250,000</div></div>", unsafe_allow_html=True)
        with r1c2: st.markdown("<div class='metric-card'><div class='metric-title'>Total Expenses</div><div class='metric-value'>$ 180,000</div></div>", unsafe_allow_html=True)
        
        r2c1, r2c2 = st.columns(2)
        with r2c1: st.markdown("<div class='metric-card'><div class='metric-title'>Net Profit</div><div class='metric-value'>$ 70,000</div></div>", unsafe_allow_html=True)
        with r2c2: st.markdown("<div class='metric-card'><div class='metric-title'>Expense Ratio</div><div class='metric-value'>72.0%</div></div>", unsafe_allow_html=True)

    with top_col2:
        fig_margin = go.Figure(data=[go.Pie(
            labels=['Core Operations', 'New Projects', 'Investment Yields'],
            values=[70, 20, 10], hole=0.75,
            marker_colors=[CHART_COLORS[0], CHART_COLORS[1], CHART_COLORS[3]],
            textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=3)), pull=[0.05, 0, 0] 
        )])
        fig_margin.update_layout(
            title=dict(text="Net Income Margin Distribution", font=dict(color='#0B2545', size=15, weight='bold'), x=0.5),
            annotations=[dict(text="Margin<br><b style='font-size:24px; color:#0B2545;'>28.0%</b>", x=0.5, y=0.5, font=CHART_FONT, showarrow=False)],
            showlegend=False, margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, font=CHART_FONT
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    with top_col3:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[65000, 78000, 87000], name='Total Income', line=dict(color=CHART_COLORS[0], width=3, shape='spline'), mode='lines+markers', marker=dict(size=8, color=CHART_COLORS[0])))
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[48000, 55000, 65000], name='Total Expenses', line=dict(color=CHART_COLORS[2], width=3, shape='spline'), mode='lines+markers', marker=dict(size=8, color=CHART_COLORS[2])))
        fig_trend.update_layout(
            title=dict(text="Profit & Loss Quarterly Trend (Apr-Jun)", font=dict(color='#0B2545', size=15, weight='bold'), x=0.5),
            margin=dict(t=40, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=0.95, bgcolor='rgba(255,255,255,0.7)'),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#E2E8F0', zeroline=False), height=280, font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    bot_col1, bot_col2, bot_col3, bot_col4 = st.columns([1.2, 1.2, 1, 1.8])

    with bot_col1:
        fig_treasury = go.Figure(data=[go.Pie(
            labels=['T-Bills', 'Corp Bonds', 'Cash/Equiv', 'Sov Bonds', 'REITs'],
            values=[35, 25, 20, 15, 5], hole=0.65,
            marker_colors=CHART_COLORS,
            textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=3)), pull=[0.05, 0, 0, 0, 0]
        )])
        fig_treasury.update_layout(
            title=dict(text="Treasury Portfolio Split", font=dict(color='#0B2545', size=15, weight='bold'), x=0.5),
            showlegend=False, margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, font=CHART_FONT
        )
        st.plotly_chart(fig_treasury, use_container_width=True)

    with bot_col2:
        fig_exp = go.Figure(data=[go.Pie(
            labels=['Salaries', 'R&D', 'Rent', 'Marketing', 'Infra'],
            values=[40, 18, 15, 12, 15], hole=0.65,
            marker_colors=[CHART_COLORS[3], CHART_COLORS[1], CHART_COLORS[2], CHART_COLORS[0], CHART_COLORS[4]],
            textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=3)), pull=[0.05, 0, 0, 0, 0]
        )])
        fig_exp.update_layout(
            title=dict(text="Expense Breakdown Q2", font=dict(color='#0B2545', size=15, weight='bold'), x=0.5),
            showlegend=False, margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, font=CHART_FONT
        )
        st.plotly_chart(fig_exp, use_container_width=True)

    with bot_col3:
        st.markdown("""
            <div class='metric-card' style='margin-top:15px; padding: 30px 10px;'>
                <div class='metric-title'>Current Highest Profit</div>
                <div class='metric-value' style='color: #0B2545;'>5.35% <span style='font-size:16px; font-weight:400; color:#64748B;'>p.a.</span></div>
                <div class='metric-sub'>Premier Trust Bank<br>July 2024</div>
            </div>
            <div class='metric-card' style='padding: 30px 10px;'>
                <div class='metric-title'>MhePR</div>
                <div class='metric-value' style='color: #0B2545;'>4.80%</div>
                <div class='metric-sub'>Next MPR Date:<br>August 14, 2024</div>
            </div>
        """, unsafe_allow_html=True)

    with bot_col4:
        fig_bar = go.Figure()
        categories = ['Others', 'Infra', 'Market', 'Rent', 'R&D', 'Salaries']
        actual = [7048, 22030, 10488, 11343, 15580, 25580]
        budget = [3253, 17800, 13300, 5820, 9200, 28500]
        
        fig_bar.add_trace(go.Bar(y=categories, x=budget, name='Budget', orientation='h', marker_color=CHART_COLORS[4], marker_line_color=CHART_COLORS[4], marker_line_width=1))
        fig_bar.add_trace(go.Bar(y=categories, x=actual, name='Actual', orientation='h', marker_color=CHART_COLORS[0], marker_line_color=CHART_COLORS[0], marker_line_width=1))
        
        fig_bar.update_layout(
            title=dict(text="Q2 Budget vs. Actual", font=dict(color='#0B2545', size=15, weight='bold'), x=0.5),
            barmode='group', margin=dict(t=40, b=20, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=0.95, bgcolor='rgba(255,255,255,0.7)'),
            xaxis=dict(showgrid=True, gridcolor='#E2E8F0', zeroline=False), yaxis=dict(showgrid=False), height=280, font=CHART_FONT
        )
        st.plotly_chart(fig_bar, use_container_width=True)
