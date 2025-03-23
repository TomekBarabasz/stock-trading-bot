import numpy as np
std_markers = markers={'buy' : 0, 'sell' : 1}
std_print_to_console = lambda fmt,vals : print(fmt.format(*vals))

def generate_valid_intervals(df, trading_points, initial_cash, spread, min_profit, price_column = 'close', markers = std_markers):
    sm = markers['sell']
    bm = markers['buy']
    n_points = len(trading_points)
    cash = initial_cash
    valid_intervals = []
    for bi in range(n_points):
        if trading_points[bi][1] == bm:
            for si in range(bi+1,n_points):
                if trading_points[si][1] == sm:
                    buy_index = trading_points[bi][0]
                    sell_index= trading_points[si][0]
                    buy_price  = df.iloc[buy_index][price_column]
                    sell_price = df.iloc[sell_index][price_column]
                    shares =  np.floor(cash / buy_price)
                    if shares >= 1:
                        profit = (sell_price - buy_price - spread) * shares
                        if profit >= min_profit:
                            valid_intervals.append( (buy_index,sell_index,profit) )

    return valid_intervals
