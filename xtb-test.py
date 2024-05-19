import sys,argparse,json,re
from datetime import datetime,timedelta
from pathlib import Path
from xAPIConnector import APIClient,APIStreamClient,loginCommand, DEFAULT_XAPI_PORT_DEMO, DEFAULT_XAPI_PORT_REAL
from time import sleep
from utils import PeriodCodes

#import logging
#logger = logging.getLogger("jsonSocket")
#FORMAT = '[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s'
#logging.basicConfig(format=FORMAT)
#if DEBUG:
#    logger.setLevel(logging.DEBUG)
#else:
#    logger.setLevel(logging.CRITICAL)

def parse_timestamp(tm_str):
    def timestamp(date_):
        dt = date_-datetime(1970,1,1)
        return int(dt.total_seconds()*1000)

    if tm_str == 'now':
        return timestamp(datetime.utcnow())
    m = re.search('([-+])(\d+)([mdwhy])',tm_str)
    if m is not None:
        sign = m.groups()[0]
        n = int(m.groups()[1])
        unit = m.groups()[2]
        if unit == 'd':
            td = timedelta(days=n)
        elif unit == 'm':
            td = timedelta(days=n*30)
        elif unit == 'w':
            td = timedelta(weeks=n)
        elif unit == 'h':
            td = timedelta(hours=n)
        elif unit == 'y':
            td = timedelta(weeks=n*52)
        else:
            raise ValueError
        return timestamp(datetime.utcnow() - td if sign == '-' else datetime.utcnow() + td)
    else:
        return timestamp(datetime.fromisoformat(tm_str))

def cmdGetCandles(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('symbols',	        type=str,  nargs='+',help="symbol")
    parser.add_argument('-freq','-f',	    type=str,  choices=PeriodCodes.keys(), help="Period code")
    parser.add_argument('-start','-s',      type=str,  default='-5m', help="start timestamp")
    parser.add_argument('-end','-e',        type=str,  help="end timestamp")
    parser.add_argument('-out','-o',        type=Path, help="output filename")
    parser.add_argument('-uid','-u',        type=int,  help="user id")
    parser.add_argument('-password','-p',   type=str,  help="password")
    parser.add_argument('-real','-r',       action='store_true')
    parser.add_argument('-crypto',          action='store_true', help='symbol is crypto currency')
    Args = parser.parse_args(args)

    if Args.start is None:
        if Args.freq == 'M5':
            start_prm = '-5m'
        elif Args.freq == 'M15' or Args.freq == 'M30':
            start_prm = '-10m'
        elif Args.freq == 'H1':
            start_prm = '-12m'
    else:
        start_prm = Args.start
    
    port = DEFAULT_XAPI_PORT_REAL if Args.real else DEFAULT_XAPI_PORT_DEMO

    client = APIClient(port=port)
    loginResponse = client.execute(loginCommand(userId=Args.uid, password=Args.password))

    # check if user logged in correctly
    if(loginResponse['status'] == False):
        print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        return

    start = parse_timestamp(start_prm)
    end = parse_timestamp(Args.end) if Args.end is not None else None
    for sym in Args.symbols:
        print('get symbol',sym, end=' ')
        symbol_name = sym if Args.crypto else sym + '_9'
        response = getCandles(client, symbol_name , PeriodCodes[Args.freq], start, end)
        if response['status'] == True:
            print('done')
            filename = Args.out / f'{sym}_{Args.freq}.json'
            with (filename).open('w') as of:
                json.dump(response['returnData'],of)
        else:
            print('error',response['errorDescr'])
    client.disconnect()   

def getCandles(client, symbol, period, start, end):
    arguments= { 'info': {
        'symbol':symbol,
        'period':period,
        'start':start }
    }
    if end is not None: arguments['info']['end'] = end
    return client.commandExecute('getChartLastRequest' if end is None else 'getChartRangeRequest', arguments=arguments)

def cmdStreamCandles(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('symbols',	        type=str,  nargs='+', help="symbol")
    parser.add_argument('-freq','-f',	    type=str,  choices=PeriodCodes.keys(), help="Period code")
    parser.add_argument('-uid','-u',        type=int,  help="user id")
    parser.add_argument('-password','-p',   type=str,  help="password")
    parser.add_argument('-real','-r',       action='store_true')
    Args = parser.parse_args(args)

    port = DEFAULT_XAPI_PORT_REAL if Args.real else DEFAULT_XAPI_PORT_DEMO
    client = APIClient(port=port)
    loginResponse = client.execute(loginCommand(userId=Args.uid, password=Args.password))
    if(loginResponse['status'] == False):
        print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        return
    ssid = loginResponse['streamSessionId']
    print('Login ok, ssid = ',ssid)
    def procTick(msg): 
        print("TICK: ", msg)
    def procTrade(msg): 
        print("TRADE: ", msg)
    def procProfit(msg): 
        print("PROFIT: ", msg)
    def procTradeStatus(msg): 
        print("TRADE STATUS: ", msg)
    sclient = APIStreamClient(ssId=ssid, tickFun=procTick, tradeFun=procTrade, profitFun=procProfit, tradeStatusFun=procTradeStatus)
    print('streaming clint created')
    sclient.subscribePrices(Args.symbols)
    print('subscribing symbols',Args.symbols)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
    sclient.disconnect()
    client.disconnect()

def cmdGetAllSymbols(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-out','-o',        type=Path, help="output filename")
    parser.add_argument('-uid','-u',        type=int,  help="user id")
    parser.add_argument('-password','-p',   type=str,  help="password")
    parser.add_argument('-real','-r',       action='store_true')
    Args = parser.parse_args(args)

    port = DEFAULT_XAPI_PORT_REAL if Args.real else DEFAULT_XAPI_PORT_DEMO
    client = APIClient(port=port)
    loginResponse = client.execute(loginCommand(userId=Args.uid, password=Args.password, appName='bot'))

    # check if user logged in correctly
    if(loginResponse['status'] == False):
        print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        return

    response = client.commandExecute('getAllSymbols')
    client.disconnect()
    of = open(Args.out,'w')
    json.dump(response['returnData'],of)

if __name__ == '__main__':
    Cmds = {
        'getcan'    : cmdGetCandles,
        'getsym'    : cmdGetAllSymbols,
        'sc'        : cmdStreamCandles
    }
    if len(sys.argv) < 2 or sys.argv[1] not in Cmds:
        print('valid commands are :',' '.join(Cmds.keys()))
        exit(0)
    Cmds[sys.argv[1]](sys.argv[2:])
