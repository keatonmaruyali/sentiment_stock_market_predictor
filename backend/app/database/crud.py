from datetime import datetime

from app.models import models
from app.services import finviz_scraper, twitter_scraper


# FinViz Operations:
def get_headlines(db):
    headlines = db.query(models.FinViz).all()
    return models.FinViz.from_orm(headlines)


def add_headlines(db, ticker: str):
    scraper_results = finviz_scraper(ticker)
    added_headlines = []
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
                'date_posted': date,
                'news_headline': headline['news_headline'],
                'sentiment': headline['sentiment'],
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
    tweets = db.query(models.Tweets).all()
    return models.Tweets.from_orm(tweets)


def add_twitter(db, ticker: str):
    twitter_results = twitter_scraper(ticker)
    added_tweets = []
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
                'date_posted': date,
                'text': tweet['text'],
                'sentiment': tweet['sentiment'],
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
