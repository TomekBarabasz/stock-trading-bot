import sys
sys.path.append(r"C:\tomek\projects\stock")
import argparse
from stock_o_bot.algorithms import *
from stock_o_bot.xtb import read_json
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('datafile',	   type=str,   help='data source filename')
parser.add_argument('--method','-m',   type=str,   default=None, help="solving method")
parser.add_argument('--len','-l',   type=int,   default=None, help="sublength")
parser.add_argument('--ema_span',   type=int,   default=5, help="ema_span")
parser.add_argument('--spread',     type=float, default=None, help="spread")
parser.add_argument('--min_profit', type=float, default=None, help="min_profit")
parser.add_argument('--initial_cash', type=float, default=None, help="min_profit")
parser.add_argument('--verbose','-v', action='store_true')
Args = parser.parse_args(sys.argv[1:])

#datafile = r'.\data\01-02-2024\MRVL.US_H1.json'
data = read_json(Args.datafile)
if Args.len is not None:
    data = data.iloc[0:Args.len] 

ref_trades, ref_total_profit, ref_cash = simulate_trading_all_in_one(data, Args.ema_span, Args.initial_cash, Args.spread, Args.min_profit, price_col='close')
print(f'ref results : n_trades {len(ref_trades)} total_profit {ref_total_profit:.1f} cash {ref_cash:.1f}')
for t in ref_trades:
    print(t)

if Args.verbose:
    verbose_fn = std_print_to_console
else:
    verbose_fn = lambda f,v: None

t0 = datetime.now()
tp = find_trading_points_0(data, ema_span=Args.ema_span, price_col='close')
match Args.method:
    case 'search':
        trading = find_best_trading_points(data,tp,initial_cash=Args.initial_cash,spread=Args.spread,min_profit=Args.min_profit,price_column='close',verbose_fn=verbose_fn)
        t1 = datetime.now()
        print(trading)
    case 'ilp':
        intervals = generate_valid_intervals(data, tp, Args.initial_cash, Args.spread, Args.min_profit, price_column = 'close', verbose_fn = std_print_to_console)
        print(f'created {len(intervals)} intervals')
        max_profit, chosen_intervals = solve_interval_scheduling_ILP(intervals)
        t1 = datetime.now()
        print(f'{max_profit=} {chosen_intervals=}')

print(f'solved in {t1-t0}')
#python .\stock_o_bot\test\test_trading_points.py .\data\01-02-2024\MRVL.US_H1.json --spread 1 --min_profit 10 --initial_cash 1000
