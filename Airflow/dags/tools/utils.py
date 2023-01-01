import ast
from datetime import datetime
from typing import List

from tools.models import models
from .services import finviz_scraper, twitter_scraper
from .db import get_db_conn


def sync_tickers(
    airflow_tickers: List[str],
    db_tickers: List[str],
    db=get_db_conn()
):
    new_db_tickers = [
        {'ticker': ticker}
        for ticker in airflow_tickers
        if ticker not in db_tickers
    ]
    added_tickers = [
        models.TrackedTickers(**new_ticker)
        for new_ticker in new_db_tickers
    ]
    db.add_all(added_tickers)
    db.commit()

    new_airflow_tickers = [
        ticker
        for ticker in db_tickers
        if ticker not in airflow_tickers
    ]
    if len(new_airflow_tickers) != 0:
        new_airflow_tickers.extend(airflow_tickers)
    return new_airflow_tickers


def add_headlines(ticker_list: List[str], db=get_db_conn()):
    tickers = ast.literal_eval(ticker_list)
    tickers = [tick.strip() for tick in tickers]
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


def add_twitter(ticker_list: List[str],  db=get_db_conn()):
    tickers = ast.literal_eval(ticker_list)
    tickers = [tick.strip() for tick in tickers]
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
