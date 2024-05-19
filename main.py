from server import createServer
import argparse,sys
from utils import readJson
from pathlib import Path
import logging

def make_logger(loglevel_str, handler_str):
    loglevel = {'error' : logging.ERROR, 'info' : logging.INFO, 'debug' : logging.DEBUG}[loglevel_str]
    logger = logging.getLogger('stock-o-bot')
    logger.setLevel(loglevel)
    match handler_str:
        case "console":
            handler = logging.StreamHandler()
        case "file":
            handler = logging.FileHandler('stock-o-bot.log')
    handler.setLevel(loglevel)
    format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(format)
    logger.addHandler(handler)
    return logger

parser = argparse.ArgumentParser()
parser.add_argument('config',     type=Path,  help="configuration file")
parser.add_argument('--loglevel', type=str,   default='info',   choices=['error','info','debug'], help="log level")
parser.add_argument('--logtarget',type=str,   default='console',choices=['console','file'],       help="log target")
args = parser.parse_args()
logger = make_logger(args.loglevel, args.logtarget)
cfg = readJson(args.config,logger)
server = createServer(cfg,logger)
server.run()
