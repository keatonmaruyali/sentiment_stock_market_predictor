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


class ModelTrainingData(Base, BaseModel):
    __tablename__ = 'model_training_data'

    id = Column(Integer, primary_key=True, index=True)
    date_posted = Column(DateTime, index=True, nullable=False)
    headline_sentiment = Column(Float, nullable=False)
    headline_sentiment_change = Column(Float, nullable=False)
    sma3_sentiment_headlines = Column(Float, nullable=False)
    headline_sentiment_change_t1 = Column(Float, nullable=False)
    tweet_sentiment = Column(Float, nullable=False)
    tweet_sentiment_change = Column(Float, nullable=False)
    sma3_sentiment_tweets = Column(Float, nullable=False)
    tweet_sentiment_change_t1 = Column(Float, nullable=False)
