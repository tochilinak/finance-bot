import requests
import apimoex
from queries.alphavantage_requests import *
from queries.moex_requests import *
from queries.general import query_function_factory


moex_cost = query_function_factory(MoexCost)
alphavantage_cost = query_function_factory(AlphaVantageCost)


def current_cost(symbol):
    """Find stock price by symbol.

    Returns int (price), string (date) if found.
    Returns None if not found
    """
    moex_result = moex_cost(symbol)
    if moex_result is not None:
        return moex_result
    return alphavantage_cost(symbol)


moex_symbol_by_name = query_function_factory(MoexSymbolByName)
alphavantage_symbol_by_name = query_function_factory(AlphaVantageSymbolByName)


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


def get_period_data_of_cost_moex(start, end, symbol):
    resp = apimoex.get_board_history(requests.Session(), symbol, start, end)
    return [[parse_date(x['TRADEDATE']) for x in resp], [float(x['CLOSE'])
                                                         for x in resp]]


get_period_data_of_cost_alphavantage = query_function_factory(
                                        AlphaVantagePeriodDataOfCost)


def get_period_data_of_cost(start, end, symbol):
    """Make list with costs by the each day from the period.

    :param start: begin of the period; type - string, format 'YYYY-MM-DD'.
    :param end: end of the period; type - string, format 'YYYY-MM-DD'.
    :param symbol: symbol of the company; type - string.
    :return: list with dates as datetime objects, list with costs as floats.
    """
    result_moex = get_period_data_of_cost_moex(start, end, symbol)

    if len(result_moex[0]):
        return result_moex

    return get_period_data_of_cost_alphavantage(start, end, symbol)


get_currency_alphavantage = query_function_factory(AlphaVantageCurrency)
get_currency_moex = query_function_factory(MoexCurrency)


def get_currency(symbol):
    """Return currency of the company.

    :param symbol: symbol of company.
    :return: currency; type - string, None if not found.
    """
    result_moex = get_currency_moex(symbol)
    if result_moex is None:
        return get_currency_alphavantage(symbol)
    return result_moex
