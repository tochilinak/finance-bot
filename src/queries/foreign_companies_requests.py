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


class AlphaVantagePeriodDataOfCost(APIQuery):
    empty_return = [[], []]

    def set_report(self):
        self.report_list = [self.start, self.end, self.symbol]

    def get_server_response(self):
        query = "https://www.alphavantage.co/query"
        params = {"function": "TIME_SERIES_DAILY", "symbol": self.symbol,
                  "apikey": config.API_KEY_ALPHAVANTAGE, "outputsize": "full"}
        self.response = self.session.get(query, params=params)

    def process_json(self, resp):
        res = [[], []]
        if "Error Message" in resp.keys():
            return res
        resp = resp["Time Series (Daily)"]
        start_ordinal = parse_date(self.start).toordinal()
        end_ordinal = parse_date(self.end).toordinal()
        for date_ordinal in range(start_ordinal, end_ordinal + 1):
            current_date = datetime.datetime.fromordinal(date_ordinal)
            if current_date.isoformat()[:10] in resp.keys():
                res[0].append(current_date)
                res[1].append(float(resp[current_date.isoformat()[:10]]
                              ["4. close"]))
        return res


class AlphaVantageCurrency(APIQuery):
    empty_return = None

    def set_report(self):
        self.report_list = [self.symbol]

    def get_server_response(self):
        query = "https://www.alphavantage.co/query"
        params = {"function": "OVERVIEW", "symbol": self.symbol, "apikey":
                  config.API_KEY_ALPHAVANTAGE}
        self.response = self.session.get(query, params=params)

    def process_json(self, resp):
        if "Currency" not in resp.keys():
            return None
        return resp["Currency"]
