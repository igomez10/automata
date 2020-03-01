import mimetypes
import http.client
import time
import os


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

while True:
    scanProperty(biggestIdentifier+counter)
    counter = counter + 1
