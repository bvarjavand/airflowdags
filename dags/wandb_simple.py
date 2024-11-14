from airflow.operators.python_operator import PythonOperator
# airflow import

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator


# python script to run
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

def train_function_wandb(config): # setup_wandb behavior is strange
    wandb = setup_wandb(config, project="Wandb_example")

    for i in range(30):
        loss = config["mean"] + config["sd"] * np.random.randn()
        train.report({"loss": loss})
        #wandb.log(dict(loss=loss))

def tune_with_setup():
    """Example for using the setup_wandb utility with the function API"""
    tuner = tune.Tuner(
        train_function_wandb,
        tune_config=tune.TuneConfig(
            metric="loss",
            mode="min",
        ),
        param_space={
            "mean": tune.grid_search([1, 2, 3, 4, 5]),
            "sd": tune.uniform(0.2, 0.8),
        },
    )
    tuner.fit()

class WandbTrainable(tune.Trainable):
    def setup(self, config):
        self.wandb = setup_wandb(
            config,
            trial_id=self.trial_id,
            trial_name=self.trial_name,
            group="Example",
            project="Wandb_example",
        )

    def step(self):
        for i in range(30):
            loss = self.config["mean"] + self.config["sd"] * np.random.randn()
            self.wandb.log({"loss": loss})
        return {"loss": loss, "done": True}

    def save_checkpoint(self, checkpoint_dir: str):
        pass

    def load_checkpoint(self, checkpoint_dir: str):
        pass

def tune_trainable():
    """Example for using a WandTrainableMixin with the class API"""
    tuner = tune.Tuner(
        WandbTrainable,
        tune_config=tune.TuneConfig(
            metric="loss",
            mode="min",
        ),
        param_space={
            "mean": tune.grid_search([1, 2, 3, 4, 5]),
            "sd": tune.uniform(0.2, 0.8),
        },
    )
    results = tuner.fit()

    return results.get_best_result().config

# run the dag
with DAG(
    "wandb_simple",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A tutorial DAG using ray and wandb",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id="run_script",
        bash_command="wandb login",
    )

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 2",
        retries=3,
    )
    t1.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    You can document your task using the attributes `doc_md` (markdown),
    `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    rendered in the UI's Task Instance Details page.
    ![img](https://imgs.xkcd.com/comics/fixing_problems.png)
    **Image Credit:** Randall Munroe, [XKCD](https://xkcd.com/license.html)
    """
    )

    dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG; OR
    dag.doc_md = """
    This is a documentation placed anywhere
    """  # otherwise, type it like this

    t3 = PythonOperator(
        task_id="templated",
        depends_on_past=True,
        provide_context=False,
        python_callable=tune_with_callback,
    )
    t3.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    Runs the ray+wandb example
    **Credit:** https://docs.ray.io/en/latest/tune/examples/tune-wandb.html
    """

    [t1, t2] >> t3

# # build and run dag
# dag = DAG('wandb_simple', default_args=default_args)

# PythonOperator(dag=dag,
#                task_id='wandb_simple',
#                provide_context=False,
#                python_callable=tune_with_callback,
#                #op_args=['arguments_passed_to_callable'],
#                #op_kwargs={'keyword_argument':'which will be passed to function'},
#               )
