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
    query = "http://api.marketstack.com/v1/tickers/" + symbol + "/intraday/latest"
    params = {"access_key": config.API_KEY_MARKETSTACK}
    r = requests.get(query, params=params)
    result = r.json()["close"] if isinstance(r.json(), dict) and "close" in r.json().keys() else None
    return result


def moex_symbol_by_name(name):
    query = ("https://iss.moex.com/iss/securities.json?q=" + name
             + "&securities.columns=name,secid,group&iss.meta=off")
    resp = requests.get(query).json()
    only_stock = filter(lambda x: x[2] == "stock_shares" and
                        x[1].isupper(), resp['securities']['data'])
    return [x[:2] for x in only_stock]
