from datetime import date,timedelta
import json
import csv
import tweepy
import re
from datetime import datetime

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pickle
import yfinance as yf
import numpy as np

# 1. Retrieve Historical Stock Data:
def get_stock(ticker):
    end_date=date.today()+timedelta(days=1)
    start_date=date.today()-timedelta(days=1)
    # 1.1 Request data:
    stock_data = yf.download(ticker, 
                      start=start_date, 
                      end=end_date,
                      interval='30m', 
                      progress=False)
    # 1.2 Feature Engineering:
    stock_data['Percent Price Change Within Period'] = ((stock_data['Close'] - stock_data['Open'])/stock_data['Open'])*100
    stock_data['Scaled Volume'] = stock_data['Volume']/stock_data['Volume'].mean()
    data_SMA = stock_data['Adj Close'].rolling(window=3).mean().shift(1)
    stock_data['SMA(3)'] = data_SMA
    stock_data.drop(['Open','High','Low','Close'],axis=1,inplace=True)
    stock_data.reset_index(inplace=True)
    stock_data['Datetime']=stock_data['Datetime'].dt.tz_convert('America/Montreal').dt.tz_localize(None)
    return stock_data
def get_news(ticker_code):
# 2.1 Define URL:
    finwiz_url = 'https://finviz.com/quote.ashx?t='
# 2.2 Requesting data:
    news_tables = {}
    tickers = [ticker_code]
    for ticker in tickers:
        url = finwiz_url + ticker
        req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
        response = urlopen(req)    
        # Read the contents of the file into 'html'
        html = BeautifulSoup(response,features="lxml")
        # Find 'news-table' in the Soup and load it into 'news_table'
        news_table = html.find(id='news-table')
        # Add the table to our dictionary
        news_tables[ticker] = news_table
# 2.3 Parsing news:
    parsed_news = []
    for file_name, news_table in news_tables.items():
        for x in news_table.findAll('tr'):
            text = x.a.get_text() 
            date_scrape = x.td.text.split()
            if len(date_scrape) == 1:
                time = date_scrape[0]
            else:
                date = date_scrape[0]
                time = date_scrape[1]
            ticker = file_name.split('_')[0]
            parsed_news.append([ticker, date, time, text])
# 2.4 Split into columns and save:
    vader = SentimentIntensityAnalyzer()
    columns = ['ticker', 'date', 'time', 'headline']
    processedHeadlines = pd.DataFrame(parsed_news, columns=columns)
    scores = processedHeadlines['headline'].apply(vader.polarity_scores).to_list()
    scores_df = pd.DataFrame(scores)
    processedHeadlines = processedHeadlines.join(scores_df, rsuffix='_right')
    processedHeadlines.insert(loc=1, column='timestamp', value=(pd.to_datetime(processedHeadlines['date'] + ' ' + processedHeadlines['time'])))
    processedHeadlines.drop(columns=['date','time'],axis=1,inplace=True)
    return processedHeadlines
# 3. Define Preprocessing Functions:
def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)       
    return input_txt
    
def clean_tweets(tweets):
    #remove twitter Return handles (RT @xxx:)
    tweets = np.vectorize(remove_pattern)(tweets, "RT @[\w]*:") 
    #remove twitter handles (@xxx)
    tweets = np.vectorize(remove_pattern)(tweets, "@[\w]*")
    #remove URL links (httpxxx)
    tweets = np.vectorize(remove_pattern)(tweets, "https?://[A-Za-z0-9./]*")
    #remove special characters, numbers, punctuations (except for #)
    tweets = np.core.defchararray.replace(tweets, "[^a-zA-Z]", " ")
    return tweets
