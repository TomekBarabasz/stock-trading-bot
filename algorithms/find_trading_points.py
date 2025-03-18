import numpy as np
from .common import std_markers,std_print_to_console,generate_valid_intervals
from datetime import datetime
from .find_optimal_trading_improve_greedy import find_optimal_trading_points__improve_greedy
from .find_optimal_trading_weighted_interval_scheduling import find_optimal_trading_points__wis

def generate_trading_points__ema_vs_raw(df, ema_span=5, price_col='close', markers = std_markers):
    """
    Vectorized function to find optimal buy/sell points using EMA.
    
    Parameters:
    - df: pandas DataFrame with stock price data (index as time, price_col as price)
    - price_col: column name containing the price data (default: 'Close')
    - ema_span: span for the EMA (default: 10, controls smoothing)
    
    Returns:
    - trade_points: list of tuples (idx,marker)
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
    signals  = [(i, markers[ 'buy']) for i in df.index[ buy_signals]]
    signals += [(i, markers['sell']) for i in df.index[sell_signals]]

    return sorted(signals, key = lambda x : x[0])

def generate_trading_points__ema_diff(df, ema_span=5, price_col='close', markers = std_markers):
    df = df.copy()

    # Calculate EMA
    df['EMA'] = df[price_col].ewm(span=ema_span, adjust=False).mean()
    df = df.reset_index(drop=True)
    diff = df.EMA.diff()
    diff1 = diff.shift(-1)
    zeros = diff[ np.sign(diff) != np.sign(diff1) ].index
    sm = markers['sell']
    bm = markers['buy']
    types = [sm if diff[z] > 0 else bm for z in zeros]

    return list(zip(zeros,types))

Trading_points_functions = {
    'ema-vs-raw' : generate_trading_points__ema_vs_raw,
    'ema-diff'   : generate_trading_points__ema_diff
}
def get_generate_trading_points_methods():
    return list(Trading_points_functions.keys())

def get_generate_trading_points_function(method):
    return Trading_points_functions.get(method,None)

def find_optimal_trading_points__search(df, trading_points, initial_cash, spread, min_profit, price_column = 'close', markers = std_markers, verbose_fn = std_print_to_console):
    sm = markers['sell']
    bm = markers['buy']
    n_points = len(trading_points)
    search_horizon = [(0, [], initial_cash, 0)]
    BestTrading = []
    total_sequences_checked = 0
    t0 = datetime.now()
    while len(search_horizon) > 0:
        t1 = datetime.now()
        if (t1-t0).total_seconds() > 1:
            best_profit = BestTrading[0][0] if len(BestTrading) > 0 else 0
            print(f' horizon size {len(search_horizon)} {best_profit=:.1f} {total_sequences_checked=}',end='\r')
        start, pairs, cash, total_profit = search_horizon.pop(-1)
        verbose_fn('pop start={} pairs={} cash={:.1f} total_profit={:.1f}', (start,pairs,cash,total_profit))
        pairs_added = 0
        for bi in range(start,n_points):
            if trading_points[bi][1] == bm:
                for si in range(bi+1,n_points):
                    if trading_points[si][1] == sm:
                        buy_price  = df.iloc[trading_points[bi][0]][price_column]
                        sell_price = df.iloc[trading_points[si][0]][price_column]
                        shares =  np.floor(cash / buy_price)
                        rest = cash - shares * buy_price
                        verbose_fn('\ttrying ({},{}) shares {} profit {}',(bi,si,shares,(sell_price - buy_price - spread) * shares))
                        if shares > 1:
                            profit = (sell_price - buy_price - spread) * shares
                            if profit > min_profit:
                                cash_after_sell = rest + shares * (sell_price-spread)
                                search_horizon.append( (si+1, pairs + [(bi,si)], cash_after_sell, total_profit + profit) )
                                a,b,c,d = search_horizon[-1]
                                verbose_fn('\tappend start={} pairs={} cash={:.1f} current_profit {:.1f} total_profit={:.1f}', (a,b,c,profit,d))
                                pairs_added += 1
        if pairs_added == 0:
            total_sequences_checked = total_sequences_checked + 1
            verbose_fn('\tend of sequence',())
            if len(BestTrading) > 0:
                if total_profit > BestTrading[0][0]:
                    #BestTrading = [(total_profit, pairs, cash)]
                    BestTrading = [(total_profit, pairs)]
                    verbose_fn('\treplace best trading',())
                elif total_profit == BestTrading[0][0]:
                    #BestTrading.append( (total_profit, pairs, cash) )
                    BestTrading.append( (total_profit, pairs) )
                    verbose_fn('\tappend to best trading',())
            else:
                #BestTrading = [(total_profit, pairs, cash)]
                BestTrading = [(total_profit, pairs)]
                verbose_fn('\tappend to best trading',())
    return BestTrading

def solve_interval_scheduling_ILP(intervals, solver=None):
    from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, PULP_CBC_CMD

    # 1) Create an LP problem.
    #    LpMaximize indicates we want to maximize our objective.
    prob = LpProblem("WeightedIntervalScheduling", LpMaximize)

    # 2) Create binary decision variables for each interval.
    #    x[i] = 1 if we choose interval i, 0 otherwise
    x = {
        i: LpVariable(f"x_{i}", cat=LpBinary)
        for i in range(len(intervals))
    }
    # 3) Add constraints: no two chosen intervals can overlap.
    #    Overlap condition: intervals i and j overlap if i.start < j.end and j.start < i.end.
    for i in range(len(intervals)):
        start_i, end_i, profit_i = intervals[i]
        for j in range(i + 1, len(intervals)):
            start_j, end_j, profit_j = intervals[j]
            # Check if i and j overlap
            if not (end_i <= start_j or end_j <= start_i):
                # They overlap => x_i + x_j <= 1
                prob += x[i] + x[j] <= 1, f"no_overlap_{i}_{j}"

    # 4) Define the objective: maximize total profit
    prob += lpSum([intervals[i][2] * x[i] for i in range(len(intervals))]), "TotalProfit"

    # 5) Solve the problem
    if solver is None:
        # Default solver is CBC in PuLP. You can pass any other solver you have installed.
        solver = PULP_CBC_CMD(msg=0,threads=12)  # msg=0 => silence solver output

    print('starting solve')
    prob.solve(solver)

    # 6) Collect the results
    max_profit = prob.objective.value()
    chosen_intervals = []
    for i in range(len(intervals)):
        if x[i].varValue > 0.5:  # means x[i] == 1
            chosen_intervals.append(intervals[i])

    return max_profit, chosen_intervals

def find_optimal_trading_points__ILP(df, trading_points, initial_cash, spread, min_profit, price_column = 'close', markers = std_markers, verbose_fn = std_print_to_console):
    intervals = generate_valid_intervals(df, trading_points, initial_cash, spread, min_profit, price_column, markers)
    verbose_fn('created {} intervals', (len(intervals),))
    max_profit, chosen_intervals = solve_interval_scheduling_ILP(intervals)
    return [(max_profit, chosen_intervals)]

def find_optimal_trading_points__local_search(df, trading_points, initial_cash, spread, min_profit, price_column = 'close', markers = std_markers, verbose_fn = std_print_to_console):
    pass

def find_optimal_trading_points__greedy(df, trading_points, initial_cash, spread, min_profit, price_column = 'close', markers = std_markers, verbose_fn = std_print_to_console):
    sm = markers['sell']
    bm = markers['buy']
    n_points = len(trading_points)
    cash = initial_cash
    total_profit = 0
    trading_pairs = []
    bi = 0
    while bi < n_points:
        if trading_points[bi][1] == bm:
            found_si = False
            for si in range(bi+1,n_points):
                if trading_points[si][1] == sm:
                    buy_price  = df.iloc[trading_points[bi][0]][price_column]
                    sell_price = df.iloc[trading_points[si][0]][price_column]
                    shares =  np.floor(cash / buy_price)
                    rest = cash - shares * buy_price
                    #verbose_fn('\ttrying ({},{}) shares {} profit {}',(bi,si,shares,(sell_price - buy_price - spread) * shares))
                    if shares > 1:
                        profit = (sell_price - buy_price - spread) * shares
                        if profit > min_profit:
                            verbose_fn('\texecuting ({},{}) shares {} profit {:.1f}',(bi,si,shares,profit))
                            total_profit += profit
                            cash = rest + shares * (sell_price-spread)
                            trading_pairs.append( (bi,si,profit) )
                            found_si = True
                            break
            bi = bi + 1 if not found_si else si + 1
        else:
            bi = bi + 1                
    return [(total_profit, trading_pairs)]

Optimal_Trading_points_functions = {
    'search' : find_optimal_trading_points__search,
    'ilp'    : find_optimal_trading_points__ILP,
    'local-search' : find_optimal_trading_points__local_search,
    'greedy' : find_optimal_trading_points__greedy,
    'improve-greedy' : find_optimal_trading_points__improve_greedy,
    'wis' : find_optimal_trading_points__wis
}

def get_optimal_trading_points_methods():
    return list(Optimal_Trading_points_functions.keys())

def get_optimal_trading_points_function(method):
    return Optimal_Trading_points_functions.get(method,None)
