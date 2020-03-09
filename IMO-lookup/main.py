#!/usr/bin/env python

import mimetypes
import http.client
import time
import os
import threading
from flask import Flask
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import logging
from google.cloud import pubsub_v1
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer
from opencensus.common.transports.async_ import AsyncTransport


def postMessage(message):
    project_id = os.environ.get('PROJECT_ID')
    topic_name = os.environ.get("_SUB_PUB_TOPIC_NAME")

    topic_path = 'projects/{project_id}/topics/{topic_name}'.format(
        project_id=project_id,
        topic_name=topic_name
    )

    publisher = pubsub_v1.PublisherClient()

    tracer = initialize_tracer()
    tracer.start_span(name="sub/pub")

    future = publisher.publish(topic_path, str.encode(message))
    print(future.result())
    tracer.end_span()


def checkIfPropertyExists(propertyID):
    base_url = os.environ.get("_BASE_URL")
    conn = http.client.HTTPSConnection(base_url, timeout=10)
    payload = ''
    headers = {}

    try:
        tracer = initialize_tracer()
        tracer.start_span(name=base_url)
        conn.request("HEAD", "/expose/"+str(propertyID), payload, headers)
        res = conn.getresponse()
        tracer.end_span()
        if res.code == 200:
            return True
    except Exception as identifier:
        logging.error("Failed making HTTP request")
        logging.error(type(identifier))
        logging.error(identifier)
        return False


def postProperty(id):
    conn = http.client.HTTPSConnection("api.airtable.com")

    payload = '{"records":[{"fields": {"ID": "%s" }}]}' % str(id)

    api_key = os.getenv("_AIRTABLE_API_KEY")
    base_id = os.getenv("_AIRTABLE_BASE_ID")

    headers = {
        'Authorization': 'Bearer %s' % (api_key),
        'Content-Type': 'application/json'
    }
    conn.request("POST", '/v0/%s/Properties' % (base_id), payload, headers)
    res = conn.getresponse()
    if res.code == 200:
        logging.debug("Created new entry")
    else:
        logging.error("Failed posting new property")
        data = res.read()
        logging.error(data.decode("utf-8"))


def scanProperty(propertyID):
    logging.debug("Looking for property %d", propertyID)
    exists = checkIfPropertyExists(propertyID)
    if exists:
        logging.debug("Property with id %s exists" % propertyID)
        postMessage(str(propertyID))


app = Flask(__name__)


def scanProperties():
    logging.info("Started scanning properties")
    counter = 0
    initialIdentifier = 114987500
    currentIdentifier = initialIdentifier
    biggestIdentifier = 114990500

    while True:
        scanProperty(currentIdentifier + counter)
        currentIdentifier = currentIdentifier + 1
        if currentIdentifier == biggestIdentifier:
            currentIdentifier = initialIdentifier
        time.sleep(1)
    logging.error("Exited while loop")


@app.route('/')
def getPrice():
    return "OK"


def setupEnvs():
    env_path = Path(os.environ.get("ENV_FILE_DIR", ".")) / '.env'
    load_dotenv(dotenv_path=env_path, verbose=True)
    for e in os.environ:
        print("%s %s" % (e, os.environ[e]))


def initialize_tracer():
    exporter = stackdriver_exporter.StackdriverExporter(
        project_id=os.environ.get("PROJECT_ID"),
        transport=AsyncTransport
    )
    tracer = opencensus.trace.tracer.Tracer(
        exporter=exporter
    )
    return tracer


# listenIncomingTraffic is only a placeholder for CloudRun requirements
def listenIncomingTraffic():
    threading.Thread(
        target=app.run,
        kwargs=dict(debug=False,
                    host='0.0.0.0',
                    port=int(os.environ.get('PORT', 8080)),
                    use_reloader=False,
                    )).start()


if __name__ == "__main__":
    setupEnvs()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format,
                        level=logging.DEBUG,
                        datefmt="%H:%M:%S")

    debug = os.getenv("_DEBUG", False)
    listenIncomingTraffic()
    scanProperties()
