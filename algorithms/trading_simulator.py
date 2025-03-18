import numpy as np
from .common import std_markers

def execute_trading_points(df, trading_points, initial_cash,  spread, min_profit, price_col='close', markers = std_markers):
    """   
    Parameters:
    - df: pandas DataFrame with stock price data (index as time, price_col as price)
    - initial_cash: starting cash amount to invest (default: 1000.0)
    - price_col: column name containing the price data (default: 'Close')
    - ema_span: span for the EMA (default: 10, controls smoothing)
    - spread: transaction cost per share per trade (default: 0.02)
    - min_profit: minimum profit required per trade (default: 0.50)
    
    Returns:
    - trades: list of dictionaries with buy/sell dates, prices, shares, and profit
    - total_profit: total profit after all trades
    - final_cash: final cash balance after all trades
    """
    
    sell_marker = markers['sell']
    buy_marker  = markers['buy']
    
    # Track trades and cash
    trades = []
    total_profit = 0.0
    cash = initial_cash    
    last_buy_price = None
    shares = 0

    for iloc,type in trading_points:
        price = df.iloc[iloc][price_col]
        date = df.iloc[iloc].Date
        if type == buy_marker:
            new_shares = np.floor(cash / price)
            if new_shares > 1:
                trades.append({
                    'iloc'  : iloc,
                    'date'  : date,
                    'type'  : type,
                    'price' : price,
                    'shares': shares,
                    'cash'  : cash
                })
                shares += new_shares
                cash -= new_shares * price
                last_buy_price = price
        elif type == sell_marker and shares > 0:
            profit_per_share = (price - last_buy_price) - spread
            trade_profit = shares * profit_per_share
            if trade_profit >= min_profit:
                cash   += shares * (price - spread)
                shares = 0
                trades.append({
                    'iloc'  : iloc,
                    'date'  : date,
                    'type'  : type,
                    'price' : price,
                    'shares': shares,
                    'cash'  : cash
                })
                total_profit += trade_profit
        
    return trades, total_profit, cash

# NOTE: this is wrong : stupid ChatGPT o1 made it wrong 
# thading intervals overlap - neeed to fix or
def _wrong_simulate_trading_all_in_one(df, ema_span=10, initial_cash=1000.0, spread=0.02, min_profit=0.50, price_col='close'):
    """
    Vectorized function to find optimal buy/sell points using EMA, with initial cash, transaction costs, and min profit.
    
    Parameters:
    - df: pandas DataFrame with stock price data (index as time, price_col as price)
    - initial_cash: starting cash amount to invest (default: 1000.0)
    - price_col: column name containing the price data (default: 'Close')
    - ema_span: span for the EMA (default: 10, controls smoothing)
    - spread: transaction cost per share per trade (default: 0.02)
    - min_profit: minimum profit required per trade (default: 0.50)
    
    Returns:
    - trades: list of dictionaries with buy/sell dates, prices, shares, and profit
    - total_profit: total profit after all trades
    - final_cash: final cash balance after all trades
    """
    # Ensure DataFrame is copied to avoid modifying the original
    df = df.copy()
    
    # Calculate EMA
    df['EMA'] = df[price_col].ewm(span=ema_span, adjust=False).mean()
    
    # Shift prices and EMA for comparison
    df['Price_Prev'] = df[price_col].shift(1)
    df['Price_Next'] = df[price_col].shift(-1)
    df['EMA_Prev'] = df['EMA'].shift(1)
    
    # Detect buy signals: price crosses below EMA and starts rising
    buy_signals = (
        (df[price_col] < df['EMA']) &  # Price below EMA
        (df['Price_Prev'] >= df[price_col]) &  # Local minimum
        (df['Price_Next'] > df[price_col])  # Price starts rising
    )
    
    # Detect sell signals: price crosses above EMA and peaks
    sell_signals = (
        (df[price_col] > df['EMA']) &  # Price above EMA
        (df['Price_Prev'] <= df[price_col]) &  # Local maximum
        (df['Price_Next'] < df[price_col])  # Price starts falling
    )
    
    # Get buy and sell indices
    buy_idx = df.index[buy_signals]
    sell_idx = df.index[sell_signals]
    
    # Track trades and cash
    trades = []
    total_profit = 0.0
    cash = initial_cash
    buy_ptr = 0
    sell_ptr = 0
    
    while buy_ptr < len(buy_idx) and sell_ptr < len(sell_idx):
        buy_date = buy_idx[buy_ptr]
        sell_date = sell_idx[sell_ptr]
        
        # Ensure sell comes after buy
        if sell_date <= buy_date:
            sell_ptr += 1
            continue
        
        buy_price = df.loc[buy_date, price_col]
        sell_price = df.loc[sell_date, price_col]
        
        # Calculate shares to buy with available cash (floor to avoid fractional shares)
        shares = np.floor(cash / buy_price)
        if shares < 1:  # Not enough cash to buy even 1 share
            break
        
        # Profit per share, adjusted for spread
        profit_per_share = (sell_price - buy_price) - spread
        trade_profit = shares * profit_per_share
        
        if trade_profit >= min_profit:
            # Update cash: sell proceeds minus spread cost
            cash = shares * sell_price - shares * spread
            trades.append({
                'buy_date': buy_date,
                'buy_price': buy_price,
                'sell_date': sell_date,
                'sell_price': sell_price,
                'shares': shares,
                'profit': trade_profit
            })
            total_profit += trade_profit
        
        # Move to next buy/sell pair
        buy_ptr += 1
        sell_ptr += 1
    
    return trades, total_profit, cash
