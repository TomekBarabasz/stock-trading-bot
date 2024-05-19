from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from time import sleep

class DataReceiver(ABC):
    @abstractmethod
    def receiveSymbol(self, symbol, symbol_data):
        pass

class DataSource(ABC):
    @abstractmethod
    def registerForSymbol(self, symbol : str, receiver : DataReceiver):
        pass
    def unregisterForSymbol(self, symbol : str, receiver : DataReceiver):
        pass
    @abstractmethod
    def run(self):
        pass

class FileDataSource(DataSource):
    def __init__(self,delay,logger):
        self.receivers = []
        self.delay = delay
        self.logger = logger
    def registerForSymbol(self, symbol, receiver):
        self.receivers.append( (receiver, symbol, datetime.now()) )
        self.logger.info(f"register for symbol {symbol}")
    @abstractmethod
    def get_next_tick(self):
        pass

    def run(self):
        cnt = 0
        while True:
            try:
                tick = self.get_next_tick()
                for receiver,symbol, tm in self.receivers:
                    receiver.receiveSymbol(symbol, tick)
                if self.delay is not None:
                    sleep(self.delay)
            except StopIteration:
                break
            cnt = cnt + 1
            if cnt > 10:
                break

class JsonDataSource(FileDataSource):
    def __init__(self, filename, **kwargs):
        delay = kwargs['delay']
        start_timestamp = kwargs.get('start_timestamp',None)
        logger = kwargs.get('logger')
        super().__init__(delay,logger)
        from utils import loadNamespaceFromJson
        self.source = loadNamespaceFromJson(open(filename)).rateInfos
        self.iter = iter(self.source)
        if start_timestamp is not None:
            while True:
                t = next(self.iter)
                if t.ctm >= start_timestamp:
                    break
            self.first = t
        else:
            self.first = None
        
    def get_next_tick(self):
        return self.first if self.first is not None else next(self.iter)    
  
class CSVDataSource(FileDataSource):
    def __init__(self, filename, delay, start_timestamp):
       pass
    
def createDataSource(type, **kwargs):
    match type:
        case 'file':
            filename = Path(kwargs['filename'])
            match filename.suffix:
                case '.json':
                    return JsonDataSource(**kwargs)
                case '.csv':
                    return CSVDataSource(**kwargs)
        case 'xtb-client':
            return None
