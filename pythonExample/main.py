from flask import Flask
import os
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


app = Flask(__name__)


@app.route('/')
def getPrice():
    price = getBTCPrice()
    return price


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
