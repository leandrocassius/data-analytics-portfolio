# Store Performance with BigQuery

An analytics project that uses Google BigQuery and Google Analytics data to evaluate an online store’s performance, traffic sources, and conversions.

## Overview

Understanding customer behavior, traffic sources, and conversion patterns is essential for e-commerce. This project uses BigQuery to query the Google Analytics sample dataset and answer questions about traffic, conversions, top pages, and seasonal trends.

## What I Did

- **BigQuery exploration** — Schema inspection and SQL queries on `ga_sessions_*` tables
- **Traffic analysis** — Main traffic sources (organic search, direct, referral, YouTube, etc.)
- **Conversion analysis** — How user demographics and behavior relate to conversion rates
- **Trend analysis** — Monthly traffic by source, seasonal patterns, and growth trends
- **Recommendations** — Insights for UX and marketing (e.g., focus on organic search, review YouTube channel)

## Algorithms & Tools

- **Google BigQuery** — SQL for large-scale analytics
- **Google Analytics** — Session and hit data
- **pandas** — Query result handling
- **matplotlib**, **seaborn**, **plotly** — Visualizations

## Data

- **Source:** [Google Analytics Sample](https://console.cloud.google.com/marketplace/product/obfuscated-ga360-data/obfuscated-ga360-data) (BigQuery public dataset)
- **Environment:** Designed for Kaggle (BigQuery integration) or local use with GCP credentials

## Setup

```bash
pip install -r requirements.txt
# Set GCP credentials for local runs; use Kaggle for direct BigQuery access
jupyter notebook evaluating-store-performance-with-bigquery.ipynb
```
