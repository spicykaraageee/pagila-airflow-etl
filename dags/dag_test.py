import datetime 

from airflow import DAG 
from airflow.operators.python import PythonOperator

from script.hello import main

with DAG(
    "hello_world",
    description="World of Airflow",
    # schedule="@daily",
    schedule="*/5 * * * *",
    catchup=False
) as dag:
    hellow = PythonOperator(
        task_id="hello_world",
        python_callable=main
    )
    
    hellow
