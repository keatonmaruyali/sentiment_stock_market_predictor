from datetime import date, datetime
from typing import List
from sqlalchemy.exc import IntegrityError
import pandas as pd

from backend.app.models import models
from backend.app.services import finviz_scraper, twitter_scraper
from backend.app.database.utils import merge_headlines_and_tweets


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


# Headline and Tweepy Operations:
def get_analysis(db):
    analysis_data = db.query(models.ModelTrainingData).order_by(
        models.ModelTrainingData.date_posted.desc()
    ).all()
    return models.ModelTrainingData.from_orm(analysis_data)


def process_headlines_and_tweets(db):
    all_tweets = get_tweets(db)
    all_tweets_df = pd.DataFrame(
        all_tweets,
        columns=[
            'text',
            'sentiment',
            'ticker',
            'date_posted',
            'date_created',
        ],
    )
    all_headlines = get_headlines(db)
    all_headlines_df = pd.DataFrame(
        all_headlines,
        columns=[
            'news_headline',
            'sentiment',
            'ticker',
            'date_posted',
            'date_created',
        ],
    )

    merged_data = merge_headlines_and_tweets(
        headlines=all_headlines_df,
        tweets=all_tweets_df,
    )

    formatted_merged_data = [
        models.ModelTrainingData(**row)
        for row in merged_data.to_dict('records')
    ]
    db.add_all(formatted_merged_data)
    db.commit()
    return merged_data.to_dict('records')


def search_sec_ticker(db, ticker: str):
    return db.query(models.SECStatementTracker).filter(
        models.SECStatementTracker.ticker == ticker
    ).one_or_none()


def add_sec_ticker(db, ticker, start_date):
    new_sec_stmt = models.SECStatementTracker(
        **{
            'ticker': ticker,
            'start_date': start_date,
            'end_date': datetime.today(),
        }
    )
    db.add(new_sec_stmt)
    db.commit()


def update_sec_ticker(db, ticker, update_values):
    # TODO: add lock
    db.query(models.SECStatementTracker).filter(
        models.SECStatementTracker.ticker == ticker
    ).update(update_values, synchronize_session=False)
