import sys,argparse,json
from datetime import datetime
from pathlib import Path
from xAPIConnector import APIClient,APIStreamClient,DEFAULT_XAPI_PORT,loginCommand
from utils import readJson,readConfig
from threading import join

def serialize(object):
    return json.dumps(object.__dict__)


class Instument:
    @staticmethod
    def readState(filename):
        return Instrument()
    
    def __init__(self):
        pass

class TradingBot:
    def __init__(self, config):
        self.config = config

    # function for processing ticks from Streaming socket
    def procTick(self,msg): 
        print("TICK: ", msg)

    # function for processing trades from Streaming socket
    def procTrade(self,msg): 
        print("TRADE: ", msg)

    # function for processing trades from Streaming socket
    def procBalance(self,msg): 
        print("BALANCE: ", msg)

    # for processing trades from Streaming socket
    def procTradeStatus(self,msg): 
        print("TRADE STATUS: ", msg)

    # function for processing trades from Streaming socket
    def procProfit(self,msg):
        print("PROFIT: ", msg)

    # function for processing news from Streaming socket
    def procNews(self,msg):
        print("NEWS: ", msg)

def makeXtbClient(Args):
    if Args.test is None:
        port = DEFAULT_XAPI_PORT if Args.port is None else Args.port
        client = APIClient(port=port)
        return client
    else:
        from test_api_client import TestClient
        testCfg = readJson(Args.test)
        client = TestClient(testCfg)
    return client

def makeXtbStreamingClient(ssid, client,  tickFun, tradeFun, profitFun, tradeStatusFun):
    if Args.test is None:
        sclient = APIStreamClient(ssId=ssid, tickFun=tickFun, tradeFun=tradeFun, profitFun=profitFun, tradeStatusFun=tradeStatusFun)
    return None

def dummy(arg):
    return arg

def main(Args):
    cfg = readConfig(Args.config)
    Instruments = [Instrument.readState(cfg.instrument) ]
    client = makeXtbClient(Args)
    loginResponse = client.execute(loginCommand(userId=Args.uid, password=Args.password))

    bot = TradingBot(cfg)
    sclient = makeXtbStreamingClient(loginResponse['streamSessionId'],\
        tickFun=bot.procTick, tradeFun=bot.procTrade, profitFun=bot.procProfit, tradeStatusFun=bot.procTradeStatus)

    sclient.run()

    sclient.disconnect()
    client.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config',	    type=Path, help="config file path and name")
    parser.add_argument('-uid','-u',    type=int,  help="user id")
    parser.add_argument('-password',    type=str,  help="password")
    parser.add_argument('-port',        type=int,  help="port number")
    parser.add_argument('-test',        type=Path, help="test config file path and name")
    Args = parser.parse_args(sys.argv[1:])

    main(Args)
