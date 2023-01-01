import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_DB_NAME = os.getenv('PG_DB_NAME')
AIRFLOW_DB_URL = (
    f"postgresql+psycopg2://{POSTGRES_USERNAME}:"
    f"{POSTGRES_PASSWORD}@{PG_HOST}/{PG_DB_NAME}"
)
FINVIZ_URL = os.getenv('FINVIZ_URL')
