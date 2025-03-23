import json
from types import SimpleNamespace
from .xtb import read_json

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

def collect_symbols_data(data_folder, name_regex = None):
    from pathlib import Path
    Symbols = {}
    for subf in Path(data_folder).iterdir():
        if subf.is_dir() and (name_regex is None or name_regex.match(subf.name) is not None):
            for file in subf.iterdir():
                if file.suffix in ('.json','.pkl'):
                    symbol = file.stem
                    if symbol in Symbols:
                        Symbols[symbol].append(file)
                    else:
                        Symbols[symbol] = [file]
    return Symbols

def merge_data(Files):
    import pandas as pd
    dataframes = []
    for fn in Files:
        if fn.suffix == '.json':
            df = read_json(fn)
        elif fn.suffix == '.pkl':
            df = pd.read_pickle(fn)
        else:
            print(f'unsupported file format {fn.name} - skipping')
            continue
        dataframes.append(df)
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.sort_values(by='Date', inplace=True)
    merged_df.drop_duplicates(subset=['Date'], keep='first', inplace=True)
    # reset index if you want a clean integer index
    merged_df.reset_index(drop=True, inplace=True)
    return merged_df  
