import http.client, urllib
from sys import argv
from utils import loadNamespaceFromJson
from notify import NotificationSink

def send_notify(cred, message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": cred.app_token,
        "user" : cred.user_key,
        "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def send_file(filename):
    import requests
    from pathlib import Path
    pf = Path(filename)
    r = requests.post("https://api.pushover.net/1/messages.json", 
        data = {
            "token": cred.app_token,
            "user": cred.user_key,
            "message": "hello world"
        },
        files = {
            "attachment": (pf.name, pf.open('rb'), "image/jpeg")
        }
    )
    print(r.text)

def PushoverNotifySink(NotificationSink):
    def __init__(self, credentials):
        self.credentials = credentials
    def notify(self, source, message):
        send_notify(self.credentials, message)

def createPushoverSink(configuration_filename):
    credentials = loadNamespaceFromJson(open(configuration_filename)).pushover
    ps = PushoverNotifySink(credentials)
    return ps

def loadCredentials(argv):
    cred_filename = argv[2] if len(argv) > 2 else './data/credentials.json'
    return  loadNamespaceFromJson(open(cred_filename)).pushover
    
if __name__ == '__main__':
    message = argv[1] if len(argv) > 1 else "hello from Stock-o-Bot"
    cred = loadCredentials(argv)
    send_notify(cred,message)
    