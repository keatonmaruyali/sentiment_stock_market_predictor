import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
PG_PORT = os.getenv('PG_PORT')
PG_DB_NAME = os.getenv('PG_DB_NAME')
DB_URL = (
    f'postgresql://{POSTGRES_USERNAME}:'
    f'{POSTGRES_PASSWORD}@db:{PG_PORT}/{PG_DB_NAME}'
)

FINVIZ_URL = os.getenv('FINVIZ_URL')
