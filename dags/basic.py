from airflow.models.dag import DAG
from airflow.operators.python_operator import PythonOperator

from datetime import datetime, timedelta
import textwrap

#### Defining the python code

def basic():
    myvar = "Hello World!"
    print(myvar)


with DAG(
    "basic",
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0, # or 1
        "retry_delay": timedelta(minutes=5),
    },
    description="A tutorial DAG using ray and wandb",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    dag.doc_md = """
    This is documentation placed anywhere
    """

    PythonOperator(task_id="basic", python_callable=basic)
