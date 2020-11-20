import requests
import json


def moex_cost(symbol):
    query = ("https://iss.moex.com/iss/engines/stock/markets/shares"
             "/boards/TQBR/securities.json?securities.columns=SECID,"
             "PREVADMITTEDQUOTE&iss.meta=off&iss.only=securities")
    resp_raw = requests.get(query).text
    resp = json.JSONDecoder().decode(resp_raw)
    result = next((x[1] for x in resp['securities']['data']
                  if x[0] == symbol), None)
    return result
