import os
import yaml


def load_cities(path: str = "/opt/airflow/config/cities.yml") -> list[dict]:
    with open(path) as f:
        return yaml.safe_load(f)["cities"]


def get_db_connection_params() -> dict:
    return {
        "host": os.environ.get("WAREHOUSE_HOST", "postgres"),
        "port": os.environ.get("WAREHOUSE_PORT", "5432"),
        "dbname": os.environ.get("WAREHOUSE_DB", "warehouse"),
        "user": os.environ.get("WAREHOUSE_USER", "de"),
        "password": os.environ.get("WAREHOUSE_PASSWORD", "de"),
    }