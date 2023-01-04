import tweepy
import re
from datetime import timedelta, datetime

from backend.app.services.sentimentService import VaderSentimentService
from backend.app.services.utils import calc_sentiment_change
from backend.app.environment import TWITTER_BEARER_TOKEN


class TwitterScraper:
    def __init__(self):
        self.bearer_token = TWITTER_BEARER_TOKEN
        self.vader_sentiment = VaderSentimentService()

    def __call__(
        self,
        hashtag_phrase: str,
        start_date=datetime.now()-timedelta(days=2),
        end_date=datetime.now()-timedelta(days=1),
        max_results=100,
    ):
        format_hashtag = f'\${hashtag_phrase}'

        api = tweepy.Client(bearer_token=self.bearer_token)

        scraped_tweets = api.search_recent_tweets(
            query=format_hashtag,
            expansions=['author_id'],
            tweet_fields=['author_id', 'created_at', 'text', 'lang'],
            user_fields=['name', 'username', 'verified'],
            max_results=max_results,
            start_time=start_date,
            end_time=end_date,
        )

        augmented_tweets = []
        for tweet in scraped_tweets.data:
            cleaned_text = self._clean_tweets(tweet.data['text'])
            augmented_tweets.append(
                {
                    'created_at': tweet.data['created_at'],
                    'text': cleaned_text,
                    'sentiment': self.vader_sentiment(tweet.data['text'])
                }
            )
        return augmented_tweets

    def _remove_pattern(self, input_txt, pattern):
        matches = re.findall(pattern, input_txt)
        for match in matches:
            input_txt = re.sub(match, '', input_txt)
        return input_txt

    def _clean_tweets(self, tweets):
        tweets = self._remove_pattern(tweets, "RT @[\w]*:")
        tweets = self._remove_pattern(tweets, "@[\w]*")
        tweets = self._remove_pattern(tweets, "https?://[A-Za-z0-9./]*")
        # tweets = np.core.defchararray.replace(tweets, "[^a-zA-Z]", " ")
        return str(tweets)

    def generate_interval_timeseries(self, data):
        data.drop_duplicates(subset='text', keep=False, inplace=True)
        data.drop(
            ['ticker', 'date_created', 'text'],
            axis=1,
            inplace=True,
        )
        data.set_index('date_posted', inplace=True)

        intervaled_data = data.resample('30min').mean().ffill()\
            .reset_index('date_posted')

        tweet_sma = intervaled_data['sentiment'].rolling(3).mean()
        intervaled_data['sma3_sentiment_tweets'] = tweet_sma

        change_in_sent = calc_sentiment_change(intervaled_data['sentiment'])
        intervaled_data['tweet_sentiment_change'] = change_in_sent

        intervaled_data[
            'tweet_sentiment_change_t1'
        ] = intervaled_data['tweet_sentiment_change'].shift(1)

        intervaled_data.rename(
            columns={'sentiment': 'tweet_sentiment'},
            inplace=True,
        )
        return intervaled_data
