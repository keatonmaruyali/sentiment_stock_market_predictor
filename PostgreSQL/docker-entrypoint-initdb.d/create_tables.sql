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

CREATE TABLE tracked_tickers (
  id serial PRIMARY KEY,
  ticker varchar(8) NOT NULL UNIQUE
);
