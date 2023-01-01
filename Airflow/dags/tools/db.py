from sqlalchemy import create_engine
import sqlalchemy.orm as orm
from airflow.models import Variable


AIRFLOW_DB_URL = Variable.get("AIRFLOW_DB_URL")

engine = create_engine(AIRFLOW_DB_URL)


def get_db_conn():
    db_session = orm.scoped_session(
        orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    )
    return db_session
