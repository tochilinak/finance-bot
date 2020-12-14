from queries.general import *
import requests
import config


class MoexCost(APIQuery):
    error_return = None

    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = ("https://iss.moex.com/iss/engines/stock/markets/shares/"
                 f"securities/{self.symbol}/candles.json?"
                 "interval=1&iss.reverse=true")
        return requests.get(query).json()["candles"]

    def result(self, resp):
        price_col = resp["columns"].index("close")
        date_col = resp["columns"].index("end")

        # not found
        if len(resp["data"]) == 0:
            return None

        price = resp["data"][0][price_col]
        date = resp["data"][0][date_col]
        return price, date


class MoexCompanyList(APIQuery):
    error_return = []

    def get_server_response(self):
        query = ("https://iss.moex.com/iss/engines/stock/markets/shares/"
                 "boards/TQBR/securities.json?securities.columns=SECID&"
                 "iss.meta=off&iss.only=securities")
        return requests.get(query).json()

    def result(self, resp):
        return [x[0] for x in resp['securities']['data']]


moex_company_list = query_function_factory(MoexCompanyList)


class MoexSymbolByName(APIQuery):
    error_return = []

    def __init__(self, name):
        self.name = name
        self.report_list = [name]

    def get_server_response(self):
        query = ("https://iss.moex.com/iss/securities.json?q=" + self.name
                 + "&securities.columns=name,secid&iss.meta=off")
        return requests.get(query).json()

    def result(self, resp):
        company_list = moex_company_list()
        only_stock = filter(lambda x: x[1] in company_list,
                            resp['securities']['data'])
        return [x[:2] for x in only_stock]


class MoexCurrency(APIQuery):
    error_return = None

    def __init__(self, symbol):
        self.symbol = symbol
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = "https://iss.moex.com/iss/securities/" + self.symbol + ".json"
        return requests.get(query).json()

    def result(self, resp):
        resp = resp["boards"]
        col = resp["columns"].index("currencyid")
        for description_string in resp["data"]:
            # there is an information of company's currency in such string.
            if description_string[1] == "TQBR":
                # this cell contains the name of a currency.
                return description_string[col]
        return None
