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
import opencensus
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
from opencensus.common.transports.async_ import AsyncTransport
from opencensus.trace.tracer import Tracer


def postMessage(message):
    project_id = os.environ.get('PROJECT_ID')
    topic_name = os.environ.get("_SUB_PUB_TOPIC_NAME")

    topic_path = 'projects/{project_id}/topics/{topic_name}'.format(
        project_id=project_id,
        topic_name=topic_name
    )
    try:
        with tracer.span(name="sub/pub"):
            publisher = pubsub_v1.PublisherClient()
            future = publisher.publish(topic_path, str.encode(message))
            print(future.result())
    except Exception:
        logging.error("failed to post message to pub/sub")


def checkIfPropertyExists(propertyID):
    base_url = os.environ.get("_BASE_URL")
    conn = http.client.HTTPSConnection(base_url, timeout=10)
    payload = ''
    headers = {}
    exists = False
    try:
        with tracer.span(name="base_url/expose/%d" % propertyID):
            conn.request("HEAD", "/expose/%s" % propertyID, payload, headers)
            res = conn.getresponse()
        if res.code == 200:
            exists = True

    except Exception as identifier:
        logging.error("Failed making HTTP request")
        logging.error(type(identifier))
        logging.error(identifier)

    finally:
        conn.close()
        return exists


def scanProperty(propertyID):
    logging.debug("Looking for property %d", propertyID)
    exists = checkIfPropertyExists(propertyID)
    if exists:
        logging.debug("Property with id %s exists" % propertyID)
        postMessage(str(propertyID))


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


app = Flask(__name__)
@app.route('/')
def getHome():
    return "OK"


def setupEnvs():
    env_path = Path(os.environ.get("ENV_FILE_DIR", ".")) / '.env'
    load_dotenv(dotenv_path=env_path, verbose=True)
    for e in os.environ:
        print("%s %s" % (e, os.environ[e]))


def getTracer():
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


exporter = stackdriver_exporter.StackdriverExporter(
    project_id=os.environ.get("PROJECT_ID"),
    transport=AsyncTransport,
)

tracer = opencensus.trace.tracer.Tracer(
    exporter=exporter,
    sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler()
)


if __name__ == "__main__":
    setupEnvs()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format,
                        level=logging.DEBUG,
                        datefmt="%H:%M:%S")

    debug = os.getenv("_DEBUG", False)
    listenIncomingTraffic()
    scanProperties()
