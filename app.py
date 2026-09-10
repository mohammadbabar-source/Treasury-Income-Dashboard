import streamlit as st
import pandas as pd

st.set_page_config(page_title="Treasury Dashboard", layout="wide")
st.title("Treasury & Income Dashboard")

# The exact name of your uploaded file
FILE_NAME = "Treasury Income July  25 - June 26.xlsx"

try:
    # 1. Read all the sheet names from your Excel file
    xls = pd.ExcelFile(FILE_NAME)
    sheet_names = xls.sheet_names
    
    # 2. Create a dropdown in the sidebar so you can choose which sheet to view
    st.sidebar.header("Navigation")
    selected_sheet = st.sidebar.selectbox("Select a Sheet to View:", sheet_names)
    
    # 3. Load the specific sheet the user selected
    # We skip the first row (header=1) on some sheets if they have merged headers
    if "Dashboard" in selected_sheet or "mapped" in selected_sheet.lower():
        df = pd.read_excel(FILE_NAME, sheet_name=selected_sheet, header=1)
    else:
        df = pd.read_excel(FILE_NAME, sheet_name=selected_sheet)
    
    # Clean up the data: Remove completely empty columns and rows
    df = df.dropna(how='all', axis=1)
    df = df.dropna(how='all', axis=0)
    
    st.subheader(f"Data View: {selected_sheet}")
    
    # Display the cleaned data table
    st.dataframe(df, use_container_width=True)
    
    st.info("💡 **Tip:** To create line charts or calculate total profits, the best practice is to have a 'Flat Table' in Excel (one column for Date, one for Category, one for Amount) without merged cells at the top.")

except FileNotFoundError:
    st.error(f"⚠️ I cannot find '{FILE_NAME}'. Please ensure the file is uploaded to GitHub with this exact name!")
except Exception as e:
    st.error(f"⚠️ An error occurred while reading the file: {e}")
