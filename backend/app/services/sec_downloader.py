import os
from sec_edgar_downloader import Downloader


class SECDownloader:
    def __init__(self):
        self.download_path = "/backend"

    def __call__(self, ticker, start_date):
        dl = Downloader()
        if self.download_path is not None:
            dl = Downloader(self.download_path)
        dl.get("10-Q", ticker.upper(), after=start_date, download_details=True)

    def get_file_paths(self, ticker):
        rootdir = f'/backend/sec-edgar-filings/{ticker.upper()}/10-Q'
        return [
            os.path.join(subdir, file)
            for subdir, _, files in os.walk(rootdir)
            for file in files
            if file == 'filing-details.html'
        ]
