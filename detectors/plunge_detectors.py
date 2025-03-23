import numpy as np
from sklearn.linear_model import LinearRegression

def rate_of_change_detector(df, threshold_pct = 3, n_intervals = 1, column_name='close'):
    threshold = threshold_pct / 100.0
    roc = df[column_name].pct_change(periods=n_intervals)
    mask = roc > threshold if threshold > 0 else roc < threshold
    return df.index[mask]

def ma_detector(df, short_span=3,long_span=7, ma_type='sma', column_name='close'):
    df = df.copy()
    match ma_type:
        case 'sma':
            df['short_ma'] = df[column_name].rolling(window=short_span).mean()
            df['long_ma']  = df[column_name].rolling(window= long_span).mean()
        case 'ema':
            df['short_ma'] = df[column_name].ewm(span=short_span, adjust=False).mean()
            df['long_ma']  = df[column_name].ewm(span= long_span, adjust=False).mean()
        case _:
            return None
    df.dropna(subset=['short_ma', 'long_ma'], inplace=True)
    
    # Trend-change indicator:
    #   +1 = uptrend starts (short_ma crosses above long_ma)
    #   -1 = downtrend starts (short_ma crosses below long_ma)
    #    0 = no change
    df['trend_change'] = 0

    # Compare current row's MA difference to previous row's
    # ma_diff > 0 => short_ma > long_ma (potential uptrend)
    # ma_diff < 0 => short_ma < long_ma (potential downtrend)
    df['ma_diff'] = df['short_ma'] - df['long_ma']

    # Check if there is a crossover from negative to positive (down to up)
    df.loc[
        (df['ma_diff'] > 0) & (df['ma_diff'].shift(1) <= 0),
        'trend_change'
    ] = 1
    
    # Check if there is a crossover from positive to negative (up to down)
    df.loc[
        (df['ma_diff'] < 0) & (df['ma_diff'].shift(1) >= 0),
        'trend_change'
    ] = -1

    trend_changes = df[df['trend_change'] != 0]
    return trend_changes['trend_change']

def macd_detector(df, short_span=12,long_span=26, signal_span=9, column_name='close'):
    df = df.copy()
    
    # 1. Calculate the short-term and long-term EMAs
    df['EMA_short'] = df[column_name].ewm(span=short_span, adjust=False).mean()
    df['EMA_long'] = df[column_name].ewm(span=long_span, adjust=False).mean()
    
    # 2. Calculate MACD and the signal line
    df['MACD'] = df.EMA_short - df.EMA_long
    df['Signal'] = df.MACD.ewm(span=signal_span, adjust=False).mean()
    
    # 3. Determine the MACD histogram (MACD minus signal)
    df['MACD_hist'] = df.MACD - df.Signal
    
    # 4. Define the 'Trend' based on whether MACD is above (+1) or below (-1) the signal
    df['trend'] = 0
    df.loc[df.MACD_hist > 0, 'trend'] =  1
    df.loc[df.MACD_hist < 0, 'trend'] = -1
    trend_change = df.trend.ne(df.trend.shift())
    
    # skip trend=0 at index 0
    return df.loc[trend_change,'trend'][1:]

def linreg_detector(df, window=5, slope_threshold=0.0, column_name='close'):
    df = df.copy()  # Work on a copy to avoid modifying the original
    
    # --- 1) Calculate slopes in a rolling manner ---
    # We'll store slopes in a new column 'slope'
    slopes = [np.nan] * (window - 1)  # first `window-1` are NaN, because no regression yet
    
    for i in range(window - 1, len(df)):
        # Take the slice of length 'window'
        y = df[column_name].iloc[i - window + 1 : i + 1].values
        x = np.arange(window).reshape(-1, 1)
        
        # Fit LinearRegression
        model = LinearRegression()
        model.fit(x, y)
        
        # slope is model.coef_[0]
        slope_val = model.coef_[0]
        slopes.append(slope_val)
    
    df["slope"] = slopes
    
    # --- 2) Define "trend_label" from slope sign ---
    # If slope > slope_threshold -> +1 (uptrend)
    # If slope < -slope_threshold -> -1 (downtrend)
    # Otherwise 0 (flat / neutral)
    def slope_to_trend_label(slope):
        if slope > slope_threshold:
            return 1  # uptrend
        elif slope < -slope_threshold:
            return -1  # downtrend
        else:
            return 0  # flat
    
    df["trend_label"] = df["slope"].apply(slope_to_trend_label)
    
    # --- 3) Identify trend changes in 'trend_label' ---
    # A trend change occurs if trend_label goes from +1 to -1 or -1 to +1.
    df["trend_label_shift"] = df["trend_label"].shift(1)
    
    # We'll define a "change" column to see the difference
    df["change"] = df["trend_label"] - df["trend_label_shift"]
    # +2 means a jump from -1 to +1
    # -2 means a drop from +1 to -1
    
    # Filter where "change" is ±2 to get sign flips
    change_mask = (df["change"] == 2) | (df["change"] == -2)
    trend_change_points = df[change_mask]
    
    # Cleanup (optional): remove helper column used for shift
    df.drop(columns=["trend_label_shift", "change"], inplace=True)
    
    return df, trend_change_points

def on_balance_volume_detector(df, **kwargs):
    pass

DetectorsByName = {
    'rate-of-change'  : rate_of_change_detector,
    'moving-averages' : ma_detector,
    'moving-average-convergence-divergence' : macd_detector,
    'linear-regression' : linreg_detector
}

def get_detector_names():
    return list(DetectorsByName.keys())

def get_detector(name):
    return DetectorsByName.get(name,None)
