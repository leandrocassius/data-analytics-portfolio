"""Build text_features table from videos and comments (lemmatized text + sentiment)."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import Comment, TextFeatures, Video
from ..db.session import get_session
from ..db.lineage import log_lineage
from .lemmatization import lemmatize_joined
from .sentiment import aggregate_sentiment, score_text


def build_text_features_for_videos(session: Session) -> int:
    """
    For each video, compute lemmatized title+description and comment sentiment aggregates;
    upsert into text_features. Returns number of rows written.
    """
    videos = session.scalars(select(Video)).all()
    count = 0
    for video in videos:
        title = video.title or ""
        desc = video.description or ""
        lemmatized = lemmatize_joined(title, desc)
        title_len = len((video.title or "").split())
        desc_len = len((video.description or "").split())

        comment_rows = session.scalars(
            select(Comment.text_original).where(Comment.video_id == video.video_id)
        ).all()
        comment_texts: List[Optional[str]] = [c for c in comment_rows if c]
        scores = [score_text(t) for t in comment_texts]
        avg_sent, std_sent, n_sent = aggregate_sentiment(scores)

        row = TextFeatures(
            video_id=video.video_id,
            lemmatized_text=lemmatized or None,
            title_length=title_len if title_len else None,
            description_length=desc_len if desc_len else None,
            comment_sentiment_avg=avg_sent if n_sent else None,
            comment_sentiment_std=std_sent if n_sent else None,
            comment_sentiment_count=n_sent if n_sent else None,
        )
        session.merge(row)
        count += 1
    session.flush()
    log_lineage(
        session,
        "build_text_features",
        source_table="videos,comments",
        target_table="text_features",
        row_count=count,
    )
    return count


def run_build_text_features(database_url: Optional[str] = None) -> int:
    """
    Run the text features job and return number of videos processed.
    Caller may log lineage after this.
    """
    with get_session(database_url) as session:
        return build_text_features_for_videos(session)
