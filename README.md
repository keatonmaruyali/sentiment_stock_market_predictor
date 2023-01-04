<div align="center">
  <h3 align="center">Stock Market Predictor</h3>

  <p align="center">
    My Capstone project from my Lighthouse Labs Data Science Bootcamp, completed in 2020.
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Setup</a></li>
      </ul>
    </li>
    <li><a href="#notes">Notes</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This is a project I completed after a 3-month data science bootcamp in 2020. This was the
very first instance of seeing code. I had 2 weeks to come up with an idea, then execute it.
This project attemps to use historical stock prices with sentiment analysis on news and tweets, to predict stock prices.


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* Flask
* VaderSentiment
* Tweepy
* yfinance

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This project, being Flask-based, is very simple to start. Version 1 was a simple as running
a `flask run` variant. Version 2 has the application Dockerized for ease.

### Prerequisites

Since Version 2 has been Dockerized, you will need to ensure you have Docker installed.
Depending on your OS, installation will be different.

This application does use the Twitter API to fetch tweets that mention stocks of interest,
so you will need to create a Twitter developer account to get a Bearer Token, which you
will add to the environment variables.

### Setup

1. Clone repo and enter directory.

2. Create a copy of the `.env.template` file. If you want, you can change them to whatever
you want. Be sure you've added your Twitter Bearer Token.

3. Build the Docker images
   ```
   docker compose build
   ```

4. Startup Docker containers.
   ```
   docker compose up -d
   ```

5. Visit `localhost:5000`.

6. To shut everything down, simply run
   ```
   docker compose down -v
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Notes

### Data Scraping

To run Airflow, the `setup` DAG needs to first be toggled as `active`, then run, to create
the Airflow variables and connections. There will be an error displayed in red at the top
of the Airflow dashboard until this step is completed. Once run, refresh the page and the
`data_scraping` DAG should appear. Now, you can toggle it, and run it.

The Twitter developer API has rate limits, meaning there is a limit to the number of tweets
a single bearer token can fetch. It is set at 2 million tweets per month, which depending on
what ticker symbols you use, may not be much. By default, I have set the `start_time` for
the query, to be one day back. If no value is provided to the endpoint, it will default to
7 days back.


### Analysis

Due to the little data I have tested with, I have manually set the interval window for data
to 30-minute intervals. This can certainly change with increasing data volume.

Since there are much more tweets, compared to news headlines, there are large portions of
data intervals where news headlines have a `sentiment = 0`. When merging the headline and 
tweet data, I perform an outer join on the tweet data, then fill in the missing data with
a value of 0 for the sentiment. This is a product of the incredibly short timeframe.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

Code Cleanup
- [x] Convert to OOP.
- [x] Add PostgreSQL database to Flask.
- [x] Better organization and structure.
- [x] Persist DB data locally.
- [x] Dockerize everything.

Data Scraping
- [x] Automate data scraping.
  - [x] Add Airflow.
  - [x] Before running scheduled scraping job, sync list of ticker symbols.
- [ ] Allow for users to view and edit list of ticker symbols.
  - [x] Create HTML page and input box.
  - [x] When editing, push to PG table and updage Airflow variables.
  - [x] Viewing will pull from PG table.
  - [x] Running job will pull from Airflow variables.
  - [ ] Allow user to delete/deactivate ticker.
- [ ] Allow users to manually trigger the scraping.
  - [ ] Keep track of time of last scraping job. Manually triggering should use
  this value as `start_time`.
- [ ] Prevent duplicate data.
  - [ ] Should it be upon adding to the DB that we check or also a scheduled job?
- [x] Allow for bulk operations.

Data Processing
- [x] Process data to be used for ML model training.
  - [x] Create new endpoints and supporting functions.
  - [x] Create new table.
- [ ] Allow user to input time-interval.
- [ ] What happens to old data when new time-interval is required?
  - [ ] One table per interval?
  - [ ] One master table, but interval window as a feature?

Machine Learning
- [ ] ML model training.
- [ ] Automated evaluation and training.
- [ ] Better UX.

Improvements
- [ ] Migrations.
- [ ] Input validation.
- [ ] Login.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Keaton Maruya-Li - keatonmaruyali@gmail.com


<p align="right">(<a href="#readme-top">back to top</a>)</p>
