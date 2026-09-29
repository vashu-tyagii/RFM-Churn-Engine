import streamlit as st
import pandas as pd
import plotly.express as px  # type: ignore

# Tera custom engine import
from config.sql_connect import engine # type:ignore

st.set_page_config(page_title="RFM & Cohort Analytics", layout="wide")
st.title("📊 Customer RFM & Cohort Analytics Dashboard")

@st.cache_data(ttl=600)
def fetch_data(query):  # type: ignore
    with engine.connect() as conn:
        return pd.read_sql(query, conn) # type: ignore

try:
    # 1. Fetch Datasets
    df_rfm = fetch_data("SELECT * FROM vw_rfm_final_segments;")
    df_cohort = fetch_data("""
        SELECT 
            cohort_month,
            MAX(CASE WHEN cohort_index = 0 THEN active_customers END) AS Month_0,
            MAX(CASE WHEN cohort_index = 1 THEN active_customers END) AS Month_1,
            MAX(CASE WHEN cohort_index = 2 THEN active_customers END) AS Month_2,
            MAX(CASE WHEN cohort_index = 3 THEN active_customers END) AS Month_3,
            MAX(CASE WHEN cohort_index = 4 THEN active_customers END) AS Month_4,
            MAX(CASE WHEN cohort_index = 5 THEN active_customers END) AS Month_5
        FROM vw_cohort_retention
        GROUP BY cohort_month
        ORDER BY cohort_month;
    """)

    # 2. Executive Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Unique Customers", f"{df_rfm['CustomerID'].nunique():,}")
    col2.metric("Average Spending ($)", f"{df_rfm['Monetary'].mean():,.2f}")
    col3.metric("Average Frequency", f"{df_rfm['Frequency'].mean():.1f}")

    st.markdown("---")

    # 3. RFM Segments Plot
    st.subheader("📌 Customer RFM Segments")
    segment_counts = df_rfm['Customer_Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    fig_seg = px.bar( # type: ignore
        segment_counts, 
        x='Count', 
        y='Segment', 
        orientation='h', 
        color='Segment',
        text='Count'
    )
    st.plotly_chart(fig_seg, use_container_width=True) # type: ignore

    # 4. Cohort Retention Heatmap
    st.subheader("🗓️ Cohort Retention Matrix Count")
    cohort_matrix = df_cohort.set_index('cohort_month')
    
    fig_heat = px.imshow( # type: ignore
        cohort_matrix,
        text_auto=True,
        color_continuous_scale="Viridis",
        aspect="auto"
    )
    st.plotly_chart(fig_heat, use_container_width=True) # type: ignore

except Exception as e:
    st.error(f"Error fetching data: {e}")