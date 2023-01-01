from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
    func,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel:
    def from_orm(response_data):
        return [
            vars(data)
            for data in response_data
        ]


class FinViz(Base, BaseModel):
    __tablename__ = "finviz"

    id = Column(Integer, primary_key=True, index=True)
    news_headline = Column(Text, nullable=False)
    sentiment = Column(Float, nullable=False)
    ticker = Column(Text, nullable=False)
    date_posted = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())


class Tweets(Base, BaseModel):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    sentiment = Column(Float, nullable=False)
    ticker = Column(Text, nullable=False)
    date_posted = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())


class TrackedTickers(Base, BaseModel):
    __tablename__ = 'tracked_tickers'

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(Text, nullable=False)
