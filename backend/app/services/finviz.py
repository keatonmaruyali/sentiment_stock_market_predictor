from urllib.request import urlopen, Request
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import pandas as pd

from backend.app.services.sentimentService import VaderSentimentService
from backend.app.services.utils import calc_sentiment_change
from backend.app.environment import FINVIZ_URL


class NewsHeadlineScraper:
    def __init__(self):
        self.finviz_url = urlparse(FINVIZ_URL)
        self.vader_sentiment = VaderSentimentService()

    def __call__(self, ticker: str):
        url = self.finviz_url._replace(query=f't={ticker}')
        req = Request(
            url=urlunparse(url),
            headers={'user-agent': 'Mozilla/5.0'},
        )
        response = urlopen(req).read()

        html = BeautifulSoup(response, "html.parser")
        news = pd.read_html(
            str(html),
            attrs={'class': 'fullview-news-outer'},
        )[0]
        news.columns = ['date', 'news_headline']

        news['sentiment'] = news['news_headline'].map(
            lambda x: self.vader_sentiment(x)
        )
        return news

    def generate_interval_timeseries(self, data):
        data.drop_duplicates(subset='news_headline', keep=False, inplace=True)
        data.drop(
            ['ticker', 'news_headline', 'date_created'],
            axis=1,
            inplace=True,
        )
        data.set_index('date_posted', inplace=True)

        intervaled_data = data.resample('30min').mean().ffill()\
            .reset_index('date_posted')

        headline_sma = intervaled_data['sentiment'].rolling(3).mean()
        intervaled_data['sma3_sentiment_headlines'] = headline_sma

        change_in_sent = calc_sentiment_change(intervaled_data['sentiment'])
        intervaled_data['headline_sentiment_change'] = change_in_sent
        intervaled_data[
            'headline_sentiment_change_t1'
        ] = intervaled_data['headline_sentiment_change'].shift(1)

        intervaled_data.rename(
            columns={'sentiment': 'headline_sentiment'},
            inplace=True,
        )
        return intervaled_data
