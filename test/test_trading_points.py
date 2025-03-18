import sys
sys.path.append(r"C:\tomek\projects\stock")
import argparse
from stock_o_bot.algorithms import (
    get_generate_trading_points_function, 
    get_generate_trading_points_methods, 
    get_optimal_trading_points_methods,
    get_optimal_trading_points_function,
    std_print_to_console
)
from stock_o_bot.xtb import read_json
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('datafile',	   type=str,   help='data source filename')
parser.add_argument('--tp_method', type=str,   default='ema-vs-raw', choices=get_generate_trading_points_methods(),help="solving method")
parser.add_argument('--method','-m',   type=str,   default='wis', choices=get_optimal_trading_points_methods(),help="solving method")
parser.add_argument('--len','-l',   type=int,   default=None, help="sublength")
parser.add_argument('--ema_span',   type=int,   default=5, help="ema_span")
parser.add_argument('--spread',     type=float, default=None, help="spread")
parser.add_argument('--min_profit', type=float, default=None, help="min_profit")
parser.add_argument('--initial_cash', type=float, default=None, help="min_profit")
parser.add_argument('--price_column',  type=str,   default='close', help="solving method")
parser.add_argument('--verbose','-v', action='store_true')
parser.add_argument('--print_trades', action='store_true')
Args = parser.parse_args(sys.argv[1:])

#datafile = r'.\data\01-02-2024\MRVL.US_H1.json'
data = read_json(Args.datafile)
if Args.len is not None:
    data = data.iloc[0:Args.len] 
print('nbr of data points ', len(data))

t0 = datetime.now()
generate_trading_points_function = get_generate_trading_points_function(Args.tp_method)
if generate_trading_points_function is None:
    print('invalid trade point genration method')
    exit(1)
tp = generate_trading_points_function(data, ema_span=Args.ema_span, price_col=Args.price_column)
print(f'generated {len(tp)} trading points in {datetime.now()-t0}')

ref_trading_function = get_optimal_trading_points_function('greedy')
ref_results = ref_trading_function(data, tp, Args.initial_cash, Args.spread, Args.min_profit, price_column=Args.price_column, verbose_fn = lambda f,v : None)
print(f'ref results [greedy]: total_profit = {ref_results[0][0]:.1f} nbr trades = {len(ref_results[0][1])}')
if Args.print_trades:
    for t in ref_results[0]:
        print(t)

if Args.verbose:
    verbose_fn = std_print_to_console
else:
    verbose_fn = lambda f,v: None

find_optimal_trading_points_function = get_optimal_trading_points_function(Args.method)
if find_optimal_trading_points_function is None:
    print('invalid method')
    exit(1)

print('starting search...')
t0 = datetime.now()
Results = find_optimal_trading_points_function(data,tp,initial_cash=Args.initial_cash,spread=Args.spread,min_profit=Args.min_profit,price_column=Args.price_column,verbose_fn=verbose_fn)
print(f'search done in {datetime.now() - t0}')
print(f'total_profit = {Results[0][0]:.1f} nbr trades = {len(Results[0][1])}')
if Args.print_trades:
    for total_profit, trading_points in Results:
        print(f'{total_profit=} nbr trading points {len(trading_points)}')
        for _tp in trading_points:
            print(_tp)

#python .\stock_o_bot\test\test_trading_points.py .\data\01-02-2024\MRVL.US_H1.json --spread 1 --min_profit 10 --initial_cash 1000
