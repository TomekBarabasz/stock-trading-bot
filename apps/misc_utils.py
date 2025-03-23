import re,argparse,sys,pickle
from pathlib import Path
from datetime import datetime
import pandas as pd

stock_o_bot_path = Path(__file__).parent.parent.parent
sys.path.append( str(stock_o_bot_path) )
from stock_o_bot.algorithms import (
    get_generate_trading_points_function, 
    get_generate_trading_points_methods, 
    generate_valid_intervals,
    std_markers
)
from stock_o_bot.xtb import read_json

def gen_int(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',	     type=Path,   help='input filename')
    parser.add_argument('--tp_method',   type=str,   default='ema-vs-raw', choices=get_generate_trading_points_methods(),help="trading points generation method")
    parser.add_argument('--price_column',type=str,   default='close', help="price column name")
    parser.add_argument('--ema_span',    type=int,   default=5,    help="ema_span")
    parser.add_argument('--initial_cash',type=float, default=1000, help="min_profit")
    parser.add_argument('--spread',      type=float, default=None, help="spread")
    parser.add_argument('--min_profit',  type=float, default=None, help="min_profit")
    parser.add_argument('--output','-o', type=Path,                help='output filename')
    Args = parser.parse_args(args)

    data = read_json(Args.filename) if Args.filename.suffix == '.json' else pd.read_pickle(Args.filename)
    generate_trading_points_function = get_generate_trading_points_function(Args.tp_method)
    tp = generate_trading_points_function(data, ema_span=Args.ema_span, price_col=Args.price_column)
    print(f'generated {len(tp)} trading points')
    intervals = generate_valid_intervals(data, tp, Args.initial_cash, Args.spread, Args.min_profit, Args.price_column, std_markers)
    print(f'generated {len(intervals)} intervals')
    if Args.output.suffix == '.bin':
        from struct import pack
        with open(Args.output,'wb') as out:
            out.write( pack('I',len(intervals)) )
            for i in intervals:
                out.write( pack('IIf', *i) )
    else:
        with open(Args.output,'w') as out:
            for i in intervals:
                out.write( f'{i[0]},{i[1]},{i[2]:.2f}\n' )

def gen_tp(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',	     type=Path,   help='input filename')
    parser.add_argument('--tp_method',   type=str,   default='ema-vs-raw', choices=get_generate_trading_points_methods(),help="trading points generation method")
    parser.add_argument('--price_column',type=str,   default='close', help="price column name")
    parser.add_argument('--ema_span',    type=int,   default=5,    help="ema_span")
    parser.add_argument('--output','-o', type=Path,                help='output filename')
    Args = parser.parse_args(args)

    data = read_json(Args.filename) if Args.filename.suffix == '.json' else pd.read_pickle(Args.filename)
    generate_trading_points_function = get_generate_trading_points_function(Args.tp_method)
    tp = generate_trading_points_function(data, ema_span=Args.ema_span, price_col=Args.price_column)
    print(f'generated {len(tp)} trading points')

    if Args.output.suffix == '.bin':
        from struct import pack
        with open(Args.output,'wb') as out:
            out.write( pack('I',len(tp)) )
            for i in tp:
                out.write( pack('IIf', *i) )
    else:
        with open(Args.output,'w') as out:
            for i in tp:
                out.write( f'{i[0]},{i[1]},{i[2]:.2f}\n' )

Cmds = {'generate-intervals'      : gen_int,
        'generate-trading-points' : gen_tp
        }

if len(sys.argv) < 2 or sys.argv[1] not in Cmds.keys():
    print('invalid command, try one of ', ','.join(Cmds.keys()))

cmd = sys.argv[1]
print(f'{cmd=}')
Cmds[cmd](sys.argv[2:])
