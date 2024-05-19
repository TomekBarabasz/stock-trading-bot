from abc import ABC,abstractmethod

class Indicator(ABC):
    def __init__(self, name, symbols):
        self._name = name
        self.receiver = None
        self._symbols = symbols
    @property
    def name(self):
        return self._name
    @property
    def symbols(self):
        return self._symbols
    def set_receiver(self,receiver):
        self.receiver = receiver
    @abstractmethod
    def start(self):
        raise NotImplemented
    @abstractmethod
    def stop(self):
        raise NotImplemented
    @abstractmethod
    def new_data(self, symbol_data):
        raise NotImplemented
