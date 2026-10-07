from datetime import datetime, timedelta
import random
import time

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule

# Default arguments for the DAG
default_args = {
    'owner': 'demo_user',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Define the DAG
with DAG(
    dag_id='demo_airflow_features',
    default_args=default_args,
    description='A comprehensive demo DAG showing various Airflow features',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['demo', 'tutorial'],
) as dag:

    # 1. BashOperator: Run a simple bash command
    start_task = BashOperator(
        task_id='start_task',
        bash_command='echo "Starting the Airflow demo DAG at $(date)"',
    )

    # 2. PythonOperator: Run a Python function
    def process_data_func(**kwargs):
        print("Processing data...")
        time.sleep(2)  # Simulate some work
        # Pass a value via XCom
        return random.choice(['success', 'failure'])

    process_data = PythonOperator(
        task_id='process_data',
        python_callable=process_data_func,
    )

    # 3. BranchPythonOperator: Branch logic based on condition
    def decide_path(**kwargs):
        # Pull the return value of process_data from XCom
        ti = kwargs['ti']
        status = ti.xcom_pull(task_ids='process_data')
        
        print(f"Data processing status was: {status}")
        
        if status == 'success':
            return 'success_path_task'
        else:
            return 'failure_path_task'

    branching_task = BranchPythonOperator(
        task_id='branching_task',
        python_callable=decide_path,
        provide_context=True,
    )

    # 4. DummyOperators / Alternative paths
    success_path_task = BashOperator(
        task_id='success_path_task',
        bash_command='echo "Data processing was successful! Proceeding with success path."',
    )

    failure_path_task = BashOperator(
        task_id='failure_path_task',
        bash_command='echo "Data processing failed. Triggering alert/fallback path."',
    )

    # 5. Join task with TriggerRule
    # We want this to run regardless of whether we went down success or failure path
    join_task = BashOperator(
        task_id='join_task',
        bash_command='echo "Joining paths back together. This runs if either success or failure path finishes."',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # 6. Final Task
    end_task = DummyOperator(
        task_id='end_task'
    )

    # Define the dependencies (the DAG structure)
    start_task >> process_data >> branching_task
    branching_task >> [success_path_task, failure_path_task]
    success_path_task >> join_task
    failure_path_task >> join_task
    join_task >> end_task
