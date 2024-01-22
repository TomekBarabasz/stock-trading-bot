import sys,argparse
from pathlib import Path

def main(Args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',	        type=Path,  nargs='+',help="candles data")
    parser.add_argument('-filter','-f',     type=str,  help="filter name to apply")
    parser.add_argument('-verbose','-v',    action='store_true')
    Args = parser.parse_args(sys.argv)
    main(Args)
