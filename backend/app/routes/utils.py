from backend.app.services import (
    sec_stat_downloader,
    fund_analysis,
)


def _download_statements(ticker):
    sec_stat_downloader(
        ticker=ticker,
        start_date='2020-01-01',
    )


def get_sec_statements(ticker):
    filepaths = sec_stat_downloader.get_file_paths(ticker=ticker)
    return fund_analysis.scrape(urls=filepaths)


def get_all_state_figures(sec_statements):
    return fund_analysis.generate_all_state_figs(
        all_statements=sec_statements
    )
