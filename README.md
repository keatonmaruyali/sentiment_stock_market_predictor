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



<!-- ROADMAP -->
## Roadmap

- [x] Convert to OOP.
- [x] Add PostgreSQL database to Flask.
- [x] Better organization and structure.
- [x] Persist DB data locally.
- [ ] Automate data scraping.
- [ ] ML model training.
- [ ] Automated evaluation and training.
- [ ] Better UX.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Keaton Maruya-Li - keatonmaruyali@gmail.com


<p align="right">(<a href="#readme-top">back to top</a>)</p>
