import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# 1. Page Configuration (Wide layout, collapsed sidebar to save space)
st.set_page_config(page_title="Quarterly Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Custom CSS to make it fit on one screen and look exactly like the image
st.markdown("""
    <style>
    /* Remove top padding to fit on one screen */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; max-width: 98%; }
    
    /* Custom metric card styling */
    .metric-card {
        background-color: rgba(20, 30, 50, 0.5);
        border: 1px solid #4B78A5;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-title { color: #E0E0E0; font-size: 16px; margin-bottom: 5px; font-weight: 500;}
    .metric-value { color: #FFFFFF; font-size: 28px; font-weight: bold; margin: 0; }
    .metric-sub { color: #A0C0E0; font-size: 12px; margin-top: 5px; line-height: 1.2; }
    
    /* Dark background for the whole app to match image */
    .stApp { background-color: #0A1428; }
    h1, h2, h3, h4 { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown("<h2 style='text-align: center; margin-bottom: 15px;'>Quarterly Financial Performance Dashboard - Q2 Closing (Apr-Jun)</h2>", unsafe_allow_html=True)

# --- TOP ROW ---
top_col1, top_col2, top_col3 = st.columns([1, 1.2, 1.8])

# Top Left: Key Metrics
with top_col1:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown("<div class='metric-card'><div class='metric-title'>Total Income</div><div class='metric-value'>$ 250,000</div></div>", unsafe_allow_html=True)
    with r1c2:
        st.markdown("<div class='metric-card'><div class='metric-title'>Total Expenses</div><div class='metric-value'>$ 180,000</div></div>", unsafe_allow_html=True)
    
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown("<div class='metric-card'><div class='metric-title'>Net Profit</div><div class='metric-value'>$ 70,000</div></div>", unsafe_allow_html=True)
    with r2c2:
        st.markdown("<div class='metric-card'><div class='metric-title'>Expense Ratio</div><div class='metric-value'>72.0%</div></div>", unsafe_allow_html=True)

# Top Middle: Income Margin Donut
with top_col2:
    fig_margin = go.Figure(data=[go.Pie(
        labels=['Core Operations', 'New Projects', 'Investment Yields'],
        values=[70, 20, 10],
        hole=0.75,
        marker_colors=['#2C6296', '#66B3E9', '#50E3C2'],
        textinfo='label+percent',
        textposition='outside'
    )])
    fig_margin.update_layout(
        title=dict(text="Net Income Margin & Revenue Distribution", font=dict(color='white', size=14), x=0.5),
        annotations=[dict(text="Margin<br><b style='font-size:24px'>28.0%</b><br><span style='font-size:10px'>Strong Q2 Performance</span>", x=0.5, y=0.5, font_color='white', showarrow=False)],
        showlegend=False,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250
    )
    st.plotly_chart(fig_margin, use_container_width=True)

# Top Right: P&L Trend Line
with top_col3:
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[65000, 78000, 87000], name='Total Income ($)', line=dict(color='white', width=3), mode='lines+markers'))
    fig_trend.add_trace(go.Scatter(x=['Apr', 'May', 'Jun'], y=[48000, 55000, 65000], name='Total Expenses ($)', line=dict(color='#4B90E2', width=3), mode='lines+markers'))
    fig_trend.update_layout(
        title=dict(text="Profit & Loss Quarterly Trend (Apr-Jun)", font=dict(color='white', size=14), x=0.5),
        margin=dict(t=30, b=20, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(yanchor="bottom", y=0.5, xanchor="right", x=1.1),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#2A3B5C'),
        height=250
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# --- BOTTOM ROW ---
bot_col1, bot_col2, bot_col3, bot_col4 = st.columns([1.2, 1.2, 1, 1.8])

# Bottom Left: Treasury Split Donut
with bot_col1:
    fig_treasury = go.Figure(data=[go.Pie(
        labels=['T-Bills', 'Corporate Bonds', 'Cash & Equivalents', 'Sovereign Bonds', 'REITs/Others'],
        values=[35, 25, 20, 15, 5],
        hole=0.6,
        marker_colors=['#2C6296', '#4B90E2', '#66B3E9', '#50E3C2', '#A3E4D7'],
        textinfo='label+percent', textposition='outside'
    )])
    fig_treasury.update_layout(
        title=dict(text="Treasury Portfolio Split", font=dict(color='white', size=14), x=0.5),
        showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250
    )
    st.plotly_chart(fig_treasury, use_container_width=True)

# Bottom Mid-Left: Expense Breakdown Donut
with bot_col2:
    fig_exp = go.Figure(data=[go.Pie(
        labels=['Salaries', 'R&D', 'Rent', 'Marketing', 'Infrastructure'],
        values=[40, 18, 15, 12, 15],
        hole=0.6,
        marker_colors=['#229954', '#52BE80', '#50E3C2', '#A3E4D7', '#4B90E2'],
        textinfo='label+percent', textposition='outside'
    )])
    fig_exp.update_layout(
        title=dict(text="Expense Breakdown Q2", font=dict(color='white', size=14), x=0.5),
        showlegend=False, margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250
    )
    st.plotly_chart(fig_exp, use_container_width=True)

# Bottom Mid-Right: New Metrics Boxes
with bot_col3:
    st.markdown("""
        <div class='metric-card' style='margin-top:20px; padding: 20px 10px;'>
            <div class='metric-title'>Current Highest Profit Rate</div>
            <div class='metric-value' style='color: #50E3C2; font-size: 24px;'>5.35% p.a.</div>
            <div class='metric-sub'>Bank: Premier Trust Bank<br>Current Month: July 2024</div>
        </div>
        <div class='metric-card' style='padding: 20px 10px;'>
            <div class='metric-title'>MhePR</div>
            <div class='metric-value' style='color: #50E3C2; font-size: 24px;'>4.8%</div>
            <div class='metric-sub'>Next MPR Date: August 14, 2024</div>
        </div>
    """, unsafe_allow_html=True)

# Bottom Right: Bar Chart
with bot_col4:
    fig_bar = go.Figure()
    categories = ['Others', 'Infrastructure', 'Marketing', 'Rent', 'R&D', 'Salaries']
    actual = [7048, 22030, 10488, 11343, 15580, 25580]
    budget = [3253, 17800, 13300, 5820, 9200, 28500]
    
    fig_bar.add_trace(go.Bar(y=categories, x=budget, name='Budget ($)', orientation='h', marker_color='#4B90E2'))
    fig_bar.add_trace(go.Bar(y=categories, x=actual, name='Actual ($)', orientation='h', marker_color='#50E3C2'))
    
    fig_bar.update_layout(
        title=dict(text="Q2 Budget vs. Actual Performance", font=dict(color='white', size=14), x=0.5),
        barmode='group',
        margin=dict(t=30, b=20, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(yanchor="bottom", y=0.3, xanchor="right", x=1.1),
        xaxis=dict(showgrid=True, gridcolor='#2A3B5C'), yaxis=dict(showgrid=False),
        height=250
    )
    st.plotly_chart(fig_bar, use_container_width=True)
