import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO

# Load data
EXCEL_PATH = "vdic_dashboard_ready.csv"
df = pd.read_csv(EXCEL_PATH)

# Drop empty titles
df = df.dropna(subset=['Title'])

# Fill missing columns
if 'Strategy ID' not in df.columns:
    df['Strategy ID'] = ['STR{:03}'.format(i+1) for i in range(len(df))]
if 'Start Date' not in df.columns:
    df['Start Date'] = pd.NaT
if 'Target Date' not in df.columns:
    df['Target Date'] = pd.NaT
if 'Progress (%)' not in df.columns:
    df['Progress (%)'] = 0
if 'Term Plan' not in df.columns:
    df['Term Plan'] = 'Short-Term'
if 'Evaluation Status' not in df.columns:
    df['Evaluation Status'] = ''

# Convert dates
df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
df['Target Date'] = pd.to_datetime(df['Target Date'], errors='coerce')

# --- Evaluation Status Mapping ---
def evaluate_status(p):
    if p >= 90:
        return "Target Achieved"
    elif 50 <= p < 90:
        return "Partially Achieved"
    else:
        return "Not Achieved"

df['Evaluation Status'] = df['Progress (%)'].apply(evaluate_status)

# Reorder columns
df = df[['Strategy ID', 'Title', 'Enabler', 'Assigned To', 'Status', 'Term Plan', 'Evaluation Status', 'Start Date', 'Target Date', 'Progress (%)']]

# --- Streamlit UI ---
st.set_page_config(page_title="Maharashtra National Law University", layout="wide")
#st.image("mnlu_logo.png", width=120)
#st.markdown("## Maharashtra National Law University, Mumbai")
# Clean, centered header with logo and title
col_logo, col_title, _ = st.columns([1, 6, 1])
with col_logo:
    st.image("mnlu_logo.png", width=100)
with col_title:
    st.markdown("""
    <h1 style='text-align: center; margin-top: 10px; margin-bottom: 0; font-size: 40px; color: #FFFFFF;'>
        Maharashtra National Law University, Mumbai
    </h1>
    """, unsafe_allow_html=True)


# --- Overview ---
st.header("📌 Overview Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Strategies", len(df))
col2.metric("Completed", df[df['Status'] == 'Completed'].shape[0])
col3.metric("In Progress", df[df['Status'] == 'In Progress'].shape[0])

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")
enabler_filter = st.sidebar.multiselect("Filter by Enabler", options=df['Enabler'].dropna().unique())
status_filter = st.sidebar.multiselect("Filter by Status", options=df['Status'].dropna().unique())
term_filter = st.sidebar.multiselect("Filter by Term Plan", options=df['Term Plan'].dropna().unique())
assigned_filter = st.sidebar.multiselect("Filter by Assigned To", options=df['Assigned To'].dropna().unique())

filtered_df = df.copy()
if enabler_filter:
    filtered_df = filtered_df[filtered_df['Enabler'].isin(enabler_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
if term_filter:
    filtered_df = filtered_df[filtered_df['Term Plan'].isin(term_filter)]
if assigned_filter:
    filtered_df = filtered_df[filtered_df['Assigned To'].isin(assigned_filter)]

# --- Charts ---
st.header("📊 Visual Insights")
col1, col2 = st.columns(2)

with col1:
    status_count = filtered_df['Status'].value_counts().reset_index()
    status_count.columns = ['Status', 'Count']
    status_chart = px.pie(status_count, values='Count', names='Status', title='Strategy Status Distribution',
                          color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(status_chart, use_container_width=True)

with col2:
    enabler_count = filtered_df['Enabler'].value_counts().reset_index()
    enabler_count.columns = ['Enabler', 'Count']
    enabler_chart = px.bar(enabler_count, x='Enabler', y='Count', title='Strategies per Enabler',
                           color='Enabler', color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(enabler_chart, use_container_width=True)

st.subheader("📈 Progress Distribution")
progress_chart = px.histogram(filtered_df, x='Progress (%)', nbins=10, title="Strategy Progress (%) Spread",
                              range_x=[0, 100], color_discrete_sequence=["#3b82f6"])
st.plotly_chart(progress_chart, use_container_width=True)

st.subheader("📊 Term Plan Distribution")
term_count = filtered_df['Term Plan'].value_counts().reset_index()
term_count.columns = ['Term Plan', 'Count']
term_chart = px.bar(term_count, x='Term Plan', y='Count', title='Strategies by Term Plan',
                    color='Term Plan', color_discrete_sequence=px.colors.qualitative.Set3)
st.plotly_chart(term_chart, use_container_width=True)

st.subheader("📊 Evaluation Status")
eval_count = filtered_df['Evaluation Status'].value_counts().reset_index()
eval_count.columns = ['Evaluation Status', 'Count']
eval_chart = px.bar(eval_count, x='Evaluation Status', y='Count', title='Target Achievement Status',
                    color='Evaluation Status', color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(eval_chart, use_container_width=True)

# --- Data Table ---
st.header("📋 Strategy Tracker Table")
st.dataframe(filtered_df, use_container_width=True)

# --- Export to Excel ---
##st.download_button(
##    label="📥 Download Filtered Data as Excel",
##    data=BytesIO(filtered_df.to_excel(index=False, engine='openpyxl')),
##    file_name="VDIC_Strategies_Filtered.xlsx",
##    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
##)

# Export filtered data to Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(filtered_df)

st.download_button(
    label="📥 Download Filtered Data as Excel",
    data=excel_data,
    file_name="VDIC_Strategies_Filtered.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


# --- Progress Bars ---
st.subheader("📍 Individual Strategy Progress")
for _, row in filtered_df.iterrows():
    st.markdown(f"**{row['Title']}** ({row['Term Plan']}) – {row['Evaluation Status']}")
    st.progress(float(row['Progress (%)']) / 100)

# --- Add Strategy Form ---
st.subheader("➕ Add New Strategy")
with st.form("add_form"):
    title = st.text_input("Title")
    enabler = st.selectbox("Enabler", options=sorted(df['Enabler'].dropna().unique()))
    term_plan = st.selectbox("Term Plan", options=['Short-Term', 'Mid-Term', 'Long-Term'])
    assigned_to = st.text_input("Assigned To")
    status = st.selectbox("Status", options=['Not Started', 'In Progress', 'Completed'])
    start_date = st.date_input("Start Date", datetime.now())
    target_date = st.date_input("Target Date", datetime.now())
    progress = st.slider("Progress (%)", 0, 100, 0)
    submit = st.form_submit_button("Add Strategy")

    if submit:
        eval_status = evaluate_status(progress)
        new_row = {
            'Strategy ID': f"STR{len(df)+1:03}",
            'Title': title,
            'Enabler': enabler,
            'Assigned To': assigned_to,
            'Status': status,
            'Term Plan': term_plan,
            'Evaluation Status': eval_status,
            'Start Date': pd.to_datetime(start_date),
            'Target Date': pd.to_datetime(target_date),
            'Progress (%)': progress
        }
        df = df.append(new_row, ignore_index=True)
        df.to_csv(EXCEL_PATH, index=False)
        st.success("✅ Strategy Added! Please refresh to see it updated.")
