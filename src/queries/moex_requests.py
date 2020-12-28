from queries.general import *
import requests
import config


class MoexCost(APIQuery):
    empty_return = None

    def set_report(self):
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = ("https://iss.moex.com/iss/engines/stock/markets/shares/"
                 f"securities/{self.symbol}/candles.json?"
                 "interval=1&iss.reverse=true&from=2020-01-01")
        self.response = self.session.get(query)

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


class MoexSymbolByName(APIQuery):
    empty_return = []

    def set_report(self):
        self.report_list = [self.name]

    def get_server_response(self):
        query = ("https://iss.moex.com/iss/securities.json?q=" + self.name
                 + "&securities.columns=name,secid,is_traded&iss.meta=off")
        self.response = self.session.get(query)

    def process_json(self, resp):
        only_active = filter(lambda x: x[2],
                            resp['securities']['data'])
        return [x[:2] for x in only_active]


class MoexCurrency(APIQuery):
    empty_return = None

    def set_report(self):
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = "https://iss.moex.com/iss/securities/" + self.symbol + ".json"
        self.response = self.session.get(query)

    def process_json(self, resp):
        resp = resp["boards"]
        cur_col = resp["columns"].index("currencyid")
        primary_col = resp["columns"].index("is_primary")
        for description_string in resp["data"]:
            # there is an information of company's currency in such string.
            if description_string[primary_col] == 1:
                # this cell contains the name of a currency.
                return description_string[cur_col]
        return None
