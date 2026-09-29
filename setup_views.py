from pathlib import Path
from sqlalchemy import text
from config.sql_connect import engine

BASE_DIR = Path(__file__).resolve().parent
SQL_FILE_PATH = BASE_DIR / "sql" / "views.sql"


def create_views():
    if not SQL_FILE_PATH.exists():
        print(f"❌ SQL File not found at {SQL_FILE_PATH}")
        return

    print("⏳ Executing SQLite Views setup...")

    with open(SQL_FILE_PATH, "r") as file:
        sql_script = file.read()

    statements = sql_script.split(";")

    with engine.begin() as conn:
        for statement in statements:
            if statement.strip():
                conn.execute(text(statement))

    print("✅ All SQLite Views created successfully!")


if __name__ == "__main__":
    create_views()
