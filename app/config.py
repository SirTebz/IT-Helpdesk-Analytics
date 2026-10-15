from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
DB_PATH = DATA / "helpdesk.db"

def database_url() -> str:
    if os.getenv("DB_DIALECT", "sqlite").lower() == "mssql":
        driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server").replace(" ", "+")
        return f"mssql+pyodbc://{os.getenv('DB_USER','')}:{os.getenv('DB_PASSWORD','')}@{os.getenv('DB_SERVER','localhost')}:{os.getenv('DB_PORT','1433')}/{os.getenv('DB_NAME','HelpdeskAnalytics')}?driver={driver}&TrustServerCertificate=yes"
    return f"sqlite:///{DB_PATH.as_posix()}"
