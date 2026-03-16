"""Fetch trending videos by region and persist raw JSON (bronze layer)."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..config import get_settings
from .youtube_client import YouTubeClient


def fetch_trending_for_region(
    client: YouTubeClient,
    region_code: str,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """Return list of video resource dicts for the given region."""
    return client.get_trending_videos(region_code=region_code, max_results=max_results)


def fetch_trending_for_regions(
    regions: List[str] | None = None,
    api_key: str | None = None,
    max_results_per_region: int = 50,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch trending videos for each region. Returns dict mapping region_code -> list of video dicts.
    """
    settings = get_settings()
    key = api_key or settings.youtube_api_key
    if not key:
        raise ValueError("YOUTUBE_API_KEY is required")
    region_list = regions or settings.regions
    client = YouTubeClient(api_key=key)
    out: Dict[str, List[Dict[str, Any]]] = {}
    for region in region_list:
        items = fetch_trending_for_region(client, region, max_results=max_results_per_region)
        out[region] = items
    return out


def save_raw_trending(
    data: Dict[str, List[Dict[str, Any]]],
    base_path: Path | None = None,
) -> List[Path]:
    """
    Save raw trending data as one JSON file per region (bronze layer).
    Filename includes timestamp. Returns list of written file paths.
    """
    settings = get_settings()
    root = base_path or settings.raw_data_path
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    written: List[Path] = []
    for region, items in data.items():
        file_path = root / f"trending_{region}_{timestamp}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"region": region, "captured_at": timestamp, "videos": items}, f, ensure_ascii=False)
        written.append(file_path)
    return written


def fetch_and_save_trending(
    regions: List[str] | None = None,
    api_key: str | None = None,
    base_path: Path | None = None,
) -> List[Path]:
    """Fetch trending for configured regions and save raw JSON. Returns paths to saved files."""
    data = fetch_trending_for_regions(regions=regions, api_key=api_key)
    return save_raw_trending(data, base_path=base_path)
