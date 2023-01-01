from datetime import datetime
from typing import List
from sqlalchemy.exc import IntegrityError

from backend.app.models import models
from backend.app.services import finviz_scraper, twitter_scraper


# Ticker Operations:
def get_tickers(db):
    tickers = db.query(models.TrackedTickers).all()
    return models.TrackedTickers.from_orm(tickers)


def add_tickers(db, tickers: List[str]):
    tickers = [
        {'ticker': ticker}
        for ticker in tickers
    ]

    tickers = [
        models.TrackedTickers(**ticker)
        for ticker in tickers
    ]

    try:
        db.add_all(tickers)
        db.commit()
        return tickers
    except IntegrityError:
        return None


# FinViz Operations:
def get_headlines(db):
    headlines = db.query(models.FinViz).order_by(
        models.FinViz.date_posted.desc()
    ).all()
    return models.FinViz.from_orm(headlines)


def add_headlines(db, tickers: List[str]):
    added_headlines = []

    for ticker in tickers:
        scraper_results = finviz_scraper(ticker)
        for headline in scraper_results.to_dict('records'):
            try:
                date = datetime.strptime(
                    headline['date'],
                    '%b-%d-%y  %H:%M%p',
                )
            except ValueError:
                now = datetime.today().strftime('%b-%d-%y')
                date = datetime.strptime(
                    f'{now} {headline["date"]}',
                    '%b-%d-%y  %H:%M%p',
                )

            added_headlines.append(
                {
                    'news_headline': headline['news_headline'],
                    'sentiment': headline['sentiment'],
                    'ticker': ticker,
                    'date_posted': date,
                    'date_created': datetime.today(),
                }
            )
    headlines = [
        models.FinViz(**headline)
        for headline in added_headlines
    ]
    db.add_all(headlines)
    db.commit()
    return headlines


# Tweepy Operations:
def get_tweets(db):
    tweets = db.query(models.Tweets).order_by(
        models.Tweets.date_posted.desc()
    ).all()
    return models.Tweets.from_orm(tweets)


def add_twitter(db, tickers: List[str]):
    added_tweets = []

    for ticker in tickers:
        twitter_results = twitter_scraper(ticker)
        for tweet in twitter_results:
            try:
                date = datetime.strptime(
                    tweet['created_at'],
                    '%Y-%m-%dT%H:%M:%S.%fZ',
                )
            except ValueError:
                now = datetime.today().strftime('%b-%d-%y')
                date = datetime.strptime(
                    f'{now} {tweet["created_at"]}',
                    '%b-%d-%y  %H:%M%p',
                )

            added_tweets.append(
                {
                    'text': tweet['text'],
                    'sentiment': tweet['sentiment'],
                    'ticker': ticker,
                    'date_posted': date,
                    'date_created': datetime.today(),
                }
            )
    formatted_tweets = [
        models.Tweets(**tweet)
        for tweet in added_tweets
    ]
    db.add_all(formatted_tweets)
    db.commit()
    return added_tweets
