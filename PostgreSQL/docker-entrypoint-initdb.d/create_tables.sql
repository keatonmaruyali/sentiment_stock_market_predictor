CREATE USER investor;
CREATE DATABASE stock_market;
GRANT ALL PRIVILEGES ON DATABASE stock_market TO investor;

\c stock_market

-- Creation of product table
CREATE TABLE finviz (
  id serial PRIMARY KEY,
  news_headline varchar (300) NOT NULL,
  sentiment float NOT NULL,
  ticker varchar(8) NOT NULL,
  date_posted timestamp NOT NULL,
  date_created timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Creation of order_status table
CREATE TABLE tweets (
  id serial PRIMARY KEY,
  text varchar (300) NOT NULL,
  sentiment float NOT NULL,
  ticker varchar(8) NOT NULL,
  date_posted timestamp NOT NULL,
  date_created timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Creation of tracked_tickers table
CREATE TABLE tracked_tickers (
  id serial PRIMARY KEY,
  ticker varchar(8) NOT NULL UNIQUE
);

-- Creation of model_training_data table
CREATE TABLE model_training_data (
  id serial PRIMARY KEY,
  date_posted timestamp NOT NULL,
  headline_sentiment float NOT NULL,
  headline_sentiment_change float NOT NULL,
  sma3_sentiment_headlines float NOT NULL,
  headline_sentiment_change_t1 float NOT NULL,
  tweet_sentiment float NOT NULL,
  tweet_sentiment_change float NOT NULL,
  sma3_sentiment_tweets float NOT NULL,
  tweet_sentiment_change_t1 float NOT NULL
)
