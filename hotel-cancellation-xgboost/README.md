# Predicting Hotel Cancellations with XGBoost

A classification project that predicts whether a hotel booking will be canceled, helping hotels optimize occupancy, staffing, and revenue.

## Overview

Predicting cancellations allows hotels to better manage room inventory, avoid overbooking, and adjust staffing and pricing. This project uses an Extreme Gradient Boosting (XGBoost) classifier trained on a hotel reservations dataset.

## What I Did

- **Exploratory data analysis** — Visualizations and summary statistics to understand booking patterns and cancellation drivers
- **Feature engineering** — Preprocessing and scaling with `MinMaxScaler`
- **Modeling** — XGBoost classification with **Stratified K-Fold cross-validation** (5 folds)
- **Evaluation** — ROC-AUC curves, confusion matrices, accuracy, and feature importance analysis

## Algorithms & Tools

- **XGBoost** (Extreme Gradient Boosting) for classification
- **scikit-learn** — StratifiedKFold, MinMaxScaler, ROC-AUC, confusion matrix
- **pandas**, **matplotlib**, **seaborn** — Data handling and visualization

## Data

- **Source:** [Hotel Reservations Classification Dataset](https://www.kaggle.com/datasets/ahsan81/hotel-reservations-classification-dataset) on Kaggle
- Place `Hotel Reservations.csv` in a `data/` folder to run locally

## Setup

```bash
pip install -r requirements.txt
jupyter notebook predicting-cancellations-with-xgb.ipynb
```
