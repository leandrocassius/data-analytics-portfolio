"""Simple lineage logging: record job name, source/target tables, row count, status."""

from sqlalchemy.orm import Session

from .models import LineageEvent


def log_lineage(
    session: Session,
    job_name: str,
    source_table: str | None = None,
    target_table: str | None = None,
    row_count: int | None = None,
    status: str = "success",
) -> None:
    """Insert one lineage_events row. Call after a successful ETL step."""
    event = LineageEvent(
        job_name=job_name,
        source_table=source_table,
        target_table=target_table,
        row_count=row_count,
        status=status,
    )
    session.add(event)
    session.flush()
