from urllib.request import urlopen, Request
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import pandas as pd

from backend.app.services.sentimentService import VaderSentimentService
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
