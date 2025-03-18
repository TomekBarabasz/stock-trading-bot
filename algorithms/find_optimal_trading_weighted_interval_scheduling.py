from .common import std_markers,std_print_to_console,generate_valid_intervals
from datetime import datetime

# Nice explanation:
# https://cs-people.bu.edu/januario/teaching/cs330/su23/slides/CS330-Lec10-with-notes.pdf
def find_optimal_trading_points__wis(df, trading_points, initial_cash, spread, min_profit, price_column = 'close', markers = std_markers, verbose_fn = std_print_to_console):
    verbose_fn('creating intervals ...',())
    t0 = datetime.now()
    intervals = generate_valid_intervals(df, trading_points, initial_cash, spread, min_profit, price_column, markers)
    verbose_fn('created {} intervals [{}]', (len(intervals),datetime.now()-t0))

    # sort by finish time
    intervals.sort(key = lambda x : x[1])

    memo = [0] * len(intervals)

    def find_latest_compatible(n):
        for i in reversed(range(n)):
            if intervals[i][1] <= intervals[n][0]:
                return i
        return 0
    
    verbose_fn('filling memo table ...',())
    t0 = datetime.now()
    for i in range(1,len(intervals)):
        memo[i] = max(intervals[i][2] + memo[find_latest_compatible(i)], memo[i-1])
    verbose_fn('done [{}]',(datetime.now()-t0,))

    selected_intervals = []

    n = len(memo)-1
    while n != 0:
        compatible_index = find_latest_compatible(n)
        if intervals[n][2] + memo[compatible_index] > memo[n-1]:
            selected_intervals.append( intervals[n] )
            n = compatible_index
        else:
            n = n-1

    selected_intervals.reverse()
    total_profit = sum([i[2] for i in selected_intervals])
    return [(total_profit,selected_intervals)]
