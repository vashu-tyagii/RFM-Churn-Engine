import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from config.sql_connect import engine

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Customer RFM & Cohort Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS ---
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- DATA LOADING WITH CACHING ---
@st.cache_data(ttl=600)
def load_rfm_data():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM vw_rfm_final_segments;", conn)
    return df


@st.cache_data(ttl=600)
def load_cohort_data():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM vw_cohort_retention;", conn)
    return df


try:
    df_rfm = load_rfm_data()
    df_cohort = load_cohort_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.title("🔍 Interactive Filters")

    # Segment Filter
    all_segments = sorted(df_rfm["Customer_Segment"].unique().tolist())
    selected_segments = st.sidebar.multiselect(
        "Select Customer Segments:",
        options=all_segments,
        default=all_segments,
    )

    # Filter RFM DataFrame
    filtered_rfm = df_rfm[df_rfm["Customer_Segment"].isin(selected_segments)]

    # --- HEADER ---
    st.title("📊 Customer RFM & Cohort Analytics Dashboard")
    st.caption(
        "SQLite-backed Portable Analytics Engine | Deployment Ready for Streamlit Cloud"
    )

    # --- KPI METRICS ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    total_cust = len(filtered_rfm)
    avg_rev = filtered_rfm["Monetary"].mean() if total_cust > 0 else 0
    avg_freq = filtered_rfm["Frequency"].mean() if total_cust > 0 else 0
    avg_rec = filtered_rfm["Recency"].mean() if total_cust > 0 else 0

    kpi1.metric("Total Customers", f"{total_cust:,}")
    kpi2.metric("Avg Revenue per Customer", f"${avg_rev:,.2f}")
    kpi3.metric("Avg Orders (Frequency)", f"{avg_freq:.1f}")
    kpi4.metric("Avg Recency", f"{avg_rec:.0f} Days")

    st.markdown("---")

    # --- NAVIGATION TABS ---
    tab1, tab2, tab3 = st.tabs(
        [
            "📌 RFM Segmentation",
            "🗓️ Cohort Retention Heatmap",
            "🔍 Segment Deep-Dive",
        ]
    )

    # TAB 1: RFM SEGMENTATION
    with tab1:
        st.subheader("Customer Distribution & Revenue Share by Segment")

        col1, col2 = st.columns(2)

        with col1:
            seg_counts = (
                filtered_rfm["Customer_Segment"]
                .value_counts()
                .reset_index()
            )
            seg_counts.columns = ["Segment", "Customer Count"]

            fig_bar = px.bar(
                seg_counts,
                x="Customer Count",
                y="Segment",
                orientation="h",
                color="Segment",
                text="Customer Count",
                title="Customer Count per Segment",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_bar.update_layout(
                showlegend=False,
                height=400,
                yaxis={"categoryorder": "total ascending"},
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            seg_rev = (
                filtered_rfm.groupby("Customer_Segment")["Monetary"]
                .sum()
                .reset_index()
            )
            fig_pie = px.pie(
                seg_rev,
                names="Customer_Segment",
                values="Monetary",
                title="Revenue Contribution by Segment",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Recency vs Monetary Scatter Plot
        st.subheader("Recency vs. Monetary Distribution")
        fig_scatter = px.scatter(
            filtered_rfm,
            x="Recency",
            y="Monetary",
            size="Frequency",
            color="Customer_Segment",
            hover_name="CustomerID",
            log_y=True,
            title="Customer Recency vs Monetary (Bubble Size = Order Frequency)",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # TAB 2: COHORT RETENTION HEATMAP
    with tab2:
        st.subheader("Monthly Cohort Retention Rate Matrix")

        if not df_cohort.empty:
            # Pivot Cohort Data
            cohort_pivot = df_cohort.pivot(
                index="cohort_month",
                columns="cohort_index",
                values="active_customers",
            )

            # Retention Rate Percentage Matrix
            cohort_size = cohort_pivot.iloc[:, 0]
            retention_matrix = cohort_pivot.divide(cohort_size, axis=0) * 100

            fig_heatmap = px.imshow(
                retention_matrix,
                labels=dict(
                    x="Cohort Index (Months)",
                    y="Cohort Month",
                    color="Retention %",
                ),
                x=[f"Month {col}" for col in retention_matrix.columns],
                text_auto=".1f",
                color_continuous_scale="Blues",
                aspect="auto",
            )
            fig_heatmap.update_layout(height=500)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("No Cohort Data available.")

    # TAB 3: CUSTOMER SEARCH & DATA TABLE
    with tab3:
        st.subheader("Customer Level Data Deep-Dive")

        search_id = st.text_input("🔍 Search Customer ID:")
        if search_id:
            display_df = filtered_rfm[
                filtered_rfm["CustomerID"]
                .astype(str)
                .str.contains(search_id)
            ]
        else:
            display_df = filtered_rfm

        st.dataframe(display_df, use_container_width=True, height=400)

        # Download CSV Option
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="rfm_customer_segments.csv",
            mime="text/csv",
        )

except Exception as e:
    st.error(f"❌ Dashboard Loading Error: {e}")
    st.warning("Ensure `python setup_views.py` has been executed successfully.")
