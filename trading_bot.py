import sys,argparse
from datetime import datetime
from pathlib import Path
from xAPIConnector import APIClient,APIStreamClient,loginCommand
from utils import readConfig

def makeXtbClient(Args):
    if Args.test is None:
        client = APIClient()
        return client
    else:
        from test_api_client import TestClient
        testCfg = readConfig(Args.test)
        client = TestClient(testCfg)
    return client

def dummy(arg):
    return arg

def main(Args):
    cfg = readConfig(Args.config)
    client = makeXtbClient(Args)
    loginResponse = client.execute(loginCommand(userId=Args.uid, password=Args.password))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config',	        type=Path, help="config file path and name")
    parser.add_argument('-uid','-u',        type=int,  help="user id")
    parser.add_argument('-password','-p',   type=str,  help="password")
    parser.add_argument('-test',            type=Path, help="test config file path and name")
    Args = parser.parse_args(args)

    main(Args)
