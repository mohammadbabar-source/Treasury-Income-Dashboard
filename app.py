import streamlit as st
import pandas as pd

# Set up the page layout
st.set_page_config(page_title="Treasury Dashboard", layout="wide")
st.title("🏦 Treasury Income Dashboard")
st.markdown("Visualizing bank profits and account performance from July '25 to June '26.")

FILE_NAME = "Treasury Income July  25 - June 26.xlsx"

try:
    # 1. Load the specific sheet that contains the mapped data
    # We use header=1 because your actual column names (Bank Name, Total) start on the second row
    df = pd.read_excel(FILE_NAME, sheet_name='Treasury Bank Profits mapped ', header=1)
    
    # Clean the data: Drop completely empty rows and columns
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    
    # Make sure the 'Total' column is treated as numbers, so we can do math on it
    # We force errors to 'coerce' (turn into 0) in case there is text like "Closed" in the total column
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
    
    # Filter out rows where there is no Bank Name (removes total/summary rows from the bottom of excel)
    df = df[df['Bank Name'].notna()]

    # --- DASHBOARD METRICS (KPIs) ---
    st.subheader("📊 Executive Summary")
    
    # Calculate totals
    total_income = df['Total'].sum()
    total_accounts = len(df['Account Title'].unique())
    top_bank = df.groupby('Bank Name')['Total'].sum().idxmax()

    # Display metrics in 3 columns
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Treasury Income", value=f"PKR {total_income:,.0f}")
    col2.metric(label="Total Bank Accounts", value=f"{total_accounts}")
    col3.metric(label="Highest Yielding Bank", value=f"{top_bank}")
    
    st.divider()

    # --- DASHBOARD CHARTS ---
    st.subheader("📈 Income Breakdown")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**Total Income by Bank**")
        # Group the data by Bank Name and sum the totals
        bank_totals = df.groupby('Bank Name')['Total'].sum().sort_values(ascending=False)
        # Display a bar chart
        st.bar_chart(bank_totals)
        
    with chart_col2:
        st.markdown("**Income by Account Title (Top 5)**")
        # Group by Account title, sort highest to lowest, take top 5
        account_totals = df.groupby('Account Title')['Total'].sum().sort_values(ascending=False).head(5)
        # Display a bar chart
        st.bar_chart(account_totals)

    st.divider()

    # --- RAW DATA TABLE ---
    # Hide the data inside an expander so it doesn't clutter the screen
    with st.expander("🔍 View Raw Data Table (Click to expand)"):
        # We drop the confusing unnamed/calculation columns at the far right for a cleaner view
        clean_table = df.drop(columns=[col for col in df.columns if 'Unnamed' in str(col) or 'GL BAL' in str(col)])
        st.dataframe(clean_table, use_container_width=True)

except FileNotFoundError:
    st.error(f"⚠️ I cannot find '{FILE_NAME}'. Please check the file name.")
except Exception as e:
    st.error(f"⚠️ An error occurred: {e}")
