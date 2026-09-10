import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set dark theme and wide layout
st.set_page_config(page_title="Financial Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Title
st.title("🏦 Treasury Financial Dashboard")
st.markdown("---")

# Create the top row with 3 main columns (mimicking the image layout)
# The ratios [1, 1.2, 1.5] dictate how wide each column is
top_col1, top_col2, top_col3 = st.columns([1, 1.2, 1.5])

with top_col1:
    # 4 Metrics stacked in a grid-like fashion using nested columns
    st.subheader("Key Metrics")
    m1, m2 = st.columns(2)
    m1.metric(label="Total Income", value="$250,000")
    m2.metric(label="Total Treasury Pool", value="$180,000") # Changed from Expenses
    
    st.write("") # Spacing
    
    m3, m4 = st.columns(2)
    # NOTE: Change "Net Profit" below to whatever you meant to type!
    m3.metric(label="Net Profit", value="$70,000") 
    m4.metric(label="Expense Ratio", value="72.0%")

with top_col2:
    st.subheader("Income by Product")
    # New Pie Chart: Savings, T-Bills, Buy/Sell, TDR
    pie_data = pd.DataFrame({
        'Product': ['Savings Account', 'T-Bills', 'Buy/Sell', 'TDR'],
        'Value': [85000, 90000, 45000, 30000]
    })
    
    # Create a donut chart using Plotly
    fig_pie = px.pie(
        pie_data, 
        names='Product', 
        values='Value', 
        hole=0.6, # Makes it a donut chart
        color_discrete_sequence=['#4B90E2', '#50E3C2', '#F5A623', '#B8E986']
    )
    fig_pie.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with top_col3:
    st.subheader("Quarterly Profit Trend (Q1 - Q4)")
    # New Line Chart: Q1, Q2, Q3, Q4
    trend_data = pd.DataFrame({
        'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
        'Profit Earned': [45000, 55000, 70000, 85000]
    })
    
    fig_line = px.line(
        trend_data, 
        x='Quarter', 
        y='Profit Earned',
        markers=True,
        line_shape='spline' # Makes the line curved and smooth
    )
    fig_line.update_traces(line_color='#50E3C2', marker=dict(size=8))
    fig_line.update_layout(
        margin=dict(t=20, b=20, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="",
        yaxis_title="Profit ($)"
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# Create the bottom row (keeping the rest the same as requested)
bottom_col1, bottom_col2, bottom_col3 = st.columns([1, 1, 2])

with bottom_col1:
    st.subheader("Current Ratio")
    st.markdown("<h2 style='text-align: center; color: #50E3C2;'>2.1</h2>", unsafe_allow_html=True)
    st.caption("Indicates Excellent Liquidity Position")

with bottom_col2:
    st.subheader("Debt-to-Equity")
    st.markdown("<h2 style='text-align: center; color: #50E3C2;'>0.8</h2>", unsafe_allow_html=True)
    st.caption("Conservative Leverage - Minimal Risk")

with bottom_col3:
    st.subheader("Budget vs. Actual")
    # Simple horizontal bar chart dummy data
    bar_data = pd.DataFrame({
        'Category': ['Salaries', 'R&D', 'Rent', 'Marketing'],
        'Budget': [28500, 9200, 5820, 13300],
        'Actual': [25380, 18580, 11343, 10488]
    })
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(y=bar_data['Category'], x=bar_data['Budget'], name='Budget', orientation='h', marker_color='#4B90E2'))
    fig_bar.add_trace(go.Bar(y=bar_data['Category'], x=bar_data['Actual'], name='Actual', orientation='h', marker_color='#50E3C2'))
    
    fig_bar.update_layout(
        barmode='group',
        margin=dict(t=0, b=0, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(yanchor="bottom", y=1.02, xanchor="right", x=1, orientation="h")
    )
    st.plotly_chart(fig_bar, use_container_width=True)
