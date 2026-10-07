from datetime import datetime

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text

# Trong Docker: dùng tên container + port nội bộ 5432
SRC_URL = "postgresql+psycopg2://cdc_user:cdc_pass@postgres_source:5432/cdc_db"
DW_URL = "postgresql+psycopg2://dw_user:dw_pass@postgres_dw:5432/datawarehouse"

SRC_SCHEMA = "banking"
DW_SCHEMA = "raw"
TABLES = ["users", "cards", "mcc_codes", "transactions"]
CHUNK = 50_000


def create_raw_schema():
    dw = create_engine(DW_URL)
    with dw.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DW_SCHEMA}"))


def load_table(table: str):
    src = create_engine(SRC_URL)
    dw = create_engine(DW_URL)

    with dw.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {DW_SCHEMA}.{table} CASCADE"))

    total = 0
    query = f"SELECT * FROM {SRC_SCHEMA}.{table}"
    for i, chunk in enumerate(pd.read_sql(query, src, chunksize=CHUNK)):
        chunk.to_sql(
            table, dw, schema=DW_SCHEMA,
            if_exists="append",
            index=False, method="multi", chunksize=5_000,
        )
        total += len(chunk)
        print(f"[{table}] loaded {total:,} rows")


with DAG(
    dag_id="banking_elt",
    start_date=datetime(2026, 1, 1),
    schedule=None,  # chạy tay trước, sau này đổi thành "@daily"
    catchup=False,
    tags=["banking"],
) as dag:
    create_schema = PythonOperator(
        task_id="create_raw_schema", python_callable=create_raw_schema
    )

    load_tasks = [
        PythonOperator(
            task_id=f"load_{t}", python_callable=load_table, op_kwargs={"table": t}
        )
        for t in TABLES
    ]

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --select path:models/banking --profiles-dir .",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --select path:models/banking --profiles-dir .",
    )

    create_schema >> load_tasks >> dbt_run >> dbt_test
