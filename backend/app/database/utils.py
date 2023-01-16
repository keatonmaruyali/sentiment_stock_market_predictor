import pandas as pd

from backend.app.services import finviz_scraper, twitter_scraper


def merge_headlines_and_tweets(headlines, tweets):
    intervaled_tweets = twitter_scraper.generate_interval_timeseries(tweets)
    intervaled_headlines = finviz_scraper.generate_interval_timeseries(headlines)
    return (
        pd.merge(
            intervaled_tweets,
            intervaled_headlines,
            on='date_posted',
            how='outer'
        ).fillna(0)
    )
