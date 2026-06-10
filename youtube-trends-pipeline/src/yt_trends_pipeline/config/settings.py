"""Central configuration loaded from environment."""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()


def get_settings() -> "Settings":
    """Return the application settings (singleton-style)."""
    return Settings()


class Settings:
    """Application settings from environment variables."""

    def __init__(self) -> None:
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql://yt_trends:yt_trends@localhost:5432/yt_trends",
        )
        regions_str: str = os.getenv("REGIONS", "US")
        self.regions: List[str] = [r.strip() for r in regions_str.split(",") if r.strip()]
        raw_path: str = os.getenv("RAW_DATA_PATH", "./data/raw")
        self.raw_data_path: Path = Path(raw_path)
        self.max_comments_per_video: int = int(os.getenv("MAX_COMMENTS_PER_VIDEO", "50"))

    def ensure_raw_data_path(self) -> Path:
        """Create raw data directory if it does not exist."""
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        return self.raw_data_path
