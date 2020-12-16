from queries.general import *
import requests
import config


class MoexCost(APIQuery):
    error_return = None

    def set_report(self):
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = ("https://iss.moex.com/iss/engines/stock/markets/shares/"
                 f"securities/{self.symbol}/candles.json?"
                 "interval=1&iss.reverse=true")
        self.response = requests.get(query)

    def process_json(self, resp):
        resp = resp["candles"]
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
        self.response = requests.get(query)

    def process_json(self, resp):
        return [x[0] for x in resp['securities']['data']]


moex_company_list = query_function_factory(MoexCompanyList)


class MoexSymbolByName(APIQuery):
    error_return = []

    def set_report(self):
        self.report_list = [self.name]

    def get_server_response(self):
        query = ("https://iss.moex.com/iss/securities.json?q=" + self.name
                 + "&securities.columns=name,secid&iss.meta=off")
        self.response = requests.get(query)

    def process_json(self, resp):
        company_list = moex_company_list(QueryData())
        only_stock = filter(lambda x: x[1] in company_list,
                            resp['securities']['data'])
        return [x[:2] for x in only_stock]


class MoexCurrency(APIQuery):
    error_return = None

    def set_report(self):
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = "https://iss.moex.com/iss/securities/" + self.symbol + ".json"
        self.response = requests.get(query)

    def process_json(self, resp):
        resp = resp["boards"]
        col = resp["columns"].index("currencyid")
        for description_string in resp["data"]:
            # there is an information of company's currency in such string.
            if description_string[1] == "TQBR":
                # this cell contains the name of a currency.
                return description_string[col]
        return None
