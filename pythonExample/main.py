import datetime
import time
import http.client
import mimetypes
import json


def getBTCPrice():
    conn = http.client.HTTPSConnection("api.coindesk.com")
    payload = ''
    headers = {}
    conn.request("GET", "/v1/bpi/currentprice.json", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    loaded_json = json.loads(data)
    return loaded_json["bpi"]["USD"]["rate"]


while True:
    print(getBTCPrice())
    # print(datetime.datetime.now())
    time.sleep(1)
