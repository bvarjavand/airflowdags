# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
# from airflow.operators.python_operator import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

from datetime import datetime, timedelta
import textwrap


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
    dag.doc_md = """
    This is a documentation placed anywhere
    """

    t1 = BashOperator(
        task_id="sleep",
        bash_command="sleep 2",
        retries=3,
    )

    t2.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    Can be any kind of task to run. In this case, sleep for 2s.
    """
    )

    t2 = KubernetesPodOperator(
        name="wandb-simple",
        image="debian",
        cmds=["bash", "-cx"],
        arguments=["python", "wandb_simple.py"],
        labels={"foo": "bar"},
        task_id="ray_wandb_demo",
        do_xcom_push=True,
    )

    t2.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    Runs the ray+wandb example with some extra setup
    **Credit:** https://docs.ray.io/en/latest/tune/examples/tune-wandb.html
    """
    )

    t1  >> t2
