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

def get_cycles(df):
    cycles = pd.read_csv('btc_cycles').iloc[:, 1:]
    cycles = cycles[cycles['cycle'] < 4]
    data = yf.Ticker("{}-USD".format('BTC'))
    df = data.history(period="max").reset_index(drop=False)

    day1 = dt.datetime(2020, 5, 11)
    new = df[df['Date'] >= day1]
    initial_price = new['Open'].iloc[0]
    num_days = len(new)
    new['cycle'] = 4
    new['days_since_halving'] = np.linspace(0, num_days, num=num_days).astype(int)
    new['por_increase'] = new['Open'] / initial_price

    new = new[cycles.columns]
    cycles = pd.concat([cycles, new]).reset_index(drop=True)
    return cycles