# 4. Retrieve Tweets:
def get_tweets(hashtag_phrase):
    format_hashtag = '$'+hashtag_phrase
    # os.environ["consumer_key"] = "psxikKIcDvu19SDl1qbTycOHY"
    # os.environ["consumer_secret"] = "H2FV5HL4UyuzVUtANd0lo3HpsNzo1woDMuwlabVyv2E7g44SDb"
    # os.environ["twitter_access_token"] = "1265371572942102528-XZyshdLemub7C7hrx51dyFrYCBCmvU"
    # os.environ["twitter_access_secret"] = "CK4hmNukUYBhzr3CAtO3gvGFx7Ahr9TW3vZMjW6pl8yVd"

    os.environ["consumer_key"] = "4BSOA2XKS8vucCHyBjy502Aw8"
    os.environ["consumer_secret"] = "l27Zsdh9X9oGGff25gJ4PX9zN6ZnjYKonu2zISu17jsQlO5Dkb"
    os.environ["twitter_access_token"] = "1265371572942102528-IsosHWjrXRDKHaqQFAbSPuM2FyH41k"
    os.environ["twitter_access_secret"] = "pVjYFAx8pDCBnJE48NxsA4KB6g4eNMw39TOWcTciLOB5u"

    # os.environ["consumer_key"] = "dQXGlGv8YFtPrZvQwcCnvbged"
    # os.environ["consumer_secret"] = "ouKbQUg1dGubyKbp7DrNo45Qdv3nNzd7MyuvCgIKha0vpuNbDA"
    # os.environ["twitter_access_token"] = "1265371572942102528-Jmu9hvd4yBep0KwV9U5mHFUnyUi9JV"
    # os.environ["twitter_access_secret"] = "CYW3FRkyXJnSzRrHoN9FcLlBdSRHfA7GWJK1PMT7Q1S7P"

    # os.environ["consumer_key"] = "ljU1UWBCC0YNKlO9pwm1TshUc"
    # os.environ["consumer_secret"] = "w5CDP6fNeNQhvDs075KiZQEIWI7VY1Z8BxiDc5kUAHTsXzOhCY"
    # os.environ["twitter_access_token"] = "1309241898419322880-hBG39tjNql0FcHrjOMYg2qTN3TEtnw"
    # os.environ["twitter_access_secret"] = "p0UOsVpTB9hu15R3YBMbWGw2zDpJjkUCmK0YadzA894ZF"

    consumer_key = os.environ['consumer_key']
    consumer_secret = os.environ['consumer_secret']
    access_token = os.environ['twitter_access_token']
    access_token_secret = os.environ['twitter_access_secret']

    auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)

    api = tweepy.API(auth)
    while True:
        try:
            tweets = tweepy.Cursor(api.search, q=format_hashtag+' -filter:retweets', lang="en", tweet_mode='extended').items(1000)
            tweets_list = [[tweet.created_at, tweet.full_text.replace('\n',' ').encode('utf-8'), tweet.user.followers_count] for tweet in tweets]
            twitter_posts = pd.DataFrame(tweets_list, columns=['timestamp', 'tweet_text', 'followers_count'])
            break
        except tweepy.TweepError:
            break
        except StopIteration:
            break
    twitter_posts['tweet_text']=twitter_posts['tweet_text'].str.decode("utf-8")
    twitter_posts['scaled_followers_count'] =twitter_posts['followers_count']/twitter_posts['followers_count'].max()
# 4.1 Feature Engineering: Sentiment Analysis
    vader = SentimentIntensityAnalyzer()
    twitter_posts['tweet_text'] = clean_tweets(twitter_posts['tweet_text'])
    scores = twitter_posts['tweet_text'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)
    df = twitter_posts.join(scores_df, rsuffix='_right')
    df['compound'] = df['compound']*(df['scaled_followers_count']+1)
    return df
        
# 5. Shared Functions:
def calc_change_sentiment(data):
    change_in_sent = []
    change_in_sent.append(data['compound'][0])
    for i in range(1,len(data['compound'])):
        if data['compound'][i] == 0:
            change_in_sent.append(0)
        elif data['compound'][i] < 0 or data['compound'][i] > 0:
            dif = data['compound'][i] - data['compound'][(i-1)]
            change_in_sent.append(dif)
    return change_in_sent

def classify_news(dataframe):
    day1, day2 = [],[]
    for i in range(len(dataframe['timestamp'])):
        if dataframe['timestamp'][i].day == dataframe['timestamp'][i].day and (dataframe['timestamp'][i].hour <= 15 and dataframe['timestamp'][i].hour >= 9):
            day1.append(i)
        elif dataframe['timestamp'][i].day == dataframe['timestamp'][i].day+1 and (dataframe['timestamp'][i].hour <= 15 and dataframe['timestamp'][i].hour >= 9):
            day2.append(i)
        else:
            pass
    news_d1, news_d2 = dataframe.iloc[day1],dataframe.iloc[day2]
    return news_d1, news_d2
