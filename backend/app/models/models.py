from sqlalchemy import func

from app import db


class BaseModel:
    def from_orm(response_data):
        return [
            vars(data)
            for data in response_data
        ]


class FinViz(db.Model, BaseModel):
    __tablename__ = "finviz"

    id = db.Column(db.Integer, primary_key=True, index=True)
    date_posted = db.Column(db.Date, nullable=False)
    news_headline = db.Column(db.String, nullable=False)
    sentiment = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=func.now())


class Tweets(db.Model, BaseModel):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True, index=True)
    date_posted = db.Column(db.Date, nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=func.now())
    text = db.Column(db.String, nullable=False)
    sentiment = db.Column(db.Float, nullable=False)
