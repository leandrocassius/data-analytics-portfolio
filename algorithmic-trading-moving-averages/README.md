# Algorithmic Trading with Moving Averages

A trend-reversal strategy built on NYSE stock data (2010–2016) using short- and long-term moving averages to generate buy/sell signals.

## Overview

This project implements a simple algorithmic trading strategy based on trend reversal. By comparing short-term and long-term moving averages (e.g., 30-day vs 90-day), the model identifies potential reversals and produces trading signals. Backtests show the strategy outperforming a passive buy-and-hold approach.

## What I Did

- **Data loading and preprocessing** — NYSE price data (2010–2016) with pandas
- **Technical indicators** — Daily and monthly returns, moving averages (MA-30, MA-90)
- **Signal generation** — Trend-reversal logic using short- vs long-term MA crossover
- **Backtesting** — Comparison of strategy returns vs passive investment (e.g., ~446% ROI vs ~223% for buy-and-hold)

## Algorithms & Tools

- **Moving averages** — Short- and long-term trend smoothing
- **pandas** — Time series manipulation
- **matplotlib**, **seaborn** — Plotting returns, MAs, and signals

## Data

- **Source:** NYSE dataset (e.g., [prices-split-adjusted](https://www.kaggle.com/datasets/dgawlik/nyse)) on Kaggle
- Place `prices-split-adjusted.csv` in a `data/` folder to run locally

## Setup

```bash
pip install -r requirements.txt
jupyter notebook algorithmic-trading-with-moving-averages.ipynb
```
