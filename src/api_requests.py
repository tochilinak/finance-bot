import requests
import json
import config


def moex_cost(symbol):
    query = ("https://iss.moex.com/iss/engines/stock/markets/shares"
             "/boards/TQBR/securities.json?securities.columns=SECID,"
             "PREVADMITTEDQUOTE&iss.meta=off&iss.only=securities")
    resp = requests.get(query).json()
    result = next((x[1] for x in resp['securities']['data']
                  if x[0] == symbol), None)
    return result


def marketstack_cost(symbol):
    query = "http://api.marketstack.com/v1/tickers/" + symbol +\
            "/intraday/latest"
    params = {"access_key": config.API_KEY_MARKETSTACK}
    r = requests.get(query, params=params).json()
    result = r["close"] if "close" in r.keys() else None
    return result


def moex_symbol_by_name(name):
    query = ("https://iss.moex.com/iss/securities.json?q=" + name
             + "&securities.columns=name,secid,group&iss.meta=off")
    resp = requests.get(query).json()
    only_stock = filter(lambda x: x[2] == "stock_shares" and
                        x[1].isupper(), resp['securities']['data'])
    return [x[:2] for x in only_stock]


def alphavantage_symbol_by_name(name):
    query = "https://www.alphavantage.co/query"
    params = {"function": "SYMBOL_SEARCH", "keywords": name, "apikey":
              config.API_KEY_ALPHAVANTAGE}
    r = requests.get(query, params=params).json()["bestMatches"]
    result = r[0]["1. symbol"] if len(r) > 0 else None
    return result


def current_cost(symbol):
    marketstack_result = marketstack_cost(symbol)
    if marketstack_result is not None:
        return marketstack_result

    return moex_cost(symbol)
