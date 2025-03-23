import re,argparse,sys
from pathlib import Path
stock_o_bot_path = Path(__file__).parent.parent.parent
sys.path.append( str(stock_o_bot_path) )
from stock_o_bot.utils import collect_symbols_data,merge_data

parser = argparse.ArgumentParser()
parser.add_argument('data_folder',	   type=Path,   help='folder with input subfolders')
parser.add_argument('--output','-o',   type=Path,   help='output folder')
parser.add_argument('--all_folders', '-a', action='store_true')
Args = parser.parse_args()

name_regex = None if Args.all_folders else re.compile(r'\d\d-\d\d-\d\d\d\d')
Symbols = collect_symbols_data(Args.data_folder,name_regex)

for symbol,files in Symbols.items():
    if symbol.startswith('symbol'):
        continue
    print(f'merging {symbol}')
    merged = merge_data(files)
    merged.to_pickle( Args.output / symbol)

