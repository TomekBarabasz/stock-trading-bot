from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import sleep

class DataReceiver(ABC):
    @abstractmethod
    def receiveSymbol(self, symbol, symbol_data):
        pass

class DataSource(ABC):
    @abstractmethod
    def registerForSymbol(self, symbol : str, frequency : str, receiver : DataReceiver):
        pass
    @abstractmethod
    def start(self):
        pass
    @abstractmethod
    def stop(self):
        pass

class FileDataSource(DataSource):
    def __init__(self,delay):
        self.receivers = []
        self.delay = delay
    def registerForSymbol(self, symbol, frequency, receiver):
        self.receivers.append( (receiver, symbol, datetime.now()) )    
    @abstractmethod
    def get_next_tick(self):
        pass

    def start(self):
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

    def stop(self):
        pass

class JsonDataSource(FileDataSource):
    def __init__(self, filename, delay, start_timestamp):
        super().__init__(delay)
        from .utils import loadNamespaceFromJson
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
    
def createDataSource(name, **kwargs):
    if name == 'file':
        filename = Path(kwargs['filename'])
        if filename.suffix == '.json':
            return JsonDataSource(**kwargs)
        elif filename.suffix == '.csv':
            return CSVDataSource(**kwargs)
    elif name == 'xtb':
        return None
