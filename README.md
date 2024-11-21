## Airflow DAGS

Synced to airflow pods via helm chart using airflow-config.yaml

### Relevant documentation for future work:
##### Airflow docs
Community helm chart (great resource) (yaml with github syncing in config folder): https://github.com/airflow-helm/charts/tree/main/charts/airflow#frequently-asked-questions
Astronomer install: https://github.com/astronomer/airflow-chart

##### Ray docs
Starting a Ray runtime: https://docs.ray.io/en/latest/ray-core/starting-ray.html#starting-ray-via-the-cli-ray-start

##### Connecting Ray to Wandb:
The cleanest way including different options is contained in the `wandb_simple.py` scripts and discussed further here: https://docs.ray.io/en/latest/tune/examples/tune-wandb.html

##### Connecting Airflow to Ray:
create the connection to the ray cluster with `http://<RayCluster name>-head-svc:8265`: https://docs.ray.io/en/latest/cluster/configure-manage-dashboard.html#viewing-ray-dashboard-in-browsers
