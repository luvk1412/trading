import pandas as pd
import yfinance as yf
from pandas_datareader import DataReader

large_cap_threshold = int(20_000e7)
mid_cap_threshold = int(50_000e7)


def get_nifty_constituents():
    url = 'https://archives.nseindia.com/content/indices/ind_nifty500list.csv'
    nifty_const = pd.read_csv(url)
    nifty_const['Symbol'] = nifty_const['Symbol'].apply(lambda x: x + '.NS')
    return nifty_const


def download_data(stocks, start_date='2015-01-01', end_date='2020-12-31'):
    data = yf.download(stocks, start=start_date, end=end_date)
    return data['Close']


def compute_momentum(prices, lookback_period):
    return prices.pct_change(lookback_period).shift()


def get_stocks(capitalization=None):
    if capitalization is None:
        stocks = nifty_const.Symbol.to_list()
    elif capitalization == 'LARGECAP':
        stocks = nifty_const.sort_values('MarketCap')[-150:].Symbol.to_list()
    elif capitalization == 'MIDCAP':
        stocks = nifty_const.sort_values(
            'MarketCap')[-300:-150].Symbol.to_list()
    elif capitalization == 'SMALLCAP':
        stocks = nifty_const.sort_values('MarketCap')[:150].Symbol.to_list()
    return stocks


def backtest(data, lookback_period=60, rebalance_freq='W-TUE'):
    momentum = compute_momentum(data, lookback_period)

    # convert to date column to datetime, else  .loc on rebalanced dates wont work
    momentum.index = pd.to_datetime(momentum.index)

    # Create a DataFrame to hold our portfolio
    portfolio = pd.DataFrame(index=data.index)

    rebalance_dates = pd.date_range(
        start=data.index.min(), end=data.index.max(), freq=rebalance_freq)

    for date in rebalance_dates:
        if date in momentum.index:
            # Get the momentum for this date
            mom = momentum.loc[date]

            # Drop any stocks that don't have a momentum value
            mom = mom.dropna()

            # Separate into winners and losers
            # winners = mom[mom > mom.median()]

            # chose top 50
            mom = mom.sort_values(ascending=False)

            # # Select top 50 stocks
            winners = mom.head(50)

            # Assign weights
            portfolio.loc[date, winners.index] = 1 / len(winners)

    portfolio.fillna(0, inplace=True)

    # Calculate returns
    returns = (portfolio * data.pct_change()).sum(axis=1)

    return returns


if __name__ == "__main__":
    nifty_const = get_nifty_constituents()

    # Choose either 'SMALLCAP', 'MIDCAP', 'LARGECAP'
    capitalization = 'LARGECAP'

    if capitalization == 'LARGECAP':
        stocks = nifty_const.sort_values(
            'MARKET CAPITALISATION IN RS. CR.')[-150:].SYMBOL.to_list()
    elif capitalization == 'MIDCAP':
        stocks = nifty_const.sort_values(
            'MARKET CAPITALISATION IN RS. CR.')[-300:-150].SYMBOL.to_list()
    elif capitalization == 'SMALLCAP':
        stocks = nifty_const.sort_values('MARKET CAPITALISATION IN RS. CR.')[
            :150].SYMBOL.to_list()
    else:
        stocks = nifty_const.SYMBOL.to_list()

    data = download_data(stocks)
    returns = backtest(data)
    print('Strategy return: ', returns.sum())
