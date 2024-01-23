import json
from types import SimpleNamespace

def readJson(filename, verbose):
    try:
        with filename.open() as jsonFile:
            cfg = json.load(jsonFile)
        verbose('config file loaded succesfully')
        return cfg
    except json.decoder.JSONDecodeError:
        verbose('config file corrupted, reverting to defaults')
        raise

def loadObjectFromJson(data,class_):
    d = json.load(data)
    o = class_()
    for k,v in d.items():
        setattr(o,k,v)
    return o

def loadNamespaceFromJson(filename):
    return json.load(filename, object_hook=lambda d: SimpleNamespace(**d))

def readConfig(filename):
    class Configuration:
        pass
    with filename.open() as jsonFile:
        return loadObjectFromJson(jsonFile,Configuration)

PeriodCodes = { 'M1':1,
                'M5':5,
                'M15':15,
                'M30':30,
                'H1':60,
                'H4':240,
                'D1':1440,
                'W1':10080,
                'MN1':43200 }
