import pandas as pd
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import yfinance as yf
import datetime as dt
import numpy as np

def get_prices():
    assets = ['BTC', 'ETH', 'ADA', 'BNB', 'XRP', 'SOL1', 'DOT1', 'DOGE']
    all_assets = {}

    for coin in assets:
        data = yf.Ticker("{}-USD".format(coin))
        df = data.history(period="max")
        df['Symbols'] = coin
        all_assets[coin] = df

    for coin in all_assets:
        if coin == 'BTC':
            results = all_assets[coin]
        else:
            data = all_assets[coin]
            results =pd.concat([results, data])

    results['unix'] = [int(dt.datetime(x.year, x.month, x.day).timestamp()) for x in results.index]
    results['Symbols'] = results['Symbols'].str.replace('1', '')
    return results.sort_index()

def get_ticker(df):
    prices = df.reset_index(drop=False).sort_values(['Date', 'Symbols'])
    current = prices[prices['Date'] == prices['Date'].iloc[-1]].reset_index()
    prev = prices[prices['Date'] == prices['Date'].iloc[-9]].reset_index()
    current['24_chng'] = ((current['Open'] - prev['Open']) / prev['Open']) * 100
    current['24_chng'] = current['24_chng'].apply(
        lambda x: "{:.1f}%    24-hr".format(x) if x < 0 else "+{:.1f}%    24-hr".format(x))
    current['Open'] = current['Open'].apply(lambda x: "${:,.1f}".format(x))
    current['color'] = current['24_chng'].apply(lambda x: 'red' if x[0] == '-' else 'green')
    prices = current[['Symbols', 'Open', '24_chng']].T
    prices.columns = prices.iloc[0]
    prices = prices.iloc[1:, :]
    return prices, current

def get_dom():
    key = 'd174938c-d8e4-46de-afb6-eb23aeea5c16'

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
      'limit':10
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': key,
    }

    session = Session()
    session.headers.update(headers)

    try:
      response = session.get(url, params=parameters)
      data = json.loads(response.text)
      print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e)

    coins = pd.DataFrame(data['data'])
    coins['mrkt_dom'] = [x['USD']['market_cap_dominance'] for x in coins['quote']]
    dom = coins[['symbol', 'mrkt_dom']]
    top_dom = dom['mrkt_dom'].sum()
    others = pd.DataFrame(['Other', 100-top_dom]).T
    others.columns = dom.columns
    dom = pd.concat([dom, others], ignore_index=True)
    return dom

def get_cycles():
    #import historic data
    BTC = pd.read_csv('historic_btc')

    # request new data and rename to match historic data
    data = yf.Ticker("{}-USD".format('BTC'))
    df = data.history(period="max").reset_index(drop=False)
    df = df[['Open', 'Date']].rename(columns={'Open': 'price', 'Date': 'time'})

    # isolate cycle 4 time series and concat with historic
    day1 = dt.datetime(2020, 5, 11)
    new = df[df['time'] >= day1]
    BTC = pd.concat([BTC, new]).reset_index(drop=True)
    BTC['time'] = pd.to_datetime(BTC['time'])

    # enter halvings dates
    halvings = pd.Series(['2009-1-3', '2012-11-28', '2016-7-9', '2020-5-11', BTC['time'].iloc[-1]])
    halvings = pd.to_datetime(halvings)

    # Create days since halving and cycle feature columns
    days = pd.Series()
    cycles = pd.Series()
    for i in range(len(halvings) - 1):
        start = halvings[i]
        end = halvings[i + 1]
        mask = (BTC['time'] >= start) & (BTC['time'] <= end)
        days_since = BTC[mask]['time'].apply(lambda x: (x - start))
        days = pd.concat([days, days_since], ignore_index=True)
        cycle = BTC[mask]['time'].apply(lambda x: i + 1)
        cycles = pd.concat([cycles, cycle], ignore_index=True)
    BTC['days_since_halving'] = days.astype(str)
    BTC['days_since_halving'] = BTC['days_since_halving'].str.replace('days', '').astype(int)
    BTC['cycle'] = cycles.astype(str)
    cycles = {}
    for cycle in BTC['cycle'].unique():
        data = BTC[BTC['cycle'] == cycle].copy()
        bottom = data['price'].iloc[0]
        data['por_increase'] = BTC['price'].apply(lambda x: x / bottom)
        data['por_increase'] = data['por_increase']
        if cycle == '1':
            results = data
        else:
            results = pd.concat([results, data])
    return results.iloc[:, 1:]

