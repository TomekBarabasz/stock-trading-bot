import json
from types import SimpleNamespace
from datetime import datetime, timedelta

def readJson(filename, logger):
    try:
        with filename.open() as jsonFile:
            cfg = json.load(jsonFile)
        logger.info('config file loaded succesfully')
        return cfg
    except json.decoder.JSONDecodeError:
        logger.error('config file corrupted, reverting to defaults')
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

def xtb_timestamp(date_):
    dt = date_-datetime(1970,1,1)
    return int(dt.total_seconds()*1000)

def xtb_date(timestamp):
    return datetime(1970,1,1) + timedelta(seconds = timestamp / 1000)
