import sys,argparse,json
from datetime import datetime
from pathlib import Path
from xAPIConnector import APIClient,APIStreamClient,loginCommand

#import logging
#logger = logging.getLogger("jsonSocket")
#FORMAT = '[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s'
#logging.basicConfig(format=FORMAT)
#if DEBUG:
#    logger.setLevel(logging.DEBUG)
#else:
#    logger.setLevel(logging.CRITICAL)

PeriodCodes = { 'M1':1,
                'M5':5,
                'M15':15,
                'M30':30,
                'H1':60,
                'H4':240,
                'D1':1440,
                'W1':10080,
                'MN1':43200 }

def timestamp(date_):
    dt = date_-datetime(1970,1,1)
    return int(dt.total_seconds()*1000)

def cmdGetCandles(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol',	        type=str,  help="symbol")
    parser.add_argument('-freq','-f',	    type=str,  choices=PeriodCodes.keys(), help="Period code")
    parser.add_argument('-start','-s',      type=str,  help="start timestamp")
    parser.add_argument('-end','-e',        type=str,  help="end timestamp")
    parser.add_argument('-out','-o',        type=Path, help="output filename")
    parser.add_argument('-uid','-u',        type=int,  help="user id")
    parser.add_argument('-password','-p',   type=str,  help="password")
    Args = parser.parse_args(args)

    client = APIClient()
    loginResponse = client.execute(loginCommand(userId=Args.uid, password=Args.password))

    #logger.info(str(loginResponse)) 
    #print(str(loginResponse)) 

    # check if user logged in correctly
    if(loginResponse['status'] == False):
        print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        return

    start = timestamp(datetime.fromisoformat(Args.start))
    end = timestamp(datetime.fromisoformat(Args.end)) if Args.end is not None else None
    response = getCandles(client,Args.symbol, PeriodCodes[Args.freq], start, end)
    client.disconnect()
    of = open(Args.out,'w')
    json.dump(response,of)

def getCandles(client, symbol, period, start, end):
    arguments= { 'info': {
        'symbol':symbol,
        'period':period,
        'start':start }
    }
    if end is not None: arguments['info']['end'] = end
    return client.commandExecute('getChartLastRequest' if end is None else 'getChartRangeRequest', arguments=arguments)


def cmdGetAllSymbols(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-out','-o',        type=Path, help="output filename")
    parser.add_argument('-uid','-u',        type=int,  help="user id")
    parser.add_argument('-password','-p',   type=str,  help="password")
    Args = parser.parse_args(args)

    client = APIClient()
    loginResponse = client.execute(loginCommand(userId=Args.uid, password=Args.password))

    # check if user logged in correctly
    if(loginResponse['status'] == False):
        print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        return

    response = client.commandExecute('getAllSymbols')
    client.disconnect()
    of = open(Args.out,'w')
    json.dump(response,of)

if __name__ == '__main__':
    Cmds = {
        'getcan'    : cmdGetCandles,
        'getallsym' : cmdGetAllSymbols,
    }
    if len(sys.argv)<1:
        print('valid commands are',Cmds.keys())
        exit(0)
    cmd = sys.argv[1]
    if cmd not in Cmds:
        print('valid commands are',Cmds.keys())
        exit(0)
    Cmds[cmd](sys.argv[2:])
