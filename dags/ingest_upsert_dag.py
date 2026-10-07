from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'demo_user',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

import psycopg2
import os

def extract_and_load_func():
    print("Starting Extract and Load...")
    
    source_hook = PostgresHook(postgres_conn_id='postgres_source')
    # We will connect directly to datawarehouse using psycopg2
    target_conn = psycopg2.connect(
        host="postgres-dw",
        port=5432,
        user=os.environ.get("DW_USER", "dw_user"),
        password=os.environ.get("DW_PASS", "dw_pass"),
        dbname=os.environ.get("DW_DB", "datawarehouse")
    )
    target_cursor = target_conn.cursor()

    # Truncate raw tables and reload (Full Load for simplicity of CDC in dbt)
    # 1. Categories
    source_categories = source_hook.get_records("SELECT id, name, description FROM categories")
    if source_categories:
        # Ensure table exists
        target_cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw.categories (
                id INT PRIMARY KEY,
                name VARCHAR(100),
                description TEXT
            )
        """)
        target_cursor.execute("TRUNCATE TABLE raw.categories CASCADE")
        target_cursor.executemany(
            "INSERT INTO raw.categories (id, name, description) VALUES (%s, %s, %s)",
            source_categories
        )

    # 2. Source Data
    source_data_records = source_hook.get_records("SELECT id, category_id, name, value, status, metadata, created_at, updated_at FROM source_data")
    if source_data_records:
        target_cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw.source_data (
                id INT PRIMARY KEY,
                category_id INT,
                name VARCHAR(50),
                value INT,
                status VARCHAR(20),
                metadata JSONB,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        target_cursor.execute("TRUNCATE TABLE raw.source_data CASCADE")
        
        # Convert dict (JSONB) to string for psycopg2 insertion
        import json
        processed_records = []
        for row in source_data_records:
            row_list = list(row)
            # metadata is at index 5
            if isinstance(row_list[5], dict):
                row_list[5] = json.dumps(row_list[5])
            processed_records.append(tuple(row_list))
            
        target_cursor.executemany(
            "INSERT INTO raw.source_data (id, category_id, name, value, status, metadata, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            processed_records
        )

    target_conn.commit()
    target_cursor.close()
    target_conn.close()
    print("Extract and Load completed successfully.")

with DAG(
    dag_id='dbt_elt_dag',
    default_args=default_args,
    description='A DAG to Extract/Load data and run dbt transformations',
    schedule_interval=timedelta(minutes=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['demo', 'dbt', 'elt'],
) as dag:

    extract_load_task = PythonOperator(
        task_id='extract_and_load',
        python_callable=extract_and_load_func,
    )

    dbt_snapshot_task = BashOperator(
        task_id='dbt_snapshot',
        bash_command='cd /opt/airflow/dbt && dbt snapshot --profiles-dir .',
    )

    dbt_run_task = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir . --exclude path:models/banking',
    )

    extract_load_task >> dbt_snapshot_task >> dbt_run_task

