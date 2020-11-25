import requests
import json
import config
import apimoex
import datetime


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

    Returns int (price) if found.
    Returns None if not found
    """
    marketstack_result = marketstack_cost(symbol)
    if marketstack_result is not None:
        return marketstack_result
    return moex_cost(symbol)


def symbol_by_name(name, result_size=5):
    """Find symbol by company name using American and Russian api's.

    Returns list of pairs of possible symbols:
    [[full_name1, symbol1], [full_name2, symbol2], ...].
    result_size (default: 5) - maximum number of companies
    returned by one api
    """
    moex_result = moex_symbol_by_name(name)[:result_size]
    alphavantage_result = alphavantage_symbol_by_name(name)[:result_size]
    return moex_result + alphavantage_result


def parse_date(date):
    """
    Parse string with date to datetime object.
    :param date: type - string.
    :return: type - datetime.
    """
    date_list = list(map(int, date.split('-')))
    return datetime.datetime(date_list[0], date_list[1], date_list[2])


def get_period_data_of_cost_moex(start, end, name):
    r = apimoex.get_board_history(requests.Session(), name, start, end)
    return [[parse_date(x['TRADEDATE']) for x in r], [x['CLOSE'] for x in r]]


def get_period_data_of_cost_marketstack(start, end, name):
    query = "http://api.marketstack.com/v1/eod"
    params = {"date_from": start, "date_to": end, "access_key":
              config.API_KEY_MARKETSTACK, "symbols": name}
    r = requests.get(query, params=params).json()["data"] if "data" in\
        requests.get(query, params=params).json().keys() else []
    r.reverse()
    return [[parse_date(x["date"][:10]) for x in r], [x["close"] for x in r]]


def get_period_data_of_cost(start, end, name):
    """
    Makes list with costs by the each day from the period.
    :param start: begin of the period, type - string, format 'YYYY-MM-DD'.
    :param end: end of the period, type - string, format 'YYYY-MM-DD'.
    :param name: symbol of the company, type - string.
    :return: list with dates as datetime objects, list with costs as integers.
    """
    result_moex = get_period_data_of_cost_moex(start, end, name)
    result_marketstack = get_period_data_of_cost_marketstack(start, end, name)
    return result_marketstack if len(result_marketstack[0]) else result_moex
