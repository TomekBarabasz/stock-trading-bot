import json

def readConfig(filename, verbose):
    try:
        with filename.open() as jsonFile:
            cfg = json.load(jsonFile)
        verbose('config file loaded succesfully')
        return cfg
    except json.decoder.JSONDecodeError:
        verbose('config file corrupted, reverting to defaults')
        raise
