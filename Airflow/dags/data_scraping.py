"""
Data pipeline perform scheduled web scraping and augmentation
jobs.
"""
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import ast
from datetime import datetime, timedelta

from tools.utils import add_headlines, add_twitter, sync_tickers


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
    "schedule_internal": "@daily",
}

dag = DAG(
    "web_scraping",
    default_args=default_args,
    schedule_interval=timedelta(1),
)


def check_conn():
    hook = PostgresHook(postgres_conn_id='stock_market')
    df = hook.get_pandas_df(sql="SELECT * FROM finviz;")
    print(df)


def sync_tracked_tickers():
    """
    Sync tickers in db with those stored in Airflow variables.
    """
    hook = PostgresHook(postgres_conn_id='stock_market')
    db_tickers = hook.get_records(sql="SELECT ticker FROM tracked_tickers;")[0]
    airflow_tickers = Variable.get('STOCK_TICKERS', default_var=[])

    if len(airflow_tickers) != 0:
        airflow_tickers = ast.literal_eval(airflow_tickers)

    new_airflow_tickers = sync_tickers(
        db_tickers=db_tickers,
        airflow_tickers=airflow_tickers,
    )

    if len(new_airflow_tickers) != 0:
        Variable.set('STOCK_TICKERS', new_airflow_tickers)


syncing_tracked_tickers = PythonOperator(
    task_id='syncing_tracked_tickers',
    python_callable=sync_tracked_tickers,
    dag=dag,
)

checking_conn = PythonOperator(
    task_id='checking_conn',
    python_callable=check_conn,
    dag=dag,
)

adding_headlines = PythonOperator(
    task_id='adding_headlines',
    python_callable=add_headlines,
    op_kwargs={
        'ticker_list': Variable.get(
            'STOCK_TICKERS',
            default_var=[],
        )
    },
    dag=dag,
)

adding_twitter = PythonOperator(
    task_id='adding_twitter',
    python_callable=add_twitter,
    op_kwargs={
        'ticker_list': Variable.get(
            'STOCK_TICKERS',
            default_var=[],
        )
    },
    dag=dag,
)

syncing_tracked_tickers >> checking_conn >> [adding_headlines, adding_twitter]
