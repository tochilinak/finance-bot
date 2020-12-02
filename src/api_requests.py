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


def alphavantage_cost(symbol):
    query = "https://www.alphavantage.co/query"
    params = {"function": "TIME_SERIES_INTRADAY", "symbol": symbol,
              "interval": "1min", "apikey": config.API_KEY_ALPHAVANTAGE}
    resp = requests.get(query, params=params).json()
    if "Error Message" in resp.keys():
        return None
    last_cost_update_key = list(resp["Time Series (1min)"].keys())[0]
    result = resp["Time Series (1min)"][last_cost_update_key]["4. close"]
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
    resp = requests.get(query, params=params).json()
    result = [[x["2. name"], x["1. symbol"]] for x in resp["bestMatches"]]
    return result


def current_cost(symbol):
    """Find stock price by symbol.

    Returns int (price) if found.
    Returns None if not found
    """
    alphavantage_result = alphavantage_cost(symbol)
    if alphavantage_result is not None:
        return alphavantage_result
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

    def pairs_into_dict(list_of_pairs):
        return dict([[y, x] for x, y in list_of_pairs])

    # putting found companies in dict, where key is symbol
    # and name is value. This way no symbol will be listed twice.
    found = pairs_into_dict(alphavantage_result)
    found.update(pairs_into_dict(moex_result))

    # converting dict into list of pairs
    return [[y, x] for x, y in found.items()]


def parse_date(date):
    """Parse string with date to datetime object.

    :param date: type - string.
    :return: type - datetime.
    """
    date_list = list(map(int, date.split('-')))
    return datetime.datetime(date_list[0], date_list[1], date_list[2])


def get_period_data_of_cost_moex(start, end, symbol):
    resp = apimoex.get_board_history(requests.Session(), symbol, start, end)
    return [[parse_date(x['TRADEDATE']) for x in resp], [float(x['CLOSE'])
                                                         for x in resp]]


def get_period_data_of_cost_alphavantage(start, end, symbol):
    query = "https://www.alphavantage.co/query"
    params = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey":
              config.API_KEY_ALPHAVANTAGE, "outputsize": "full"}
    result = [[], []]
    if "Error Message" in requests.get(query, params=params).json().keys():
        return result

    # there are prices of stocks by each day from company history
    # in "Time Series (Daily)" resp key.
    resp = requests.get(query, params=params).json()["Time Series (Daily)"]
    start_ordinal = parse_date(start).toordinal()
    end_ordinal = parse_date(end).toordinal()
    for date_ordinal in range(start_ordinal, end_ordinal + 1):
        current_date = datetime.datetime.fromordinal(date_ordinal)
        if current_date.isoformat()[:10] in resp.keys():
            result[0].append(current_date)
            result[1].append(float(resp[current_date.isoformat()[:10]]
                                   ["4. close"]))
    return result


def get_period_data_of_cost(start, end, symbol):
    """Make list with costs by the each day from the period.

    :param start: begin of the period; type - string, format 'YYYY-MM-DD'.
    :param end: end of the period; type - string, format 'YYYY-MM-DD'.
    :param symbol: symbol of the company; type - string.
    :return: list with dates as datetime objects, list with costs as floats.
    """
    result_moex = get_period_data_of_cost_moex(start, end, symbol)
    result_alphavantage = get_period_data_of_cost_alphavantage(start,
                                                               end, symbol)
    return result_alphavantage if len(result_alphavantage[0]) else result_moex


def get_currency_alphavantage(symbol):
    query = "https://www.alphavantage.co/query"
    params = {"function": "OVERVIEW", "symbol": symbol, "apikey":
              config.API_KEY_ALPHAVANTAGE}
    resp = requests.get(query, params=params).json()
    if "Currency" not in resp.keys():
        return None
    return resp["Currency"]


def get_currency_moex(symbol):
    query = "https://iss.moex.com/iss/securities/" + symbol + ".json"

    # there is a description data of company in "description" and "data"
    # resp keys.
    resp = requests.get(query).json()["description"]["data"]
    for description_string in resp:

        # there is an information of company's currency in such string.
        if description_string[0] == "FACEUNIT":

            # this cell contains the name of a currency.
            return description_string[2]
    return None


def get_currency(symbol):
    """Return currency of the company.

    :param symbol: symbol of company.
    :return: currency; type - string, None if not found.
    """
    result_alphavantage = get_currency_alphavantage(symbol)
    if result_alphavantage is None:
        return get_currency_moex(symbol)
    return result_alphavantage
