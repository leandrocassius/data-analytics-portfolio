"""SQLAlchemy models for YouTube Trends pipeline (single source of truth for schema)."""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all models."""

    pass


class Channel(Base):
    """Unique channels from trending videos."""

    __tablename__ = "channels"

    channel_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel_title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    videos: Mapped[list["Video"]] = relationship("Video", back_populates="channel")


class Video(Base):
    """Trending videos with metrics and raw text."""

    __tablename__ = "videos"

    video_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(64), ForeignKey("channels.channel_id"), index=True)
    region_code: Mapped[str] = mapped_column(String(8), index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trending_capture_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    view_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    like_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    comment_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    favorite_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    channel: Mapped["Channel"] = relationship("Channel", back_populates="videos")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="video")
    text_features: Mapped[Optional["TextFeatures"]] = relationship(
        "TextFeatures", back_populates="video", uselist=False
    )


class Comment(Base):
    """Comments sampled from videos."""

    __tablename__ = "comments"

    comment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(String(32), ForeignKey("videos.video_id"), index=True)
    author_channel_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    text_original: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    like_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    video: Mapped["Video"] = relationship("Video", back_populates="comments")


class TextFeatures(Base):
    """Preprocessed text and sentiment features per video."""

    __tablename__ = "text_features"

    video_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("videos.video_id"), primary_key=True
    )
    lemmatized_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment_sentiment_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment_sentiment_std: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment_sentiment_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    video: Mapped["Video"] = relationship("Video", back_populates="text_features")


class LineageEvent(Base):
    """Simple lineage log: job name, source/target tables, run time, row count."""

    __tablename__ = "lineage_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(128), index=True)
    source_table: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    target_table: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="success")
