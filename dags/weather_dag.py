from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from ingestion.config import load_cities
from ingestion.extract import extract_all
from ingestion.load import load_all


def _extract_and_load(logical_date: str, **context):
    """Combined extract+load task: fetch from the API, then write to Postgres.

    Combined into one task (not two) because the extracted data (a dict of
    city -> API response) would otherwise need to be passed between tasks via
    XCom, which is meant for small metadata, not raw API payloads.
    """
    cities = load_cities()
    data = extract_all(logical_date, cities)
    load_all(logical_date, data)


with DAG(
    dag_id="weather_pipeline",
    description="Extract daily weather from Open-Meteo, load to Postgres, transform with dbt.",
    schedule="@daily",
    start_date=datetime(2026, 8, 1),
    catchup=True,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": 300,  # seconds
    },
) as dag:

    extract_and_load = PythonOperator(
        task_id="extract_and_load",
        python_callable=_extract_and_load,
        op_kwargs={"logical_date": "{{ ds }}"},
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test",
    )

    extract_and_load >> dbt_run >> dbt_test