from queries.general import *
import requests
import config


class FinnhubCost(APIQuery):
    empty_return = None

    def set_report(self):
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = "https://finnhub.io/api/v1/quote"
        params = {"symbol": self.symbol, "token": config.API_KEY_FINNHUB}
        self.response = self.session.get(query, params=params)

    def process_json(self, resp):
        result = resp["c"]
        if int(result) == 0:
            return None
        return result, "real time"


class AlphaVantageSymbolByName(APIQuery):
    empty_return = []

    def set_report(self):
        self.report_list = [self.name]

    def get_server_response(self):
        query = "https://www.alphavantage.co/query"
        params = {"function": "SYMBOL_SEARCH", "keywords": self.name, "apikey":
                  config.API_KEY_ALPHAVANTAGE}
        self.response = self.session.get(query, params=params)

    def process_json(self, resp):
        result = [[x["2. name"], x["1. symbol"]] for x in resp["bestMatches"]]
        return result


class FinnhubCurrency(APIQuery):
    empty_return = None

    def set_report(self):
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = "https://finnhub.io/api/v1/stock/profile2"
        params = {"symbol": self.symbol, "token": config.API_KEY_FINNHUB}
        self.response = self.session.get(query, params=params)

    def process_json(self, resp):
        if len(resp.keys()) == 0:
            return None
        return resp["currency"]
