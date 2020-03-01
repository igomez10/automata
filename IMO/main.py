import mimetypes
import http.client
import time
import os
import threading
from flask import Flask
from dotenv import load_dotenv
from pathlib import Path  # python3 only


def checkIfPropertyExists(propertyID):
    base_url = os.environ.get("_BASE_URL")
    conn = http.client.HTTPSConnection(base_url)
    payload = ''
    headers = {}
    conn.request("HEAD", "/expose/"+str(propertyID), payload, headers)
    res = conn.getresponse()
    cases = {
        200: True,
    }

    if res.code in cases:  # exists
        return cases[res.code]

    return False


def postProperty(id):
    print(id)
    return


def scanProperty(propertyID):
    exists = checkIfPropertyExists(propertyID)
    if exists:
        postProperty(propertyID)


counter = 0
biggestIdentifier = 114988500
started = False
app = Flask(__name__)


def scanProperties():
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
    return 201


def setupEnvs():
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path, verbose=True)


if __name__ == "__main__":
    setupEnvs()
    started = False
    debug = os.getenv("_DEBUG", False)
    app.run(debug=debug,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
