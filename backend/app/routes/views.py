from flask import request, render_template, redirect, url_for
from flask import current_app as app
import re

from backend.app.database import crud
from backend.app.database.database import get_db_conn


@app.route("/")
def main():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/tickers", methods=['GET', 'POST'])
def tickers(db=get_db_conn()):
    if request.method == 'GET':
        tickers = crud.get_tickers(db)
        return render_template("tickers.html", tickers=tickers)

    if request.method == 'POST':
        new_tickers = request.form['new-ticker'].upper()
        new_tickers = re.split(r',|\s', new_tickers)

        if not isinstance(new_tickers, list):
            new_tickers = [new_tickers]

        crud.add_tickers(db, new_tickers)
        return redirect(url_for('tickers'))


@app.route("/finviz", methods=['GET', 'POST'])
def finviz(db=get_db_conn()):
    if request.method == 'GET':
        headlines = crud.get_headlines(db)
        return render_template("finviz.html", headlines=headlines)

    elif request.method == 'POST':
        tickers = request.get_json().get('tickers')
        headlines = crud.add_headlines(db, tickers)
        return render_template("finviz.html", headlines=headlines)


@app.route("/twitter", methods=['GET', 'POST'])
def twitter(db=get_db_conn()):
    if request.method == 'GET':
        tweets = crud.get_tweets(db)
        return render_template("tweet.html", tweets=tweets)

    elif request.method == 'POST':
        tickers = request.get_json().get('tickers')
        tweets = crud.add_twitter(db, tickers)
        return render_template("tweet.html", tweets=tweets)
