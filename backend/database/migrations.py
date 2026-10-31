"""Additive schema upgrade; unknown legacy provenance stays unverified."""
from sqlalchemy import inspect, text
from models.base import Base
from models import entities  # register metadata


def ensure_schema(engine):
    Base.metadata.create_all(bind=engine)
    additions = {
        "users": {"phone": "VARCHAR(30)"},
        "price_history": {"data_source": "VARCHAR(30) NOT NULL DEFAULT 'unknown'"},
    }
    with engine.begin() as conn:
        for table, columns in additions.items():
            existing = {c["name"] for c in inspect(conn).get_columns(table)}
            for name, sql_type in columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}"))
        conn.execute(text("UPDATE price_history SET data_source='synthetic' "
                          "WHERE product_id LIKE 'DEMO-%' AND data_source='unknown'"))
