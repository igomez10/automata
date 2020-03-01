import mimetypes
import http.client
import time
import os
import threading
from flask import Flask
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import logging

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
    print(id)
    return


def scanProperty(propertyID):
    logging.debug("Looking for property:")
    logging.debug(propertyID)
    exists = checkIfPropertyExists(propertyID)
    if exists:
        logging.debug("Property exists:")
        logging.debug(propertyID)
        postProperty(propertyID)


counter = 0
biggestIdentifier = 114988500
started = False
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
    global started
    if started:
        return "OK"
    started = True
    x = threading.Thread(target=scanProperties)
    x.start()
    return "Started"


def setupEnvs():
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path, verbose=True)


if __name__ == "__main__":
    setupEnvs()
    started = False
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format,
                        level=logging.DEBUG,
                        datefmt="%H:%M:%S")
    debug = os.getenv("_DEBUG", False)
    app.run(debug=debug,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
