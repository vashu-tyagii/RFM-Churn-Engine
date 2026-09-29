import sys
import sqlite3
from pathlib import Path
import pandas as pd  # type:ignore

# 1. Project Root Directory Setup
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

CSV_FILE_PATH = ROOT_DIR / "data" / "dataset.csv"
DB_FILE_PATH = ROOT_DIR / "data" / "rfm_database.db"
TABLE_NAME = "sales_data"

print(f"🚀 Starting Persistent Direct Ingestion into SQLite...")

def InsertData():
    if not CSV_FILE_PATH.exists():
        print(f"❌ Error: CSV File not found at {CSV_FILE_PATH}")
        return

    print("📖 Reading CSV dataset...")
    df = pd.read_csv(CSV_FILE_PATH)

    if df.empty:
        print("⚠️ Warning: CSV file is empty!")
        return

    print(f"📊 Total rows loaded from CSV: {len(df):,}")

    # Ensure data directory exists
    DB_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Direct SQLite Persistent Connection
    conn = sqlite3.connect(DB_FILE_PATH)
    try:
        df.to_sql(TABLE_NAME, con=conn, if_exists="replace", index=False)
        conn.commit()  # Direct Permanent Storage
        print(f"✅ Successfully persisted {len(df):,} rows into '{DB_FILE_PATH.name}'!")
    except Exception as e:
        print(f"❌ Ingestion Error: {e}")
    finally:
        conn.close()

def VerifyData():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"🔍 Hard Verified DB Count: {count:,} rows")

if __name__ == "__main__":
    InsertData()
    VerifyData()