"""CLI entrypoint for running the pipeline locally (without Airflow)."""

import argparse
import sys
from pathlib import Path

from .config import get_settings
from .db.session import get_session
from .db.models import Video
from .ingestion.fetch_trending import fetch_and_save_trending
from .ingestion.fetch_comments import fetch_and_save_comments
from .ingestion.load_raw_to_db import run_load_trending, run_load_comments


def _get_video_ids_from_db(session) -> list[str]:
    """Return list of video_id from videos table."""
    rows = session.query(Video.video_id).all()
    return [r[0] for r in rows]


def run_pipeline(
    regions: list[str] | None = None,
    skip_fetch_trending: bool = False,
    skip_fetch_comments: bool = False,
    skip_load_trending: bool = False,
    skip_load_comments: bool = False,
    skip_text_features: bool = False,
    raw_dir: Path | None = None,
) -> None:
    """
    Run the full pipeline: fetch trending -> load to DB -> fetch comments -> load comments -> build text features.
    """
    settings = get_settings()
    raw_path = raw_dir or settings.raw_data_path
    raw_path = Path(raw_path)
    raw_path.mkdir(parents=True, exist_ok=True)
    region_list = regions or settings.regions

    if not skip_fetch_trending:
        print("Fetching trending videos...")
        fetch_and_save_trending(regions=region_list, base_path=raw_path)
        print("Saved raw trending JSON.")
    else:
        print("Skipping fetch trending.")

    if not skip_load_trending:
        print("Loading trending data into DB...")
        n = run_load_trending(raw_dir=raw_path)
        print(f"Loaded {n} videos (and channels).")
    else:
        print("Skipping load trending.")

    if not skip_fetch_comments:
        with get_session() as session:
            video_ids = _get_video_ids_from_db(session)
        if not video_ids:
            print("No video IDs in DB; skipping comment fetch.")
        else:
            print(f"Fetching comments for {len(video_ids)} videos...")
            fetch_and_save_comments(video_ids, base_path=raw_path)
            print("Saved raw comments JSON.")
    else:
        print("Skipping fetch comments.")

    if not skip_load_comments:
        print("Loading comments into DB...")
        n = run_load_comments(raw_dir=raw_path)
        print(f"Loaded {n} comments.")
    else:
        print("Skipping load comments.")

    if not skip_text_features:
        try:
            from .processing.build_text_features import run_build_text_features
            print("Building text features...")
            n = run_build_text_features()
            print(f"Built text features for {n} videos.")
        except ImportError:
            print("Text features module not ready; skipping.")
    else:
        print("Skipping text features.")


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube Trends pipeline")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run"],
        help="Command to run (default: run)",
    )
    parser.add_argument("--regions", nargs="+", help="Override regions (e.g. US BR)")
    parser.add_argument("--skip-fetch-trending", action="store_true")
    parser.add_argument("--skip-fetch-comments", action="store_true")
    parser.add_argument("--skip-load-trending", action="store_true")
    parser.add_argument("--skip-load-comments", action="store_true")
    parser.add_argument("--skip-text-features", action="store_true")
    parser.add_argument("--raw-dir", type=Path, help="Override raw data directory")
    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(
            regions=args.regions,
            skip_fetch_trending=args.skip_fetch_trending,
            skip_fetch_comments=args.skip_fetch_comments,
            skip_load_trending=args.skip_load_trending,
            skip_load_comments=args.skip_load_comments,
            skip_text_features=args.skip_text_features,
            raw_dir=args.raw_dir,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
