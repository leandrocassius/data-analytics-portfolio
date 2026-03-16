"""Load raw JSON (bronze) into PostgreSQL (silver): videos, channels, comments."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from ..db.models import Channel, Comment, Video
from ..db.session import get_session
from ..db.lineage import log_lineage
from .youtube_client import YouTubeClient


def _parse_iso_datetime(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _video_resource_to_row(item: Dict[str, Any], region_code: str, capture_time: datetime) -> Dict[str, Any]:
    """Map one videos.list item to a Video row dict."""
    sid = item.get("id") or ""
    snippet = item.get("snippet") or {}
    stats = item.get("statistics") or {}
    return {
        "video_id": sid,
        "channel_id": snippet.get("channelId") or "",
        "region_code": region_code,
        "published_at": _parse_iso_datetime(snippet.get("publishedAt")),
        "trending_capture_time": capture_time,
        "title": (snippet.get("title") or "")[:512],
        "description": snippet.get("description"),
        "view_count": _int_or_none(stats.get("viewCount")),
        "like_count": _int_or_none(stats.get("likeCount")),
        "comment_count": _int_or_none(stats.get("commentCount")),
        "favorite_count": _int_or_none(stats.get("favoriteCount")),
    }


def _channel_resource_to_row(item: Dict[str, Any]) -> Dict[str, Any]:
    """Map one channels.list item to a Channel row dict."""
    cid = item.get("id") or ""
    snippet = item.get("snippet") or {}
    return {
        "channel_id": cid,
        "channel_title": (snippet.get("title") or "")[:512],
        "description": snippet.get("description"),
        "published_at": _parse_iso_datetime(snippet.get("publishedAt")),
        "country": (snippet.get("country") or "")[:8] or None,
    }


def _comment_thread_to_row(thread: Dict[str, Any], video_id: str) -> Optional[Dict[str, Any]]:
    """Map one commentThread item to a Comment row dict."""
    cid = thread.get("id")
    if not cid:
        return None
    snippet = thread.get("snippet", {}) or {}
    top = snippet.get("topLevelComment", {}) or {}
    top_snippet = top.get("snippet", {}) or {}
    author = top_snippet.get("authorChannelId", {}) or {}
    author_channel_id = author.get("value") if isinstance(author, dict) else None
    return {
        "comment_id": cid,
        "video_id": video_id,
        "author_channel_id": author_channel_id,
        "text_original": top_snippet.get("textDisplay") or top_snippet.get("textOriginal"),
        "like_count": _int_or_none(top_snippet.get("likeCount")),
        "published_at": _parse_iso_datetime(top_snippet.get("publishedAt")),
    }


def _int_or_none(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def load_trending_files_into_db(
    trending_paths: List[Path],
    session: Session,
    api_key: str,
) -> int:
    """
    Read trending JSON files, fetch channel details via API, upsert channels and videos.
    Returns total number of video rows inserted/updated.
    """
    all_video_rows: List[Dict[str, Any]] = []
    all_channel_ids: set = set()

    for path in trending_paths:
        path = Path(path)
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        region = payload.get("region", "US")
        captured = payload.get("captured_at")
        try:
            capture_dt = datetime.strptime(captured, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc) if captured else datetime.now(timezone.utc)
        except (ValueError, TypeError):
            capture_dt = datetime.now(timezone.utc)
        items = payload.get("videos") or []
        for item in items:
            row = _video_resource_to_row(item, region, capture_dt)
            if row["video_id"] and row["channel_id"]:
                all_video_rows.append(row)
                all_channel_ids.add(row["channel_id"])

    if not all_channel_ids:
        return 0

    client = YouTubeClient(api_key=api_key)
    channel_details = client.get_channel_details(list(all_channel_ids))
    channel_rows = [_channel_resource_to_row(c) for c in channel_details]
    inserted_channel_ids = {row["channel_id"] for row in channel_rows}
    missing_channel_ids = all_channel_ids - inserted_channel_ids

    for row in channel_rows:
        stmt = pg_insert(Channel).values(**row)
        stmt = stmt.on_conflict_do_update(
            index_elements=["channel_id"],
            set_={
                "channel_title": stmt.excluded.channel_title,
                "description": stmt.excluded.description,
                "published_at": stmt.excluded.published_at,
                "country": stmt.excluded.country,
            },
        )
        session.execute(stmt)

    for cid in missing_channel_ids:
        # Some channels may not be returned by the API (e.g. terminated, restricted).
        # Insert minimal stub rows so videos can still reference them.
        stmt = pg_insert(Channel).values(channel_id=cid).on_conflict_do_nothing(
            index_elements=["channel_id"]
        )
        session.execute(stmt)

    for row in all_video_rows:
        stmt = pg_insert(Video).values(**row)
        stmt = stmt.on_conflict_do_update(
            index_elements=["video_id"],
            set_={
                "channel_id": stmt.excluded.channel_id,
                "region_code": stmt.excluded.region_code,
                "published_at": stmt.excluded.published_at,
                "trending_capture_time": stmt.excluded.trending_capture_time,
                "title": stmt.excluded.title,
                "description": stmt.excluded.description,
                "view_count": stmt.excluded.view_count,
                "like_count": stmt.excluded.like_count,
                "comment_count": stmt.excluded.comment_count,
                "favorite_count": stmt.excluded.favorite_count,
            },
        )
        session.execute(stmt)

    session.flush()
    log_lineage(
        session,
        "load_trending",
        source_table="raw_trending",
        target_table="videos,channels",
        row_count=len(all_video_rows),
    )
    return len(all_video_rows)


def load_comments_file_into_db(comments_path: Path, session: Session) -> int:
    """
    Read one comments JSON file and insert comment rows (skip duplicates by comment_id).
    Returns number of comment rows inserted.
    """
    path = Path(comments_path)
    if not path.exists():
        return 0
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    by_video = payload.get("comments_by_video") or {}
    rows: List[Dict[str, Any]] = []
    for video_id, threads in by_video.items():
        for thread in threads:
            row = _comment_thread_to_row(thread, video_id)
            if row:
                rows.append(row)

    for row in rows:
        stmt = pg_insert(Comment).values(**row)
        stmt = stmt.on_conflict_do_nothing(index_elements=["comment_id"])
        session.execute(stmt)
    session.flush()
    log_lineage(
        session,
        "load_comments",
        source_table="raw_comments",
        target_table="comments",
        row_count=len(rows),
    )
    return len(rows)


def run_load_trending(
    raw_dir: Path | None = None,
    api_key: str | None = None,
    database_url: str | None = None,
) -> int:
    """
    Find trending_*.json in raw_dir, load into DB (channels + videos). Returns video count.
    """
    from ..config import get_settings
    settings = get_settings()
    root = Path(raw_dir or settings.raw_data_path)
    key = api_key or settings.youtube_api_key
    if not key:
        raise ValueError("YOUTUBE_API_KEY is required")
    paths = sorted(root.glob("trending_*.json"))
    if not paths:
        return 0
    with get_session(database_url) as session:
        return load_trending_files_into_db(paths, session, key)


def run_load_comments(
    comments_file: Path | None = None,
    raw_dir: Path | None = None,
    database_url: str | None = None,
) -> int:
    """
    Load comments from a specific file or the latest comments_*.json in raw_dir. Returns comment count.
    """
    from ..config import get_settings
    settings = get_settings()
    if comments_file:
        path = Path(comments_file)
    else:
        root = Path(raw_dir or settings.raw_data_path)
        files = sorted(root.glob("comments_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        path = files[0] if files else None
    if not path or not path.exists():
        return 0
    with get_session(database_url) as session:
        return load_comments_file_into_db(path, session)
