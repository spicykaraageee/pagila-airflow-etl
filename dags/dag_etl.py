import datetime 

from airflow import DAG 
from airflow.operators.python import PythonOperator

from script.extract import run_extract
from script.loading import run_loading

with DAG(
    "dag_etl",
    description="ETL Progress",
    # schedule="@daily",
    schedule="*/5 * * * *",
    catchup=False
) as dag:
    extract = PythonOperator(
        task_id="run_extract",
        python_callable=run_extract
    )
    
    loading = PythonOperator(
        task_id="run_loading",
        python_callable=run_loading
    )

    extract >> loading