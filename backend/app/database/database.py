from sqlalchemy import create_engine
import sqlalchemy.orm as orm

from app.environment import DB_URL

engine = create_engine(DB_URL)


def get_db_conn():
    db_session = orm.scoped_session(
        orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    )
    return db_session
