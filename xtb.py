import json
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

def date_to_timestamp(date_):
    dt = date_-datetime(1970,1,1)
    return int(dt.total_seconds()*1000)

def timestamp_to_date(timestamp):
    return datetime(1970,1,1) + timedelta(seconds = timestamp / 1000)

def read_json(filename):
    j = json.loads( open(filename).read() )
    digits = 10**j['digits']
    df = pd.DataFrame(j['rateInfos'])
    df.rename(columns={'close':'close_r', 'low':'low_r', 'high':'high_r'}, inplace=True)
    df.open /= digits
    df['close'] = df.open + df.close_r/digits
    df['low'] = df.open + df.low_r/digits
    df['high'] = df.open + df.high_r/digits
    df['Date'] = df.apply( lambda r : timestamp_to_date( r.ctm ), axis=1 )
    return df

def collect_symbols_data(data_folder):
    Symbols = {}
    for subf in Path(data_folder).iterdir():
        if subf.is_dir():
            for file in subf.iterdir():
                if file.suffix in ('.json','.plkl'):
                    symbol = file.stem
                    if symbol in Symbols:
                        Symbols[symbol].append(file)
                    else:
                        Symbols[symbol] = [file]
    return Symbols

def merge_data(Files):
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

def normalize_candles(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = {'open','close','high','low'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Missing columns: {missing}")

    df = df.copy()
    o = df.open
    c = df.close
    h = df.high
    l = df.low

    total_range = h-l
    total_range = total_range.replace(0, 1e-9) #prevent later division by zero
    body = (c-o).abs()
    max_oc = pd.concat([o,c], axis=1).max(axis=1)
    min_oc = pd.concat([o,c], axis=1).min(axis=1)
    directional_strength = (c - o) / total_range
    prev_c = c.shift(1)
    
    normalized = pd.DataFrame({
        'Date' : df.Date,
        'ctmString' : df.ctmString,
        'body_ratio': body / total_range,
        'upper_wick_ratio': (h - max_oc) / total_range,
        'lower_wick_ratio': (min_oc - l) / total_range,
        'directional_strength': directional_strength,
        'gap_open' : (o - prev_c) / prev_c,
        'momentum_continuity' : directional_strength * directional_strength.shift(1)
    })
    return normalized
