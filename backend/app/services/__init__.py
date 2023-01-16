from .finviz import NewsHeadlineScraper
from .twitter_scraping import TwitterScraper
from .fundamental_analysis import FundamentalAnalysis
from .sec_downloader import SECDownloader

finviz_scraper = NewsHeadlineScraper()
twitter_scraper = TwitterScraper()
fund_analysis = FundamentalAnalysis()
sec_stat_downloader = SECDownloader()
