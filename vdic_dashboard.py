import streamlit as st
import pandas as pd
from datetime import datetime

# Path to your original Excel file
EXCEL_PATH = "vdic_dashboard_ready.csv"


# Load the Excel file
df = pd.read_csv(EXCEL_PATH)


# Fill down (handle merged-cell-like rows)
#df[['Assignee Member', 'Designation', 'Vision Name']] = df[['Assignee Member', 'Designation', 'Vision Name']].ffill()

# Drop rows where Work Assigned is blank (those aren't real tasks)
df = df.dropna(subset=['Title'])


# Rename and map columns to what the dashboard expects
df.rename(columns={
    'Work Assigned': 'Title',
    'Vision Name': 'Enabler',
    'Assignee Member': 'Assigned To',
    'Completion Status': 'Status'
}, inplace=True)

# Add missing fields
if 'Strategy ID' not in df.columns:
    df['Strategy ID'] = ['STR{:03}'.format(i+1) for i in range(len(df))]
if 'Start Date' not in df.columns:
    df['Start Date'] = pd.NaT
if 'Target Date' not in df.columns:
    df['Target Date'] = pd.NaT
if 'Progress (%)' not in df.columns:
    df['Progress (%)'] = 0

# Ensure correct data types
df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
df['Target Date'] = pd.to_datetime(df['Target Date'], errors='coerce')

# Reorder columns to match expected format
df = df[['Strategy ID', 'Title', 'Enabler', 'Assigned To', 'Status', 'Start Date', 'Target Date', 'Progress (%)']]

# Streamlit UI
#st.set_page_config(page_title="VDIC Dashboard", layout="wide")
#st.title("📊 Vision Document Implementation Dashboard")
st.image("mnlu_logo.png", width=150)

st.markdown("### Maharashtra National Law University Mumbai")


# Overview Section
st.header("Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Strategies", len(df))
col2.metric("Completed", df[df['Status'] == 'Completed'].shape[0])
col3.metric("In Progress", df[df['Status'] == 'In Progress'].shape[0])

# Filters
st.sidebar.header("🔍 Filters")
enabler_filter = st.sidebar.multiselect("Filter by Enabler", options=df['Enabler'].dropna().unique())
status_filter = st.sidebar.multiselect("Filter by Status", options=df['Status'].dropna().unique())

filtered_df = df.copy()
if enabler_filter:
    filtered_df = filtered_df[filtered_df['Enabler'].isin(enabler_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]

# Strategy Table
st.subheader("📌 Strategy Tracker")
st.dataframe(filtered_df, use_container_width=True)

# Progress Bars
st.subheader("📈 Progress Overview")
for _, row in filtered_df.iterrows():
    st.markdown(f"**{row['Title']}**")
    try:
        st.progress(float(row['Progress (%)']) / 100)
    except:
        st.warning("⚠️ Invalid progress value")

# Add Strategy Form
with st.expander("➕ Add New Strategy"):
    with st.form("add_form"):
        title = st.text_input("Title")
        enabler = st.selectbox("Enabler", options=sorted(df['Enabler'].dropna().unique()))
        assigned_to = st.text_input("Assigned To")
        status = st.selectbox("Status", options=['Not Started', 'In Progress', 'Completed'])
        start_date = st.date_input("Start Date", datetime.now())
        target_date = st.date_input("Target Date", datetime.now())
        progress = st.slider("Progress (%)", 0, 100, 0)
        submit = st.form_submit_button("Add Strategy")

        if submit:
            new_row = {
                'Strategy ID': f"STR{len(df)+1:03}",
                'Title': title,
                'Enabler': enabler,
                'Assigned To': assigned_to,
                'Status': status,
                'Start Date': pd.to_datetime(start_date),
                'Target Date': pd.to_datetime(target_date),
                'Progress (%)': progress
            }
            df = df.append(new_row, ignore_index=True)
            df.to_excel(EXCEL_PATH, index=False)
            st.success("✅ Strategy Added! Please reload to see the changes.")
