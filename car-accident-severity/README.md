# Analyzing and Predicting Car Accident Severity

An end-to-end project that explores US car accident data and builds a model to predict accident severity, supporting road safety analysis and resource planning.

## Overview

Car accidents have major impacts on public safety and infrastructure. This project analyzes over 7 million US accident records to uncover patterns and train a classifier that predicts severity based on time, location, weather, and other factors.

## What I Did

- **Exploratory data analysis** — Geospatial and time-series visualizations, severity distributions, and demographic patterns
- **Feature engineering** — Handling missing values, encoding categoricals, scaling with scikit-learn pipelines (`ColumnTransformer`)
- **Modeling** — XGBoost classification with class weights for imbalanced targets
- **Evaluation** — Confusion matrices, classification reports, and hyperparameter tuning (e.g., GridSearchCV)

## Algorithms & Tools

- **XGBoost** (XGBClassifier) for classification
- **scikit-learn** — Pipelines, ColumnTransformer, StandardScaler, OneHotEncoder, OrdinalEncoder, train/test split, GridSearchCV
- **pandas**, **matplotlib**, **seaborn** — Data manipulation and visualization

## Data

- **Source:** [US Accidents](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents) on Kaggle
- Place `US_Accidents_March23.csv` in a `data/` folder to run locally

## Setup

```bash
pip install -r requirements.txt
jupyter notebook analyzing-and-predicting-car-accident-severity.ipynb
```
