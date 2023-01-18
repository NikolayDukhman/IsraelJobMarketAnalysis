# import the libraries

from datetime import timedelta
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to write tasks!
from airflow.operators.bash_operator import BashOperator
# This makes scheduling easy
from airflow.utils.dates import days_ago


#defining DAG arguments

# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'Nikolay Dukhman',
    'start_date': days_ago(0),
    'email': ['nikolay.duhman@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


# define the DAG
dag = DAG(
    dag_id='drushim-etl-dag',
    default_args=default_args,
    description='ETL DAG for drushim.co.il website',
    schedule_interval=timedelta(days=1),
)


# define the tasks

# define the first task named extract
extract = BashOperator(
    task_id='extract',
    bash_command='cd ~/Jobs/python/extract/ && bash ../../bash/daily.sh ',
    dag=dag,
)

# define the second task named transform
transform = BashOperator(
    task_id='transform',
    bash_command='cd ~/Jobs/python/transform/ && python transform.py ',
    dag=dag,
)

# define the third task named load

load = BashOperator(
    task_id='load',
    bash_command='cd ~/Jobs/python/load/ && python load.py ',
    dag=dag,
)


# task pipeline
extract >> transform >> load
