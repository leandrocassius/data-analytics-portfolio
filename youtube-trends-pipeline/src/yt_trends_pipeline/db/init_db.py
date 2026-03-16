"""Create database tables from SQLAlchemy models. Run as: python -m yt_trends_pipeline.db.init_db."""

from .session import create_all_tables

if __name__ == "__main__":
    create_all_tables()
    print("Tables created successfully.")
