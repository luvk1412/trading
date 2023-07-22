import pandas as pd
import yfinance as yf
from pandas_datareader import DataReader

def get_nifty_constituents():
    url = 'https://www1.nseindia.com/content/indices/ind_nifty500list.csv'
    const = pd.read_csv(url)
    return const

def download_data(stocks, start_date='2015-01-01', end_date='2020-12-31'):
    data = yf.download(stocks, start=start_date, end=end_date)
    return data['Close']

def compute_momentum(prices, lookback_period):
    return prices.pct_change(lookback_period).shift()

def backtest(data, lookback_period=60, rebalance_freq='W'):
    momentum = compute_momentum(data, lookback_period)

    # Create a DataFrame to hold our portfolio
    portfolio = pd.DataFrame(index=data.index)
    
    for date in data.index[::rebalance_freq]:
        # Get the momentum for this date
        mom = momentum.loc[date]

        # Drop any stocks that don't have a momentum value
        mom = mom.dropna()

        # Separate into winners and losers
        winners = mom[mom > mom.median()]
        
        # Assign weights
        portfolio.loc[date, winners.index] = 1 / len(winners)
    
    portfolio.fillna(0, inplace=True)
    
    # Calculate returns
    returns = (portfolio.shift() * data.pct_change()).sum(axis=1)
    
    return returns

if __name__ == "__main__":
    nifty_const = get_nifty_constituents()

    # Choose either 'SMALLCAP', 'MIDCAP', 'LARGECAP'
    capitalization = 'LARGECAP'

    if capitalization == 'LARGECAP':
        stocks = nifty_const.sort_values('MARKET CAPITALISATION IN RS. CR.')[-150:].SYMBOL.to_list()
    elif capitalization == 'MIDCAP':
        stocks = nifty_const.sort_values('MARKET CAPITALISATION IN RS. CR.')[-300:-150].SYMBOL.to_list()
    elif capitalization == 'SMALLCAP':
        stocks = nifty_const.sort_values('MARKET CAPITALISATION IN RS. CR.')[:150].SYMBOL.to_list()
    else:
        stocks = nifty_const.SYMBOL.to_list() 

    data = download_data(stocks)
    returns = backtest(data)
    print('Strategy return: ', returns.sum())
