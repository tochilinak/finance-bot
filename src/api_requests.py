import requests
import apimoex
from queries.foreign_companies_requests import *
from queries.moex_requests import *
from queries.general import *
from enum import Enum, auto
from requests_futures.sessions import FuturesSession
import itertools as it
import threading
import yfinance
import datetime


class QueryType(Enum):
    CURRENT_COST = auto()
    PERIOD_COST = auto()
    CURRENCY = auto()


moex_cost = query_function_factory(MoexCost)
finnhub_cost = query_function_factory(FinnhubCost)


def current_cost(symbol):
    """Find stock price by symbol.

    Returns int (price), string (date) if found.
    Returns None if not found
    """
    query_data = QueryData(symbol=symbol)
    moex_result = moex_cost(query_data)
    if moex_result is not None:
        return moex_result
    return finnhub_cost(query_data)


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


get_primary_board_moex = query_function_factory(MoexPrimaryBoard)


def get_period_data_of_cost_moex(start, end, symbol):
    resp = apimoex.get_market_history(requests.Session(), symbol, start, end)
    board = get_primary_board_moex(QueryData(symbol=symbol))
    dates, prices = [], []
    for line in resp:
        if line['CLOSE'] is None or line['BOARDID'] != board:
            continue
        dates += [datetime.datetime.strptime(line['TRADEDATE'], "%Y-%m-%d")]
        prices += [float(line['CLOSE'])]

    return dates, prices


def get_period_data_of_cost_yahoo(start, end, symbol):

    def add_day(date, delta=1):
        return (datetime.date.fromisoformat(date) +
                datetime.timedelta(days=delta)).isoformat()

    try:
        company = yfinance.Ticker(symbol)
        res = company.history(start=add_day(start, -1), end=add_day(end))["Close"]

        # remove extra dates
        res = res[(res.index.strftime("%Y-%m-%d") >= start) &
                  (res.index.strftime("%Y-%m-%d") <= end)]

        dates = [x.to_pydatetime() for x in res.index]
        return dates, list(res)
    except:
        return [], []


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

    return get_period_data_of_cost_yahoo(start, end, symbol)


def get_period_data_of_cost_query_data(query_data):
    result = get_period_data_of_cost(query_data.start_date,
                                     query_data.end_date, query_data.symbol)
    query_data.result[QueryType.PERIOD_COST] = result


get_currency_finnhub = query_function_factory(FinnhubCurrency)
get_currency_moex = query_function_factory(MoexCurrency)


def get_currency(symbol):
    """Return currency of the company.

    :param symbol: symbol of company.
    :return: currency; type - string, None if not found.
    """
    query_data = QueryData(symbol=symbol)
    result_moex = get_currency_moex(query_data)
    if result_moex is None:
        return get_currency_finnhub(query_data)
    return result_moex


moex_queries = {
    QueryType.CURRENT_COST: MoexCost,
    QueryType.CURRENCY: MoexCurrency
}

foreign_queries = {
    QueryType.CURRENT_COST: FinnhubCost,
    QueryType.CURRENCY: FinnhubCurrency
}


def start_requests(session, query_data_list, query_types, type_dict):
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
            query_data.result[query_type] = query.empty_return

    return list_of_futures


def collect_results(list_of_futures, query_data_list):
    for i in range(len(list_of_futures)):
        future = list_of_futures[i]
        query = future.attached_to
        query_data = query_data_list[query.query_data_id]
        if query_data.result[query.query_type] != query.empty_return:
            future.cancel()
            continue
        query.response = future.result()
        query_data.result[query.query_type] = query.get_result()


def async_current_cost_and_currency(query_data_list, query_types):
    session = FuturesSession()
    list_of_futures_moex = start_requests(session, query_data_list,
                                          query_types, moex_queries)
    list_of_futures_foreign = start_requests(session, query_data_list,
                                             query_types, foreign_queries)
    collect_results(list_of_futures_moex, query_data_list)
    collect_results(list_of_futures_foreign, query_data_list)


def start_period_cost(query_data_list):
    threads = []
    for query_data in query_data_list:
        x = threading.Thread(target=get_period_data_of_cost_query_data,
                             args=(query_data,))
        threads.append(x)
        x.start()
    return threads


def async_request(query_data_list, query_types):
    threads = []
    if QueryType.PERIOD_COST in query_types:
        threads += start_period_cost(query_data_list)

    rest = threading.Thread(target=async_current_cost_and_currency,
                            args=(query_data_list, query_types,))
    threads.append(rest)
    rest.start()

    for thread in threads:
        thread.join()
