"""
Data pipeline to create all Airflow Connections and Variables.
"""
from airflow import DAG, settings
from airflow.models import Variable, Connection
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import json
import os

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.now(),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "catchup": False,
}

dag = DAG(
    "setup",
    default_args=default_args,
    schedule_interval=None,
)


def variable_setup():
    """ Create Airflow variables and connections. """
    with open(os.path.join(os.getcwd(), "dags/tools/env_vars.json"), 'r') as f:
        env_vars = json.load(f)

    Variable.set("STOCK_TICKERS", "", serialize_json=True)

    Variable.set("TWITTER_BEARER_TOKEN", env_vars["TWITTER_BEARER_TOKEN"])
    Variable.set("FINVIZ_URL", env_vars["FINVIZ_URL"])

    POSTGRES_USERNAME = env_vars['POSTGRES_USERNAME']
    POSTGRES_PASSWORD = env_vars['POSTGRES_PASSWORD']
    PG_HOST = env_vars['PG_HOST']
    PG_DB_NAME = env_vars['PG_DB_NAME']

    AIRFLOW_DB_URL = (
        f"postgresql+psycopg2://{POSTGRES_USERNAME}:"
        f"{POSTGRES_PASSWORD}@{PG_HOST}/{PG_DB_NAME}"
    )
    Variable.set("AIRFLOW_DB_URL", AIRFLOW_DB_URL)

    conn = Connection(
        conn_id=PG_DB_NAME,
        conn_type="Postgres",
        host=PG_HOST,
        login=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        port=5432,
        schema=PG_DB_NAME,
    )

    session = settings.Session()
    conn_name = session.query(Connection).filter(
        Connection.conn_id == conn.conn_id
    ).first()

    if str(conn_name) == str(conn.conn_id):
        return None

    session.add(conn)
    session.commit()


airflow_setup = PythonOperator(
    task_id='add_variables',
    python_callable=variable_setup,
    dag=dag,
)

airflow_setup
