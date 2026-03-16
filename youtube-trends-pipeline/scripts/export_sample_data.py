"""
Export pipeline tables to CSV under data/example/ for use without a database
(e.g. exploratory notebook, or sharing sample data in the repo).

Run from project root:
  python scripts/export_sample_data.py
  or: python -m scripts.export_sample_data   (with project root on PYTHONPATH)
"""

import sys
from pathlib import Path

# Allow importing the package when run as script
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv(project_root / ".env")
OUTPUT_DIR = project_root / "data" / "example"
TABLES = ["channels", "videos", "comments", "text_features", "lineage_events"]


def main() -> None:
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://yt_trends:yt_trends@localhost:5432/yt_trends",
    )
    if not db_url.startswith("postgresql+"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    engine = create_engine(db_url)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for table in TABLES:
        df = pd.read_sql(text(f'SELECT * FROM "{table}"'), con=engine)
        path = OUTPUT_DIR / f"{table}.csv"
        df.to_csv(path, index=False, encoding="utf-8")
        print(f"Wrote {path} ({len(df)} rows)")
    print(f"Done. Sample data is in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