# 6. Preprocess Tweets:
def preprocess_posts(df):
    df.drop(['neg','neu','pos','followers_count'],axis=1,inplace=True)
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('America/Montreal').dt.tz_localize(None)
    df.set_index('timestamp', inplace=True)
    twitter_df_30m = df.resample('30min').median().ffill().reset_index()
    change_in_sent = calc_change_sentiment(twitter_df_30m)
    twitter_sma = twitter_df_30m['compound'].rolling(3).mean()
    twitter_df_30m['Compound SMA(3) Twitter'] = twitter_sma
    twitter_df_30m['change in sentiment twitter'] = change_in_sent
    twitter_df_30m['change in sentiment twitter (t-1)'] = twitter_df_30m['change in sentiment twitter'].shift(1)
    tweet_d1,tweet_d2 = classify_news(twitter_df_30m)
    tweet_d1_red,tweet_d2_red= tweet_d1.iloc[1:],tweet_d2.iloc[1:]
    frames = [tweet_d1_red,tweet_d2_red]
    processed_tweets = pd.concat(frames)
    return processed_tweets
# 7. Preprocess Headlines:
def preprocess_headlines(data):
    data.drop_duplicates(subset='headline',keep=False, inplace=True)
    data.drop(['ticker','neg','neu','pos'], axis=1, inplace=True)
    data.set_index('timestamp', inplace=True)
    data_30m = data.resample('30min').median().ffill().reset_index()
    change_in_sent=calc_change_sentiment(data_30m)
    headline_sma = data_30m['compound'].rolling(3).mean()
    data_30m['Compound SMA(3) Headlines'] = headline_sma
    data_30m['change in sentiment headlines'] = change_in_sent
    data_30m['change in sentiment headlines (t-1)'] = data_30m['change in sentiment headlines'].shift(1)
    news_d1, news_d2 = classify_news(data_30m)
    news_d1_red, news_d2_red = news_d1.iloc[1:],news_d2.iloc[1:]
    frames_news = [news_d1_red, news_d2_red]
    processed_headlines = pd.concat(frames_news)
    return processed_headlines

# 8. Retrieve, Process, and Merge:
def data_merge(ticker):
    stock_data = get_stock(ticker)
    headlines = get_news(ticker)
    tweets = get_tweets(ticker)
    processed_headlines = preprocess_headlines(headlines)
    processed_tweets = preprocess_posts(tweets)
    with_twitter_df = stock_data.merge(processed_tweets, left_on='Datetime', right_on='timestamp',how='left').ffill().drop('timestamp',axis=1)
    full_df = with_twitter_df.merge(processed_headlines, left_on='Datetime', right_on='timestamp',how='left').ffill().drop('timestamp',axis=1)
    full_df['Percent Price Change Within Period (t+1)'] = full_df['Percent Price Change Within Period'].shift(-1)
    return full_df
# 9. Import Model and Predict:
def make_prediction(ticker):
    dataframe = data_merge(ticker)
    x_var = ['Adj Close','Scaled Volume','compound_y','compound_x','Compound SMA(3) Headlines','Compound SMA(3) Twitter','SMA(3)','change in sentiment headlines','change in sentiment headlines (t-1)','change in sentiment twitter','change in sentiment twitter (t-1)']
    X_test = dataframe[x_var][-2:]
    loaded_model = pickle.load(open('finalized_xgb_model.sav', 'rb'))
    result = ((loaded_model.predict(X_test)/100) * dataframe['Adj Close'].iloc[-2]) + dataframe['Adj Close'].iloc[-2]
    previous_price = dataframe['Adj Close'].iloc[-2]
    if result[0] > previous_price:
        return (ticker.upper(),'The predicted close for {} within the next 30 minutes is ${}, up from ${}.'.format(ticker, "%.2f" % result[0],"%.2f" % previous_price))
    else:
        return (ticker.upper(),'The predicted close for {} within the next 30 minutes is ${}, down from ${}.'.format(ticker, "%.2f" % result[0],"%.2f" % previous_price))

# 10. Execute:
# if __name__ == '__main__':
#     while True:
#         ticker= input('Insert ticker symbol: ').upper()
#         print('Fetching Data...')
#         if ticker == 'EXIT':
#             print("Thank you, come again!")
#             break
#         else:
#             predict_price(ticker)



