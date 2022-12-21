from flask import request, render_template
from flask import current_app as app

from app.database import crud
from app.database.database import get_db_conn


@app.route("/")
def main():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/finviz", methods=['GET', 'POST'])
def finviz(db=get_db_conn()):
    if request.method == 'GET':
        headlines = crud.get_headlines(db)
        return render_template("finviz.html", headlines=headlines)

    elif request.method == 'POST':
        ticker = request.get_json().get('ticker')
        headlines = crud.add_headlines(db, ticker)
        return render_template("finviz.html", headlines=headlines)


@app.route("/twitter", methods=['GET', 'POST'])
def twitter(db=get_db_conn()):
    if request.method == 'GET':
        tweets = crud.get_tweets(db)
        return render_template("tweet.html", tweets=tweets)

    elif request.method == 'POST':
        ticker = request.get_json().get('ticker')
        tweets = crud.add_twitter(db, ticker)
        return render_template("tweet.html", tweets=tweets)
