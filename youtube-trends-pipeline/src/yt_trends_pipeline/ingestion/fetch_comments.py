"""Fetch comments for a set of video IDs and persist raw JSON (bronze layer)."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..config import get_settings
from .youtube_client import YouTubeClient


def fetch_comments_for_video(
    client: YouTubeClient,
    video_id: str
) -> List[Dict[str, Any]]:
    """Return list of commentThread resource dicts for the video."""
    return client.get_video_comments(video_id, max_results=50)


def fetch_comments_for_videos(
    video_ids: List[str]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch comments for each video. Returns dict mapping video_id -> list of commentThread dicts.
    """
    client = YouTubeClient()
    out: Dict[str, List[Dict[str, Any]]] = {}
    for vid in video_ids:
        items = fetch_comments_for_video(client, vid)
        out[vid] = items
    return out


def save_raw_comments(
    # Fixme: too many paths
    data: Dict[str, List[Dict[str, Any]]],
    base_path: Path | None = None,
) -> Path:
    """Save raw comments as one JSON file (all videos). Returns path to written file."""
    settings = get_settings()
    root = base_path or settings.raw_data_path
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = root / f"comments_{timestamp}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"captured_at": timestamp, "comments_by_video": data}, f, ensure_ascii=False)
    return file_path


def fetch_and_save_comments(
    video_ids: List[str],
    base_path: Path | None = None,
) -> Path:
    """Fetch comments for the given video IDs and save raw JSON. Returns path to saved file."""
    data = fetch_comments_for_videos(video_ids)
    return save_raw_comments(data, base_path=base_path)
