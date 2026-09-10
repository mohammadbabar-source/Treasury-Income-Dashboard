import streamlit as st
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(page_title="Quarterly Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Splash Screen & Loading Animation (Runs only once per visit)
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    # This creates a temporary container that takes over the screen
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; height: 80vh; flex-direction: column; text-align: center;'>
                <h1 style='color: #50E3C2; font-size: 60px; letter-spacing: 2px; margin-bottom: 10px;'>KARANDAAZ PAKISTAN</h1>
                <p style='color: #A0C0E0; font-size: 22px;'>Loading Treasury Financial Data...</p>
                <div class="loader"></div>
            </div>
            <style>
            /* Custom CSS Spinner */
            .loader { border: 6px solid #142340; border-top: 6px solid #50E3C2; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-top: 20px;}
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .stApp { background-color: #0A1428; }
            </style>
        """, unsafe_allow_html=True)
        time.sleep(2.5) # Simulate the loading sequence for 2.5 seconds
    
    # Destroy the splash screen to reveal the dashboard
    splash.empty()
    st.session_state.first_load = False

# 3. Custom CSS for the Dashboard
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 98%; }
    .metric-card {
        background: linear-gradient(145deg, rgba(20, 35, 60, 0.8), rgba(10, 20, 40, 0.8));
        border: 1px solid #2C4A70;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); border-color: #50E3C2; }
    .metric-title { color: #E0E0E0; font-size: 16px; margin-bottom: 5px; font-weight: 500;}
    .metric-value { color: #FFFFFF; font-size: 28px; font-weight: bold; margin: 0; text-shadow: 0 0 10px rgba(255,255,255,0.2); }
    .metric-sub { color: #A0C0E0; font-size: 12px; margin-top: 5px; line-height: 1.2; }
    .stApp { background-color: #0A1428; }
    h1, h2, h3, h4 { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# Wrap the dashboard generation in a Streamlit spinner just in case charts take a moment
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
            marker_colors=['#2C6296', '#66B3E9', '#50E3C2'],
            textinfo='label+percent', textposition='outside',
            # UPGRADED PIE STYLING: Dark borders and exploding the biggest slice
            marker=dict(line=dict(color='#0A1428', width=3)),
            pull=[0.05, 0, 0] 
        )])
        fig_margin.update_layout(
            title=dict(text="Net Income Margin Distribution", font=dict(color='white', size=14), x=0.5),
            annotations=[dict(text="Margin<br><b style='font-size:24px; color:#50E3C2'>28.0%</b>", x=0.5, y=0.5, font_color='white', showarrow=False)],
            showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    with top_col3:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[65000, 78000, 87000], name='Total Income', line=dict(color='white', width=4, shape='spline'), mode='lines+markers', marker=dict(size=8, color='#50E3C2', line=dict(width=2, color='white'))))
        fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[48000, 55000, 65000], name='Total Expenses', line=dict(color='#4B90E2', width=4, shape='spline'), mode='lines+markers', marker=dict(size=8)))
        fig_trend.update_layout(
            title=dict(text="Profit & Loss Quarterly Trend (Apr-Jun)", font=dict(color='white', size=14), x=0.5),
            margin=dict(t=30, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=0.95, bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1C2A45', zeroline=False), height=250
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- BOTTOM ROW ---
    bot_col1, bot_col2, bot_col3, bot_col4 = st.columns([1.2, 1.2, 1, 1.8])

    with bot_col1:
        fig_treasury = go.Figure(data=[go.Pie(
            labels=['T-Bills', 'Corp Bonds', 'Cash/Equiv', 'Sov Bonds', 'REITs'],
            values=[35, 25, 20, 15, 5], hole=0.6,
            marker_colors=['#2C6296', '#4B90E2', '#66B3E9', '#50E3C2', '#A3E4D7'],
            textinfo='label+percent', textposition='outside',
            # UPGRADED PIE STYLING:
            marker=dict(line=dict(color='#0A1428', width=3)),
            pull=[0.05, 0, 0, 0, 0]
        )])
        fig_treasury.update_layout(
            title=dict(text="Treasury Portfolio Split", font=dict(color='white', size=14), x=0.5),
            showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250
        )
        st.plotly_chart(fig_treasury, use_container_width=True)

    with bot_col2:
        fig_exp = go.Figure(data=[go.Pie(
            labels=['Salaries', 'R&D', 'Rent', 'Marketing', 'Infra'],
            values=[40, 18, 15, 12, 15], hole=0.6,
            marker_colors=['#229954', '#52BE80', '#50E3C2', '#A3E4D7', '#4B90E2'],
            textinfo='label+percent', textposition='outside',
            # UPGRADED PIE STYLING:
            marker=dict(line=dict(color='#0A1428', width=3)),
            pull=[0.05, 0, 0, 0, 0]
        )])
        fig_exp.update_layout(
            title=dict(text="Expense Breakdown Q2", font=dict(color='white', size=14), x=0.5),
            showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250
        )
        st.plotly_chart(fig_exp, use_container_width=True)

    with bot_col3:
        st.markdown("""
            <div class='metric-card' style='margin-top:15px; padding: 25px 10px;'>
                <div class='metric-title'>Current Highest Profit</div>
                <div class='metric-value' style='color: #50E3C2; font-size: 24px;'>5.35% <span style='font-size:14px'>p.a.</span></div>
                <div class='metric-sub'>Premier Trust Bank<br>July 2024</div>
            </div>
            <div class='metric-card' style='padding: 25px 10px;'>
                <div class='metric-title'>MhePR</div>
                <div class='metric-value' style='color: #50E3C2; font-size: 24px;'>4.80%</div>
                <div class='metric-sub'>Next MPR Date:<br>August 14, 2024</div>
            </div>
        """, unsafe_allow_html=True)

    with bot_col4:
        fig_bar = go.Figure()
        categories = ['Others', 'Infra', 'Market', 'Rent', 'R&D', 'Salaries']
        actual = [7048, 22030, 10488, 11343, 15580, 25580]
        budget = [3253, 17800, 13300, 5820, 9200, 28500]
        
        fig_bar.add_trace(go.Bar(y=categories, x=budget, name='Budget', orientation='h', marker_color='#4B90E2', marker_line_color='#0A1428', marker_line_width=1))
        fig_bar.add_trace(go.Bar(y=categories, x=actual, name='Actual', orientation='h', marker_color='#50E3C2', marker_line_color='#0A1428', marker_line_width=1))
        
        fig_bar.update_layout(
            title=dict(text="Q2 Budget vs. Actual", font=dict(color='white', size=14), x=0.5),
            barmode='group', margin=dict(t=30, b=20, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=0.95, bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(showgrid=True, gridcolor='#1C2A45', zeroline=False), yaxis=dict(showgrid=False), height=250
        )
        st.plotly_chart(fig_bar, use_container_width=True)
