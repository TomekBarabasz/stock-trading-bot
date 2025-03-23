import numpy as np
from .common import std_markers,std_print_to_console,generate_valid_intervals
from datetime import datetime

def build_greedy_solution(intervals, n_points):
    trading_pairs = []
    total_profit = 0
    current_start = 0
    while current_start < n_points:
        pass    

    return [(total_profit,trading_pairs)]

def weighted_interval_scheduling(interval_subset):
    """
    Solve a standard Weighted Interval Scheduling on the 'interval_subset'
    using DP in O(n log n) time. Returns the subset of intervals that yields
    maximum total profit.
    
    interval_subset: list of (start, end, profit)
    """
    if not interval_subset:
        return []
    
    # Sort by end time
    sorted_by_end = sorted(interval_subset, key=lambda x: x[1])
    n = len(sorted_by_end)
    
    # Precompute p(i): for each i, the largest j < i s.t. intervals j and i don't overlap
    ends = [iv[1] for iv in sorted_by_end]
    starts = [iv[0] for iv in sorted_by_end]
    
    p = [0]*n
    for i in range(n):
        (si, ei, pi) = sorted_by_end[i]
        # Find rightmost interval j < i with end_j <= start_i
        # We can use binary search on the 'ends' array
        j = bisect_right(ends, si) - 1
        p[i] = j  # j might be -1 if none fit
    
    # dp[i] = max profit using intervals up to index i
    dp = [0]*(n+1)
    
    # Keep track of choices for reconstruction
    choice = [False]*n  # whether we pick interval i
    
    for i in range(1, n+1):
        # i-1 is the index in sorted_by_end
        (si, ei, pi) = sorted_by_end[i-1]
        # Option 1: skip interval i-1
        if dp[i-1] >= dp[p[i-1]+1] + pi:
            dp[i] = dp[i-1]
            choice[i-1] = False
        else:
            dp[i] = dp[p[i-1]+1] + pi
            choice[i-1] = True
    
    # Backtrack to get solution intervals
    selected = []
    i = n
    while i > 0:
        if choice[i-1]:
            selected.append(sorted_by_end[i-1])
            i = p[i-1] + 1
        else:
            i -= 1
    selected.reverse()
    return selected
    
def find_optimal_trading_points__improve_greedy(df, trading_points, initial_cash, spread, min_profit, price_column = 'close', markers = std_markers, verbose_fn = std_print_to_console):
    intervals = generate_valid_intervals(df, trading_points, initial_cash, spread, min_profit, price_column, markers)
    verbose_fn('created {} intervals', (len(intervals),))
    from bisect import bisect_right
    n_points = len(trading_points)
    greedy = build_greedy_solution(intervals, n_points)
    total_profit = 0
    for i in greedy:
        total_profit += i[2]
    return [(total_profit,greedy)]
