from airflow import DAG
from airflow.operators.python_operator import PythonOperator
# airflow import

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

# build and run dag
dag = DAG('wandb_simple', default_args=default_args)

PythonOperator(dag=dag,
               task_id='wandb_simple',
               provide_context=False,
               python_callable=tune_with_callback,
               #op_args=['arguments_passed_to_callable'],
               #op_kwargs={'keyword_argument':'which will be passed to function'},
              )
