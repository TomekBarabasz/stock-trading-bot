import sys
import argparse
from pathlib import Path
from ..data_source import createDataSource, DataReceiver

class TestReceiver(DataReceiver):
    def receiveSymbol(self,symbol, data):
        print('symbol=',symbol,'data=',data)

# how to run:
# python3 -m stock_o_bot.test.test_datasource <filename>
# python3 -m stock_o_bot.test.test_datasource ./data/09-01-2024/AMD.US_H1.json -d 0.1
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',	   type=str,   help='data source filename')
    parser.add_argument('-start','-s', type=int,   default=None, help="start timestamp")
    parser.add_argument('-end','-e',   type=str,   default=None, help="end timestamp")
    parser.add_argument('-delay','-d', type=float, default=None, help="real time delay")
    Args = parser.parse_args(sys.argv[1:])
   
    kwargs = {"filename" : Args.filename, "delay" : Args.delay, "start_timestamp" : Args.start}
    ds = createDataSource('file', **kwargs)
    rec = TestReceiver()
    ds.registerForSymbol('AA',None,rec)
    ds.start()
