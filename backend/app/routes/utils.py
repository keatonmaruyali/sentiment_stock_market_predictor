from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from backend.app.database import crud
from backend.app.services import (
    sec_stat_downloader,
    fund_analysis,
)


def download_statements(
    ticker: str,
    start_date: str,
    end_date: str = date.today().strftime('%Y-%m-%d')
):
    sec_stat_downloader(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )


def get_sec_statements(ticker: str):
    filepaths = sec_stat_downloader.get_file_paths(ticker=ticker.upper())
    return fund_analysis.scrape(urls=filepaths)


def get_all_state_figures(sec_statements):
    return fund_analysis.generate_all_state_figs(
        all_statements=sec_statements
    )


def format_html_figures(all_stmt_figs: dict):
    all_figs = []
    for key, value in all_stmt_figs.items():
        stmt_figs = [f'<h1> {key.capitalize()} </h1>']
        stmt_figs.append(
            '<div> <img src="data:image/png;base64,'
            f'{str(value[key])}"/> <div/>'
        )
        all_figs.append(' '.join(stmt_figs))

    with open("/backend/app/templates/sec_results.html", "w") as file:
        file.write('''{% extends 'base.html' %}
            {% block content %}
                ''' + ' '.join(all_figs) + '''
        {% endblock %}''')


def check_sec_stmts(db, search_ticker, input_start_date):
    ''' Business logic for downloading SEC statements. '''
    query_results = crud.search_sec_ticker(
        db,
        ticker=search_ticker,
    )

    input_start_date = datetime.strptime(
        input_start_date,
        "%Y-%m-%d",
    )

    if query_results:
        _check_sec_download_date(
            db=db,
            ticker=search_ticker,
            input_start_date=input_start_date,
            query_results=query_results,
        )
    else:
        # new_sec_ticker = crud.add_sec_ticker(
        #     db=db,
        #     ticker=search_ticker,
        #     start_date=input_start_date,
        # )
        download_statements(
            ticker=search_ticker,
            start_date=datetime.strftime(
                input_start_date,
                "%Y-%m-%d",
            ),
        )
        # return new_sec_ticker


def _check_sec_download_date(
    db,
    ticker,
    input_start_date,
    query_results,
):
    # input_start_date = datetime.strptime(
    #     input_start_date,
    #     "%Y-%m-%d",
    # )
    next_quarter = query_results.end_date + relativedelta(
        years=2,
        months=6,
    )

    if query_results.start_date > input_start_date:
        download_statements(
            ticker=ticker,
            start_date=datetime.strftime(
                input_start_date,
                "%Y-%m-%d",
            ),
            end_date=datetime.strftime(
                query_results.start_date,
                "%Y-%m-%d",
            ),
        )
        crud.update_sec_ticker(
            db,
            ticker=ticker,
            update_values={'start_date': input_start_date},
        )

    if next_quarter < datetime.today():
        download_statements(
            ticker=ticker,
            start_date=datetime.strftime(
                query_results.end_date,
                "%Y-%m-%d",
            ),
        )
        crud.update_sec_ticker(
            db,
            ticker=ticker,
            update_values={'end_date': next_quarter},
        )
