import streamlit as st
import pandas as pd

# Set page layout to wide for a better dashboard view
st.set_page_config(page_title="Treasury Dashboard", layout="wide")
st.title("Treasury & Income Dashboard")

# --- OPTION A: LOAD THE EXCEL FILE ---
# IMPORTANT: Change 'my_data.xlsx' to the EXACT name of your uploaded Excel file!
FILE_NAME = "my_data.xlsx"

try:
    # Read the excel file
    df = pd.read_excel(FILE_NAME)

    # --- OPTION B: INTERACTIVE FILTERS ---
    st.sidebar.header("Filter Your Data")
    
    # ⚠️ IMPORTANT: Change 'Category' to a real column name from your Excel file (e.g., 'Department' or 'Type')
    filter_column = 'Category' 
    
    # Create a multiselect dropdown in the sidebar
    unique_values = df[filter_column].unique()
    selected_values = st.sidebar.multiselect("Select Categories:", unique_values, default=unique_values)
    
    # Filter the data based on user selection
    filtered_df = df[df[filter_column].isin(selected_values)]

    # --- OPTION C: KPI METRICS ---
    st.subheader("Summary Metrics")
    
    # ⚠️ IMPORTANT: Change 'Income' and 'Expenses' to the actual column names holding your numbers!
    total_income = filtered_df['Income'].sum()
    total_expenses = filtered_df['Expenses'].sum()
    net_profit = total_income - total_expenses

    # Create 3 columns for the metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Income", value=f"${total_income:,.2f}")
    col2.metric(label="Total Expenses", value=f"${total_expenses:,.2f}")
    col3.metric(label="Net Profit", value=f"${net_profit:,.2f}")
    
    st.divider() # Adds a visual line break

    # --- DISPLAY CHART & DATA ---
    st.subheader("Data Chart")
    # ⚠️ IMPORTANT: Change 'Date' to your date/time column name
    st.line_chart(filtered_df, x='Date', y=['Income', 'Expenses'])
    
    st.subheader("Raw Data Table")
    st.dataframe(filtered_df) # Shows the filtered Excel data table

# Error handling to help you if column names don't match
except FileNotFoundError:
    st.error(f"⚠️ I cannot find a file named '{FILE_NAME}'. Please check the file name at the top of the code.")
except KeyError as e:
    st.error(f"⚠️ Column Name Error: Your Excel file doesn't have a column named {e}. Please look at the code lines marked with '⚠️ IMPORTANT' and change the names to match your Excel columns exactly (including capital letters)!")
