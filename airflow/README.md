# Airflow + dbt Orchestration

This adds Apache Airflow to orchestrate your ETL and dbt runs.

## Services

- airflow_postgres: Airflow metadata DB (PostgreSQL)
- airflow-init: One-time initialization (DB migrate + admin user)
- airflow-webserver: UI at http://localhost:8080 (user: admin / pass: admin)
- airflow-scheduler: Schedules and runs DAGs

## DAG

- `airflow/dags/retail_etl_dag.py`
  - Installs project requirements
  - Runs ETL cleaning (`etl/data_processor.py`)
  - Loads to DBs (`db_admin/load_data_to_database.py`)
  - Runs dbt (`dbt run`)
  - Schedule: hourly (adjust in DAG)

## dbt Profiles

- `dbt_project/profiles/profiles.yml` is mounted to `/opt/airflow/.dbt` inside Airflow containers.

## How to Run

```bash
# Start infra + Airflow
docker-compose up -d airflow_postgres airflow-init airflow-webserver airflow-scheduler postgres mongodb

# Open Airflow UI
start http://localhost:8080
# login: admin / admin
```

Once UI is up:
- Unpause `retail_etl_and_dbt` DAG
- Trigger a run and monitor tasks

## Notes
- The DAG uses the mounted project directory at `/opt/airflow/project`
- Airflow talks to the same Postgres/Mongo defined in docker-compose
- Adjust the schedule or add sensors for near-real-time using shorter intervals

