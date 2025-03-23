import re,argparse,sys,pickle
from pathlib import Path
from datetime import datetime
import pandas as pd

stock_o_bot_path = Path(__file__).parent.parent.parent
sys.path.append( str(stock_o_bot_path) )
from stock_o_bot.algorithms import (
    get_generate_trading_points_function, 
    get_generate_trading_points_methods, 
    get_optimal_trading_points_methods,
    get_optimal_trading_points_function,
    std_print_to_console
)
from stock_o_bot.xtb import read_json

# run windows
# python stock_o_bot\apps\generate_trading_points.py .\data\merged-upto-26-02-2025 ULTA.US_H1 --ema_span 3:5 --min_profit 10:20:5 --initial_cash 1000 --spread 1

# run linux
# python3 ./stock_o_bot/apps/generate_trading_points.py ./data/merged-upto-26-02-2025 ULTA.US_H1 --ema_span 3:5 --min_profit 10:20:5 --initial_cash 1000 --spread 1

parser = argparse.ArgumentParser()
parser.add_argument('data_folder',	    type=Path,   help='folder with data files')
parser.add_argument('data_file_regex',	type=str,   help='data filename as regex [allows processing more files]')
parser.add_argument('--tp_method',      type=str,   default='ema-vs-raw', choices=get_generate_trading_points_methods(),help="trading points generation method")
parser.add_argument('--method','-m',    type=str,   default='wis',        choices=get_optimal_trading_points_methods(), help="optimal trading pairs search method")
parser.add_argument('--len','-l',       type=int,   default=None, help="sublength")
parser.add_argument('--ema_span',       type=str,   default=5, help="ema_span")
parser.add_argument('--spread',         type=float, default=None, help="spread")
parser.add_argument('--min_profit',     type=str, default=None, help="min_profit")
parser.add_argument('--initial_cash',   type=float, default=None, help="min_profit")
parser.add_argument('--price_column',   type=str,   default='close', help="solving method")
parser.add_argument('--verbose','-v',   action='store_true')
parser.add_argument('--output','-o',    type=Path,   help="output folder")
Args = parser.parse_args()

def make_range(range_string):
    vals = list(map(int,range_string.split(':')))
    match len(vals):
        case 1:
            return range(vals[0],vals[0]+1)
        case 2:
            return range(vals[0],vals[1]+1)
        case 3:
            return range(vals[0],vals[1]+1,vals[2])
        case _:
            return None
ema_range = make_range(Args.ema_span)
min_profit_range = make_range(Args.min_profit)

generate_trading_points_function = get_generate_trading_points_function(Args.tp_method)
find_optimal_trading_points_function = get_optimal_trading_points_function(Args.method)

file_regex = re.compile(Args.data_file_regex)
for path in Args.data_folder.iterdir():
    if path.is_file() and file_regex.match(path.name):
        data = read_json(path) if path.suffix == '.json' else pd.read_pickle(path)
        print(f'found matching file {path.name} time span from {data.Date.min()} to {data.Date.max()}')
        for ema_span in ema_range:
            print(f'{ema_span=}')
            t0 = datetime.now()
            tp = generate_trading_points_function(data, ema_span=ema_span, price_col=Args.price_column)
            print(f'generated {len(tp)} trading points in {datetime.now()-t0}')
            for min_profit in min_profit_range:
                print(f'{min_profit=}')
                t0 = datetime.now()
                Results = find_optimal_trading_points_function(data,tp,initial_cash=Args.initial_cash,spread=Args.spread,min_profit=min_profit,price_column=Args.price_column,verbose_fn=std_print_to_console)
                print(f'search done . total profit {Results[0][0]} exec time {datetime.now() - t0}')
                if len(Results):
                    pickle.dump(Results[0], (Args.output / f'{path.name}_trades_{ema_span}_{min_profit}.pkl').open('wb'))

