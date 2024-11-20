from airflow.models.dag import DAG
from airflow.operators.python_operator import PythonOperator

from datetime import datetime, timedelta
import textwrap

#### Defining the python code

import numpy as np
import ray
from ray import train, tune
from ray.air.integrations.wandb import WandbLoggerCallback, setup_wandb

def train_function(config):
    for i in range(30):
        loss = config["mean"] + config["sd"] * np.random.randn()
        train.report({"loss": loss})

def tune_with_callback():
    """Example for using a WandbLoggerCallback with the function API"""
    tuner = tune.Tuner(
        train_function,
        tune_config=tune.TuneConfig(
            metric="loss",
            mode="min",
        ),
        run_config=train.RunConfig(
            callbacks=[WandbLoggerCallback(project="Wandb_example")]
        ),
        param_space={
            "mean": tune.grid_search([1, 2, 3, 4, 5]),
            "sd": tune.uniform(0.2, 0.8),
        },
    )
    tuner.fit()

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

    t1 = PythonOperator(task_id="tune_with_callback", python_callable=tune_with_callback)
