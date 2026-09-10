import streamlit as st
import pandas as pd

st.set_page_config(page_title="Treasury Dashboard", layout="wide")
st.title("🏦 Treasury Income Dashboard")
st.markdown("Visualizing bank profits and account performance from July '25 to June '26.")

FILE_NAME = "Treasury Income July  25 - June 26.xlsx"

try:
    df = pd.read_excel(FILE_NAME, sheet_name='Treasury Bank Profits mapped ', header=1)
    
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
    df = df[df['Bank Name'].notna()]

    # 🛠️ THE FIX: Force these columns to be text so dates/numbers don't crash the charts
    df['Bank Name'] = df['Bank Name'].astype(str)
    df['Account Title'] = df['Account Title'].astype(str)
    
    # 🛠️ EXTRA CLEANUP: Remove any row where the Bank Name is literally just the word "Bank Name"
    df = df[df['Bank Name'] != 'Bank Name']

    # --- DASHBOARD METRICS (KPIs) ---
    st.subheader("📊 Executive Summary")
    
    total_income = df['Total'].sum()
    total_accounts = len(df['Account Title'].unique())
    top_bank = df.groupby('Bank Name')['Total'].sum().idxmax()

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
        bank_totals = df.groupby('Bank Name')['Total'].sum().sort_values(ascending=False)
        st.bar_chart(bank_totals)
        
    with chart_col2:
        st.markdown("**Income by Account Title (Top 5)**")
        account_totals = df.groupby('Account Title')['Total'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(account_totals)

    st.divider()

    with st.expander("🔍 View Raw Data Table (Click to expand)"):
        clean_table = df.drop(columns=[col for col in df.columns if 'Unnamed' in str(col) or 'GL BAL' in str(col)])
        st.dataframe(clean_table, use_container_width=True)

except FileNotFoundError:
    st.error(f"⚠️ I cannot find '{FILE_NAME}'. Please check the file name.")
except Exception as e:
    st.error(f"⚠️ An error occurred: {e}")
