from abc import ABC
from utils import loadNamespaceFromJson

class DataReceiver(ABC):
    @abstractmethod
    def receiveSymbol(symbol, symbol_data, timestamp):
        pass

class DataSource(ABC):
    @abstractmethod
    def registerForSymbol(self, symbol : str, frequency : str, receiver : DataReceiver):
        pass

class JsonDataSource(DataSource):
    import json
    def __init__(self, filename, delay):
        self.source = loadNamespaceFromJson(filename)

    def registerForSymbol(self, symbol, frequency, receiver):
        pass

class DataSoruceFactory:
    @staticmethod
    def createDataSource(name, **kwargs):
        if name == 'json':
            return JsonDataSource
