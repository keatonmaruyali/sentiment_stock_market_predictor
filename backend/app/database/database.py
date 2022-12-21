from sqlalchemy import create_engine
import sqlalchemy.orm as orm

PSQL_DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"

engine = create_engine(PSQL_DATABASE_URL)


def get_db_conn():
    db_session = orm.scoped_session(
        orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    )
    return db_session
