import requests
import apimoex
from queries.alphavantage_requests import *
from queries.moex_requests import *
from queries.general import *
from enum import Enum, auto
from requests_futures.sessions import FuturesSession
import itertools as it
import threading
from concurrent.futures import as_completed


moex_cost = query_function_factory(MoexCost)
alphavantage_cost = query_function_factory(AlphaVantageCost)


def current_cost(symbol):
    """Find stock price by symbol.

    Returns int (price), string (date) if found.
    Returns None if not found
    """
    query_data = QueryData(symbol=symbol)
    moex_result = moex_cost(query_data)
    if moex_result is not None:
        return moex_result
    return alphavantage_cost(query_data)


moex_symbol_by_name = query_function_factory(MoexSymbolByName)
alphavantage_symbol_by_name = query_function_factory(AlphaVantageSymbolByName)


def symbol_by_name(name, result_size=5):
    """Find symbol by company name using American and Russian api's.

    Returns list of pairs of possible symbols:
    [[full_name1, symbol1], [full_name2, symbol2], ...].
    result_size (default: 5) - maximum number of companies
    returned by one api
    """
    query_data = QueryData(name=name)
    moex_result = moex_symbol_by_name(query_data)[:result_size]
    alphavantage_result = alphavantage_symbol_by_name(query_data)[:result_size]

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
    query_data = QueryData(start_date=start, end_date=end, symbol=symbol)
    result_moex = get_period_data_of_cost_moex(start, end, symbol)

    if len(result_moex[0]):
        return result_moex

    return get_period_data_of_cost_alphavantage(query_data)


get_currency_alphavantage = query_function_factory(AlphaVantageCurrency)
get_currency_moex = query_function_factory(MoexCurrency)


def get_currency(symbol):
    """Return currency of the company.

    :param symbol: symbol of company.
    :return: currency; type - string, None if not found.
    """
    query_data = QueryData(symbol=symbol)
    result_moex = get_currency_moex(query_data)
    if result_moex is None:
        return get_currency_alphavantage(query_data)
    return result_moex


class QueryType(Enum):
    CURRENT_COST = auto()
    PERIOD_COST = auto()
    CURRENCY = auto()


moex_queries = {
    QueryType.CURRENT_COST: MoexCost,
    QueryType.CURRENCY: MoexCurrency
}

alphavantage_queries = {
    QueryType.CURRENT_COST: AlphaVantageCost,
    QueryType.CURRENCY: AlphaVantageCurrency
}


def start_requests(query_data_list, query_types, type_dict):
    session = FuturesSession()
    list_of_futures = []
    for query_data_id, query_data in enumerate(query_data_list):
        for query_type in query_types:
            if query_type == QueryType.PERIOD_COST:
                continue
            query = type_dict[query_type](session, query_data,
                                             query_data_id=query_data_id,
                                             query_type=query_type)
            query.get_server_response()
            query.response.attached_to = query
            list_of_futures.append(query.response)

    return list_of_futures


def collect_results(list_of_futures, query_data_list):
    for future in as_completed(list_of_futures):
        query = future.attached_to
        query.response = future.result()
        query_data = query_data_list[query.query_data_id]
        query_data.result[query.query_type] = query.get_result()


def async_request(query_data_list, query_types):
    # first try moex requests
    list_of_futures = start_requests(query_data_list, query_types, moex_queries)
    collect_results(list_of_futures, query_data_list)

    not_found_data = []
    for query_data in query_data_list:
        if any(query_data.result[x] == moex_queries[x].empty_return
               for x in query_types):
            not_found_data.append(query_data)

    # try alphavantage for not found
    list_of_futures = start_requests(not_found_data, query_types,
                                     alphavantage_queries)
    collect_results(list_of_futures, not_found_data)
