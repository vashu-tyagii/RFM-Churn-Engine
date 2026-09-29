import pandas as pd
from sqlalchemy import text
from config.sql_connect import engine

with engine.connect() as conn:
    print("--- 1. Raw sales_data Count ---")
    raw_count = conn.execute(text("SELECT COUNT(*) FROM sales_data;")).fetchone()[0]
    print(f"Raw Sales Data Rows: {raw_count}")

    print("\n--- 2. Sample Data from sales_data ---")
    df_sample = pd.read_sql("SELECT * FROM sales_data LIMIT 3;", conn)
    print("Columns in DB:", df_sample.columns.tolist())
    print(df_sample)

    print("\n--- 3. Cleaned View Count ---")
    try:
        clean_count = conn.execute(text("SELECT COUNT(*) FROM vw_cleaned_sales;")).fetchone()[0]
        print(f"Cleaned Sales View Rows: {clean_count}")
    except Exception as e:
        print(f"Error reading vw_cleaned_sales: {e}")

    print("\n--- 4. RFM Final Segments Count ---")
    try:
        rfm_count = conn.execute(text("SELECT COUNT(*) FROM vw_rfm_final_segments;")).fetchone()[0]
        print(f"RFM Final Segments Rows: {rfm_count}")
    except Exception as e:
        print(f"Error reading vw_rfm_final_segments: {e}")