import yfinance as yf
from datetime import date, timedelta


class YahooStockData:
    def __call__(
        self,
        ticker_symbol: str,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        interval='30m'
    ):
        # 1. Request data:
        data = yf.download(
            ticker_symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
        )
        # 2. Feature Engineering:
        data['Percent Price Change Within Period'] = self._price_change_within_period(
            open_price=data['Open'],
            close_price=data['Close'],
        )
        # data['Change in Close Price'] = data['Close'] - data['Close'].shift(1)
        # data['Scaled Delta Close'] = data['Change in Close Price']/(data['Close'].mean())
        data['Scaled Volume'] = data['Volume']/data['Volume'].mean()
        data_SMA = data['Adj Close'].rolling(window=3).mean().shift(1)
        data['SMA(3)'] = data_SMA
        data['t+1'] = data['Adj Close'].shift(-1)
        data.reset_index(inplace=True)
        data['Datetime'] = self._adjust_datetime(data['Datetime'])
        data.drop(['Open','High','Low','Close'],axis=1,inplace=True)
        #3. Export data:
        # f_name = ticker_symbol + "_data"
        # data.to_csv('~/LighthouseLabs-Final/Dataset/1. Stock_Data/' + f_name + ".csv")
        # print('Data saved!')
        return data

    def _price_change_within_period(self, open_price, close_price):
        price_change = ((close_price - open_price)/open_price)*100
        return price_change

    def _adjust_datetime(self, datetime):
        adj_datetime = datetime.dt.tz_convert(
            'America/Montreal'
        ).dt.tz_localize(None)
        return adj_datetime
