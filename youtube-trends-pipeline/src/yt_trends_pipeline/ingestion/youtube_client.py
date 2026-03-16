"""YouTube Data API v3 client with retry and rate limiting."""

import time
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeClient:
    """Thin wrapper around the YouTube Data API with retry and backoff."""

    def __init__(self, api_key: str, max_retries: int = 3, delay_seconds: float = 0.2) -> None:
        self._api_key = api_key
        self._max_retries = max_retries
        self._delay_seconds = delay_seconds
        self._youtube = build("youtube", "v3", developerKey=api_key)

    def _request(self, method: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute an API request with retries and rate limiting."""
        last_error: Optional[Exception] = None
        for attempt in range(self._max_retries):
            try:
                time.sleep(self._delay_seconds)
                request = getattr(self._youtube, method)().list(**kwargs)
                return request.execute()
            except HttpError as e:
                last_error = e
                if e.resp.status in (429, 500, 503):
                    time.sleep(self._delay_seconds * (2 ** attempt))
                    continue
                raise
        if last_error:
            raise last_error
        return {}

    def get_trending_videos(
        self,
        region_code: str,
        max_results: int = 50,
        part: str = "snippet,statistics,contentDetails",
    ) -> List[Dict[str, Any]]:
        """Fetch most popular (trending) videos for a region. Returns list of video resource dicts."""
        result = self._request(
            "videos",
            part=part,
            chart="mostPopular",
            regionCode=region_code,
            maxResults=min(max_results, 50),
        )
        return result.get("items", [])

    def get_channel_details(
        self,
        channel_ids: List[str],
        part: str = "snippet,statistics",
    ) -> List[Dict[str, Any]]:
        """Fetch channel details for given channel IDs. API accepts up to 50 IDs per request."""
        if not channel_ids:
            return []
        all_items: List[Dict[str, Any]] = []
        for i in range(0, len(channel_ids), 50):
            batch = channel_ids[i : i + 50]
            result = self._request("channels", part=part, id=",".join(batch))
            all_items.extend(result.get("items", []))
        return all_items

    def get_video_comments(
        self,
        video_id: str,
        max_results: int = 50,
        part: str = "snippet",
        order: str = "relevance",
    ) -> List[Dict[str, Any]]:
        """Fetch top-level comments for a video. Returns list of commentThread resources."""
        try:
            result = self._request(
                "commentThreads",
                part=part,
                videoId=video_id,
                maxResults=min(max_results, 100),
                order=order,
                textFormat="plainText",
            )
            return result.get("items", [])
        except HttpError as e:
            if e.resp.status == 403 and "commentsDisabled" in str(e):
                return []
            raise
