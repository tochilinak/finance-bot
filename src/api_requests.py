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


def moex_company_list():
    query = ("https://iss.moex.com/iss/engines/stock/markets/shares/"
             "boards/TQBR/securities.json?securities.columns=SECID&"
             "iss.meta=off&iss.only=securities")
    resp = requests.get(query).json()
    return [x[0] for x in resp['securities']['data']]


def marketstack_cost(symbol):
    query = "http://api.marketstack.com/v1/tickers/" + symbol +\
            "/intraday/latest"
    params = {"access_key": config.API_KEY_MARKETSTACK}
    r = requests.get(query, params=params).json()
    result = r["close"] if "close" in r.keys() else None
    return result


def moex_symbol_by_name(name):
    query = ("https://iss.moex.com/iss/securities.json?q=" + name
             + "&securities.columns=name,secid&iss.meta=off")
    resp = requests.get(query).json()
    company_list = moex_company_list()
    only_stock = filter(lambda x: x[1] in company_list,
                        resp['securities']['data'])
    return [x[:2] for x in only_stock]


def alphavantage_symbol_by_name(name):
    query = "https://www.alphavantage.co/query"
    params = {"function": "SYMBOL_SEARCH", "keywords": name, "apikey":
              config.API_KEY_ALPHAVANTAGE}
    r = requests.get(query, params=params).json()["bestMatches"]
    result = [[x["2. name"], x["1. symbol"]] for x in r]
    return result


def current_cost(symbol):
    """Find stock price by symbol.

    Returns None if not found
    """
    marketstack_result = marketstack_cost(symbol)
    if marketstack_result is not None:
        return marketstack_result
    return moex_cost(symbol)


def symbol_by_name(name, result_size=5):
    """Find symbol by company name using American and Russian api's.

    Returns list of pairs [full_name, symbol].
    result_size (default: 5) - maximum number of companies
    returned by one api
    """
    moex_result = moex_symbol_by_name(name)[:result_size]
    alphavantage_result = alphavantage_symbol_by_name(name)[:result_size]
    return moex_result + alphavantage_result
