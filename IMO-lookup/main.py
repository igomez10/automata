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


def postMessage(message):
    project_id = os.environ.get('PROJECT_ID')
    topic_name = os.environ.get("_SUB_PUB_TOPIC_NAME")

    topic_path = 'projects/{project_id}/topics/{topic_name}'.format(
        project_id=project_id,
        topic_name=topic_name
    )

    publisher = pubsub_v1.PublisherClient()
    future = publisher.publish(topic_path, str.encode(message))
    print(future.result())


def checkIfPropertyExists(propertyID):
    base_url = os.environ.get("_BASE_URL")
    conn = http.client.HTTPSConnection(base_url)
    payload = ''
    headers = {}
    conn.request("HEAD", "/expose/"+str(propertyID), payload, headers)
    res = conn.getresponse()

    if res.code == 200:
        return True

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
    logging.debug("Looking for property:")
    logging.debug(propertyID)
    exists = checkIfPropertyExists(propertyID)
    if exists:
        logging.debug("Property exists:")
        logging.debug(propertyID)
        postMessage(str(propertyID))
        # postProperty(propertyID)


counter = 0
biggestIdentifier = 114988500
app = Flask(__name__)


def scanProperties():
    logging.info("Started scanning properties")
    while True:
        global counter
        scanProperty(biggestIdentifier + counter)
        counter = counter + 1
        time.sleep(1)


@app.route('/')
def getPrice():
    return "OK"


def setupEnvs():
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path, verbose=True)
    for e in os.environ:
        print("%s %s" % (e, os.environ[e]))


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
