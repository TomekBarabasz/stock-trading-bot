import json
from datetime import datetime, timedelta
import pandas as pd

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
