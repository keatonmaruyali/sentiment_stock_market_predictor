from flask import request, render_template, redirect, url_for
from flask import current_app as app
import re

from backend.app.database import crud
from backend.app.database.database import get_db_conn
from backend.app.routes.utils import (
    _download_statements,
    get_sec_statements,
    get_all_state_figures,
)


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


@app.route("/analysis", methods=['GET', 'POST'])
def analysis(db=get_db_conn()):
    if request.method == 'GET':
        analysis_data = crud.get_analysis(db)
        return render_template("analysis.html", data=analysis_data)

    elif request.method == 'POST':
        analysis_data = crud.process_headlines_and_tweets(db)
        return render_template("analysis.html", data=analysis_data)


@app.route("/sec_statements", methods=['GET', 'POST'])
def sec_statements():
    if request.method == 'GET':
        return render_template("sec_statements.html")

    if request.method == 'POST':
        search_ticker = request.form['search-company'].upper()
        search_ticker = re.split(r',|\s', search_ticker)
        return redirect(url_for('sec_results', ticker=search_ticker))


@app.route("/sec_results/<ticker>", methods=['GET'])
def sec_results(ticker):
    if request.method == 'GET':
        # print(f'Ticker: {ticker}')
        sec_statements = get_sec_statements(ticker=ticker)
        balance_sheet_fig = get_all_state_figures(
            sec_statements=sec_statements
        )
        # print(f'Fig res: {len(balance_sheet_fig["balance"])}')
        all_figs = []
        for key, value in balance_sheet_fig.items():
            stmt_figs = [f'<h1> {key.capitalize()} </h1>']
            stmt_figs.append(
                '<div> <img src="data:image/png;base64,'
                f'{str(value[key])}"/> <div/>'
            )
            all_figs.append(' '.join(stmt_figs))

        # print(f'All Figs: {list(balance_sheet_fig.keys())}')
        with open("/backend/app/templates/sec_results.html", "w") as file:
            file.write('''{% extends 'base.html' %}
            {% block content %}
                ''' + ' '.join(all_figs) + '''
            {% endblock %}''')
        return render_template("sec_results.html")
    elif request.method == 'POST':
        _download_statements(ticker)
        return render_template("sec_results.html")

