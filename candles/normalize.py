import pandas as pd

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
