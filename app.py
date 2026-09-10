import streamlit as st
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(page_title="Quarterly Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Splash Screen & Loading Animation
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 80vh; flex-direction: column; text-align: center; animation: fadeOut 0.5s ease-in 2s forwards;'>
                <h1 style='color: #0B2545; font-size: 56px; letter-spacing: 1px; margin-bottom: 10px; font-weight: 700;'>KARANDAAZ PAKISTAN</h1>
                <p style='color: #333333; font-size: 20px; font-weight: 400;'>Loading Treasury Financial Data...</p>
                <div class="loader"></div>
            </div>
            <style>
            .loader { border: 6px solid #E0E6ED; border-top: 6px solid #0B2545; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-top: 20px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
            .stApp { background-color: #FFFFFF; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
    
    splash.empty()
    st.session_state.first_load = False

# 3. Typography & Styling: White Background, Black Text, Dark Navy Blue Headers
st.markdown("""
    <style>
    * {
        font-family: 'Roboto', 'Arial', sans-serif !important;
        font-style: normal !important;
        text-decoration: none !important;
    }

    @keyframes smoothLoad {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 0rem; 
        max-width: 98%; 
        animation: smoothLoad 1s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
    }
    
    /* App White Background */
    .stApp { 
        background-color: #FFFFFF !important; 
    }

    /* Dark Navy Blue Headers */
    h1, h2, h3, h4, h5, h6 { 
        color: #0B2545 !important; 
        font-weight: 700 !important; 
    }

    /* White Metric Cards with Navy Borders */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #D1D9E6;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(11, 37, 69, 0.08);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .metric-card:hover { 
        transform: translateY(-3px); 
        border-color: #0B2545; 
    }
    
    .metric-title { 
        color: #0B2545; 
        font-size: 15px; 
        margin-bottom: 5px; 
        font-weight: 700; 
    }
    .metric-value { 
        color: #111111; 
        font-size: 28px; 
        font-weight: 700; 
        margin: 0; 
    }
    .metric-sub { 
        color: #4A5568; 
        font-size: 12px; 
        font-weight: 400; 
        margin-top: 5px; 
        line-height: 1.3; 
    }
    </style>
""", unsafe_allow_html=True)

# Shared Color Constants & Font Settings
NAVY_BLUE = "#0B2545"
TEXT_BLACK = "#111111"
GRID_GRAY = "#E2E8F0"
CHART_FONT = dict(family="Roboto, Arial, sans-serif", color=TEXT_BLACK, size=12)

with st.spinner("Rendering Visualizations..."):
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 15px;'>Quarterly Financial Performance Dashboard - Q2 Closing (Apr-Jun)</h2>", unsafe_allow_html=True)

    # --- TOP ROW ---
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
            marker_colors=['#0B2545', '#134074', '#00A896'],
            textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2)), pull=[0.04, 0, 0] 
        )])
        fig_margin.update_layout(
            title=dict(text="Net Income Margin Distribution", font=dict(family="Roboto, Arial, sans-serif", color=NAVY_BLUE, size=14, weight='bold'), x=0.5),
            annotations=[dict(text="Margin<br><b style='font-size:22px; color:#0B2545;'>28.0%</b>", x=0.5, y=0.5, font=CHART_FONT, showarrow=False)],
            showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250,
            font=CHART_FONT
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    with top_col3:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[65000, 78000, 87000], name='Total Income', line=dict(color='#0B2545', width=3, shape='spline'), mode='lines+markers', marker=dict(size=7, color='#00A896')))
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[48000, 55000, 65000], name='Total Expenses', line=dict(color='#4A90E2', width=3, shape='spline'), mode='lines+markers', marker=dict(size=7)))
        fig_trend.update_layout(
            title=dict(text="Profit & Loss Quarterly Trend (Apr-Jun)", font=dict(family="Roboto, Arial, sans-serif", color=NAVY_BLUE, size=14, weight='bold'), x=0.5),
            margin=dict(t=30, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=0.95, bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=GRID_GRAY, zeroline=False), height=250,
            font=CHART_FONT
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- BOTTOM ROW ---
    bot_col1, bot_col2, bot_col3, bot_col4 = st.columns([1.2, 1.2, 1, 1.8])

    with bot_col1:
        fig_treasury = go.Figure(data=[go.Pie(
            labels=['T-Bills', 'Corp Bonds', 'Cash/Equiv', 'Sov Bonds', 'REITs'],
            values=[35, 25, 20, 15, 5], hole=0.6,
            marker_colors=['#0B2545', '#134074', '#2A6F97', '#00A896', '#62B6CB'],
            textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2)), pull=[0.04, 0, 0, 0, 0]
        )])
        fig_treasury.update_layout(
            title=dict(text="Treasury Portfolio Split", font=dict(family="Roboto, Arial, sans-serif", color=NAVY_BLUE, size=14, weight='bold'), x=0.5),
            showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250,
            font=CHART_FONT
        )
        st.plotly_chart(fig_treasury, use_container_width=True)

    with bot_col2:
        fig_exp = go.Figure(data=[go.Pie(
            labels=['Salaries', 'R&D', 'Rent', 'Marketing', 'Infra'],
            values=[40, 18, 15, 12, 15], hole=0.6,
            marker_colors=['#0B2545', '#1D4ED8', '#00A896', '#3B82F6', '#93C5FD'],
            textinfo='label+percent', textposition='outside',
            marker=dict(line=dict(color='#FFFFFF', width=2)), pull=[0.04, 0, 0, 0, 0]
        )])
        fig_exp.update_layout(
            title=dict(text="Expense Breakdown Q2", font=dict(family="Roboto, Arial, sans-serif", color=NAVY_BLUE, size=14, weight='bold'), x=0.5),
            showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250,
            font=CHART_FONT
        )
        st.plotly_chart(fig_exp, use_container_width=True)

    with bot_col3:
        st.markdown("""
            <div class='metric-card' style='margin-top:15px; padding: 22px 10px;'>
                <div class='metric-title'>Current Highest Profit</div>
                <div class='metric-value' style='color: #0B2545; font-size: 24px;'>5.35% <span style='font-size:14px; font-weight:400;'>p.a.</span></div>
                <div class='metric-sub'>Premier Trust Bank<br>July 2024</div>
            </div>
            <div class='metric-card' style='padding: 22px 10px;'>
                <div class='metric-title'>MhePR</div>
                <div class='metric-value' style='color: #0B2545; font-size: 24px;'>4.80%</div>
                <div class='metric-sub'>Next MPR Date:<br>August 14, 2024</div>
            </div>
        """, unsafe_allow_html=True)

    with bot_col4:
        fig_bar = go.Figure()
        categories = ['Others', 'Infra', 'Market', 'Rent', 'R&D', 'Salaries']
        actual = [7048, 22030, 10488, 11343, 15580, 25580]
        budget = [3253, 17800, 13300, 5820, 9200, 28500]
        
        fig_bar.add_trace(go.Bar(y=categories, x=budget, name='Budget', orientation='h', marker_color='#134074'))
        fig_bar.add_trace(go.Bar(y=categories, x=actual, name='Actual', orientation='h', marker_color='#00A896'))
        
        fig_bar.update_layout(
            title=dict(text="Q2 Budget vs. Actual", font=dict(family="Roboto, Arial, sans-serif", color=NAVY_BLUE, size=14, weight='bold'), x=0.5),
            barmode='group', margin=dict(t=30, b=20, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=0.95, bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(showgrid=True, gridcolor=GRID_GRAY, zeroline=False), yaxis=dict(showgrid=False), height=250,
            font=CHART_FONT
        )
        st.plotly_chart(fig_bar, use_container_width=True)
