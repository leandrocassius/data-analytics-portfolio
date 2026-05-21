# YouTube Trends Data Pipeline

A portfolio data engineering project that ingests YouTube trending data via the YouTube Data API, stores it in PostgreSQL, and processes titles, descriptions, and comments for theme analysis and sentiment. It showcases **API ingestion**, **relational modeling**, **orchestration with Airflow**, **text preprocessing and lemmatization**, and **basic data lineage** logging.

## Tech stack

- **Python** – ingestion, ETL, text processing
- **PostgreSQL** – relational storage (app data + Airflow metadata)
- **SQLAlchemy** – schema as single source of truth, session management, lineage table
- **Apache Airflow** – orchestration (local Docker, daily DAG)
- **spaCy** – tokenization and lemmatization
- **VADER** – comment sentiment analysis

## Architecture

```mermaid
flowchart LR
  ytApi["YouTube API"] --> rawJson["Raw JSON (bronze)"]
  rawJson --> ingestVideos["Ingest videos & channels"]
  ingestVideos --> pgVideos["PostgreSQL videos"]
  ingestVideos --> pgChannels["PostgreSQL channels"]
  ytApi --> commentsRaw["Raw comments JSON"]
  commentsRaw --> ingestComments["Ingest comments"]
  ingestComments --> pgComments["PostgreSQL comments"]
  pgVideos --> buildText["Build text features"]
  pgComments --> buildText
  buildText --> pgTextFeatures["PostgreSQL text_features"]
  buildText --> lineage["lineage_events log"]
```

- **Bronze**: Raw JSON files per region (`trending_<region>_<ts>.json`) and one `comments_<ts>.json`.
- **Silver**: Normalized tables `videos`, `channels`, `comments` in PostgreSQL.
- **Gold**: `text_features` (lemmatized title+description, comment sentiment aggregates) and `lineage_events` (job name, source/target, row count, run time).

## How to run

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- [YouTube Data API v3](https://console.cloud.google.com/apis/credentials) key

### Local setup

1. **Clone and install**

   ```bash
   cd youtube-trends-pipeline
   pip install -e ".[dev]"
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('vader_lexicon')"
   ```

   Or use the Makefile: `make install`.

2. **Environment**

   Copy `.env.example` to `.env` and set:

   - `YOUTUBE_API_KEY` – required for ingestion
   - `DATABASE_URL` – e.g. `postgresql://yt_trends:yt_trends@localhost:5432/yt_trends` when using Docker Postgres
   - `REGIONS` – comma-separated (e.g. `US,BR`)

3. **Start Postgres (and Airflow)**

   ```bash
   docker-compose up -d
   ```

   For Postgres only: `docker-compose up -d postgres` (then run the pipeline locally with `make run-pipeline`).

4. **Create tables**

   ```bash
   make init-db
   ```

   This runs SQLAlchemy `create_all` for `videos`, `channels`, `comments`, `text_features`, `lineage_events`.

5. **Run the pipeline**

   - **Without Airflow** (one-shot):  
     `make run-pipeline`  
     This fetches trending, loads to DB, fetches comments, loads comments, and builds text features.

   - **With Airflow**:  
     Open http://localhost:8080 (user `admin`, password `admin`), unpause and trigger the `yt_trends_dag` DAG.

### What the pipeline does

1. **Fetch trending** – Calls `videos.list` with `chart=mostPopular` and `regionCode` for each region; writes raw JSON to `data/raw/`.
2. **Load trending** – Reads raw trending JSON, fetches channel details via API, upserts into `channels` and `videos`.
3. **Fetch comments** – For each video in `videos`, fetches top comments and saves raw JSON.
4. **Load comments** – Inserts into `comments` (skip duplicates by `comment_id`).
5. **Build text features** – For each video: lemmatizes title+description, scores comment sentiment with VADER, aggregates (mean, std, count); upserts into `text_features` and logs a row in `lineage_events`.

## Sample data (for notebooks without a DB)

To export the current DB tables to CSV so the exploratory notebook (and others) can run without PostgreSQL:

```bash
python scripts/export_sample_data.py
```

This writes `data/example/channels.csv`, `videos.csv`, `comments.csv`, `text_features.csv`, and `lineage_events.csv`. The notebook automatically uses these CSVs when present.

## Sample analysis

After a run, you can inspect data and lineage in PostgreSQL.

**Themes in trending (example – top tokens from lemmatized text):**

```sql
SELECT video_id, left(lemmatized_text, 200) AS sample
FROM text_features
WHERE lemmatized_text IS NOT NULL
LIMIT 10;
```

**Comment sentiment by region:**

```sql
SELECT v.region_code,
       avg(t.comment_sentiment_avg) AS avg_sentiment,
       count(*) AS videos_with_comments
FROM videos v
JOIN text_features t ON v.video_id = t.video_id
WHERE t.comment_sentiment_count > 0
GROUP BY v.region_code;
```

**Last pipeline runs (lineage):**

```sql
SELECT job_name, source_table, target_table, run_at, row_count, status
FROM lineage_events
ORDER BY run_at DESC
LIMIT 10;
```

## Project layout

```
youtube-trends-pipeline/
├── dags/
│   └── yt_trends_dag.py       # Airflow DAG (fetch → load → comments → text features)
├── src/yt_trends_pipeline/
│   ├── config/settings.py     # Env-based config
│   ├── db/
│   │   ├── models.py          # SQLAlchemy models (videos, channels, comments, text_features, lineage_events)
│   │   ├── session.py         # Engine and session factory
│   │   ├── lineage.py        # Simple lineage logging helper
│   │   └── init_db.py        # Create tables
│   ├── ingestion/
│   │   ├── youtube_client.py  # API client with retry/rate limit
│   │   ├── fetch_trending.py # Trending by region, save raw JSON
│   │   ├── fetch_comments.py # Comments per video, save raw JSON
│   │   └── load_raw_to_db.py # Bronze → silver (videos, channels, comments)
│   ├── processing/
│   │   ├── text_cleaning.py  # URLs, emoji, lowercasing
│   │   ├── lemmatization.py  # spaCy lemmatization
│   │   ├── sentiment.py      # VADER scoring and aggregation
│   │   └── build_text_features.py  # Gold table + lineage log
│   └── cli.py                 # Entrypoint for make run-pipeline
├── scripts/
│   └── init-postgres.sql     # Create airflow DB/user for Docker Postgres
├── docker-compose.yml        # Postgres + Airflow
├── pyproject.toml / requirements.txt
├── .env.example
└── Makefile
```

## Future work

- **dbt** – Move silver→gold transformations into dbt models.
- **Topic modeling** – LDA or similar on `text_features.lemmatized_text` for theme clusters.
- **Multi-language** – Multilingual spaCy model and per-language sentiment.
- **Production lineage** – OpenLineage or similar instead of a custom `lineage_events` table.
- **Incremental loads** – Only fetch comments for new videos or since last run.
