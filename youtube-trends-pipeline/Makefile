.PHONY: init-db run-pipeline airflow-up airflow-down install help

help:
	@echo "yt-trends-pipeline targets:"
	@echo "  install       - Install package and dependencies (pip install -e .)"
	@echo "  init-db       - Create PostgreSQL tables via SQLAlchemy"
	@echo "  run-pipeline  - Run full pipeline once (fetch + load + text features)"
	@echo "  airflow-up    - Start Postgres + Airflow via docker-compose"
	@echo "  airflow-down  - Stop docker-compose services"

install:
	pip install -e ".[dev]"
	python -m spacy download en_core_web_sm
	python -c "import nltk; nltk.download('vader_lexicon')"

init-db:
	python -m yt_trends_pipeline.db.init_db

run-pipeline:
	python -m yt_trends_pipeline.cli run

airflow-up:
	docker-compose up -d

airflow-down:
	docker-compose down
