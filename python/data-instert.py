import os
import sys
from pathlib import Path
import pandas as pd  # type:ignore
from tqdm import tqdm  # type:ignore

# Automatic root folder dhoondh kar sys.path mein jodna
current_dir = Path(__file__).resolve()
for parent in [current_dir] + list(current_dir.parents):
    if parent.name == "RFM-Churn-Engine":
        sys.path.append(str(parent))
        break

# Config se engine import karo
# # fmt: off
from config.sql_connect import engine # type:ignore
# # fmt: on

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
TABLE_NAME = "sales_data"
CHUNK_SIZE = 50000

print(f"🚀 Starting Data Ingestion into '{TABLE_NAME}' table...")


def InsertData():
    df = pd.read_csv(CSV_FILE_PATH)

    if df.empty:
        print(f"⚠️ CSV file is empty: {CSV_FILE_PATH}")
        return

    df.to_sql(
        TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=CHUNK_SIZE,
    )

    print(
        f"✅ Data inserted successfully into '{TABLE_NAME}' from '{CSV_FILE_PATH}'")


def showtable():
    query = """
    SELECT * FROM sales_data LIMIT 10;
    """
    print(pd.read_sql(query, con=engine))


if __name__ == "__main__":
    InsertData()
    showtable()
