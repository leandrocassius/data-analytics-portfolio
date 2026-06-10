"""
YouTube Trends pipeline DAG: fetch trending -> load to DB -> fetch comments -> load comments -> build text features.
"""

from pathlib import Path

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

# Default args for the DAG
DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": __import__("datetime").timedelta(minutes=2),
}

RAW_DATA_PATH = Path("/opt/airflow/data/raw")


@dag(
    dag_id="yt_trends_dag",
    default_args=DEFAULT_ARGS,
    schedule="@daily",
    start_date=days_ago(1),
    tags=["youtube", "trends", "portfolio"],
    catchup=False,
)
def yt_trends_pipeline_dag():
    """Orchestrate YouTube trending ingestion and text feature build."""

    @task
    def fetch_trending_raw():
        from yt_trends_pipeline.ingestion.fetch_trending import fetch_and_save_trending
        paths = fetch_and_save_trending(base_path=RAW_DATA_PATH)
        return len(paths)

    @task
    def load_trending_to_db():
        from yt_trends_pipeline.ingestion.load_raw_to_db import run_load_trending
        return run_load_trending(raw_dir=RAW_DATA_PATH)

    @task
    def fetch_comments_raw():
        from yt_trends_pipeline.db.session import get_session
        from yt_trends_pipeline.db.models import Video
        from yt_trends_pipeline.ingestion.fetch_comments import fetch_and_save_comments
        from sqlalchemy import select
        base = Path("/opt/airflow/data/raw")
        base.mkdir(parents=True, exist_ok=True)
        with get_session() as session:
            video_ids = list(session.scalars(select(Video.video_id)).all())
        if not video_ids:
            return 0
        fetch_and_save_comments(video_ids, base_path=base)
        return len(video_ids)

    @task
    def load_comments_to_db():
        from yt_trends_pipeline.ingestion.load_raw_to_db import run_load_comments
        return run_load_comments(raw_dir=RAW_DATA_PATH)

    @task
    def build_text_features():
        from yt_trends_pipeline.processing.build_text_features import run_build_text_features
        return run_build_text_features()

    n_raw = fetch_trending_raw()
    n_videos = load_trending_to_db()
    n_fetch_comments = fetch_comments_raw()
    n_comments = load_comments_to_db()
    n_features = build_text_features()

    n_raw >> n_videos >> n_fetch_comments >> n_comments >> n_features


yt_trends_pipeline_dag()
