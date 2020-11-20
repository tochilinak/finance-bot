import requests
import json
import config


def moex_cost(symbol):
    query = ("https://iss.moex.com/iss/engines/stock/markets/shares"
             "/boards/TQBR/securities.json?securities.columns=SECID,"
             "PREVADMITTEDQUOTE&iss.meta=off&iss.only=securities")
    resp_raw = requests.get(query).text
    resp = json.JSONDecoder().decode(resp_raw)
    result = next((x[1] for x in resp['securities']['data']
                  if x[0] == symbol), None)
    return result

def marketstack_cost(symbol):
    query = "http://api.marketstack.com/v1/tickers/" + symbol + "/intraday/latest"
    params = {"access_key": config.API_KEY_MARKETSTACK}
    r = requests.get(query, params=params)
    result = r.json()["close"]
    return result