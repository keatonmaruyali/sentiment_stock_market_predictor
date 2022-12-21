-- Creation of product table
CREATE TABLE finviz (
  id serial PRIMARY KEY,
  news_headline varchar (300) NOT NULL,
  date_posted date NOT NULL,
  sentiment float NOT NULL,
  date_created date DEFAULT CURRENT_TIMESTAMP
);

-- Creation of order_status table
CREATE TABLE tweets (
  id serial PRIMARY KEY,
  text varchar (300) NOT NULL,
  date_posted date NOT NULL,
  sentiment float NOT NULL,
  date_created date DEFAULT CURRENT_TIMESTAMP
);
