import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine

# .env file bilkul sql_connect.py ke sath hi config/ folder mein hai
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

# Credentials fetch karna
user = os.getenv("MYSQL_USER")
raw_password = os.getenv("MYSQL_PASSWORD")
password = quote_plus(raw_password) if raw_password else ""
host = os.getenv("MYSQL_HOST")
port = int(os.getenv("MYSQL_PORT", 3306))
database = os.getenv("MYSQL_DB")

# SQLAlchemy Engine setup
db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_url)
