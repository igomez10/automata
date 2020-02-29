from flask import Flask
import os
import datetime
import time
import http.client
import mimetypes
import json
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer


def initialize_tracer(project_id):
    exporter = stackdriver_exporter.StackdriverExporter(
        project_id=project_id
    )
    tracer = opencensus.trace.tracer.Tracer(
        exporter=exporter,
        sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler()
    )

    return tracer


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


@app.route('/price/btc/usd')
def getPrice():
    tracer = app.config['TRACER']
    tracer.start_span(name='price/btc/usd')
    price = getBTCPrice()
    tracer.end_span()
    return price


if __name__ == "__main__":
    tracer = initialize_tracer(os.environ.get("GOOGLE_CLOUD_PROJECT"))
    app.config['TRACER'] = tracer

    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
