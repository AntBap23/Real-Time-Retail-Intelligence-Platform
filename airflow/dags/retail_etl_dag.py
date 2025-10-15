from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    dag_id='retail_etl_and_dbt',
    default_args=default_args,
    description='Run ETL, load to databases, and dbt transformations',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Ensure project deps are installed inside Airflow image (optional if mounting venv)
    install_requirements = BashOperator(
        task_id='install_requirements',
        bash_command='pip install -r /opt/airflow/project/requirements.txt',
    )

    # Run your Python ETL cleaning (reads from mounted /opt/airflow/project)
    run_cleaning = BashOperator(
        task_id='run_cleaning',
        bash_command='python /opt/airflow/project/etl/data_processor.py',
        env={
            'MONGO_URI': os.getenv('MONGO_URI', 'mongodb+srv://username:password@cluster.mongodb.net/'),
            'MONGO_DB': os.getenv('MONGO_DB', 'retail_intelligence'),
        }
    )

    # Note: For Databricks implementation, use Databricks Workflows instead of this Airflow DAG
    # This DAG is kept for local development only
    databricks_notice = BashOperator(
        task_id='databricks_notice',
        bash_command='echo "For production, use Databricks Workflows instead of this Airflow DAG"',
    )

    install_requirements >> run_cleaning >> databricks_notice


