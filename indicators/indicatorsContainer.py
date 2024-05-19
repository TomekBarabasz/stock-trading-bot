from data_source import DataSource, DataReceiver
from notify import NotificationSink
from collections import defaultdict

class IndicatorContainer(DataReceiver):
    def __init__(self, data_source : DataSource, notification_receiver : NotificationSink):
        self.notification_receiver = notification_receiver
        self.data_source = data_source
        self.symbols = defaultdict(list)
    def register(self, indicator):
        indicator.set_receiver(self.notification_receiver)
        for sym in indicator.symbols:
            self.symbols[sym].append(indicator)
        indicator.start()
    def deregister(self, indicator):
        for sym,indicator_list in self.symbols:
            idx = indicator_list.find(indicator)
            if idx >=0:
                del indicator_list[idx]
            if len(indicator_list) == 0:
                self.data_source.unregisterForSymbol(sym)
    def stop(self, name):
        for _,indicator_list in self.symbols:
            for ind in indicator_list:
                if ind.name == name:
                    ind.stop()
    def start(self, name):
        for _,indicator_list in self.symbols:
            for ind in indicator_list:
                if ind.name == name:
                    ind.start()
    def receiveSymbol(self, symbol, symbol_data):
        for ind in self.symbols[symbol]:
            ind.new_data(symbol_data)
    def run(self):
        for symbol in self.symbols.keys():          
            self.data_source.registerForSymbol(symbol,self)


