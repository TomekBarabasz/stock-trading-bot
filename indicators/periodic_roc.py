from .indicator import Indicator

class PeriodicROC(Indicator):
    def __init__(self, name, config):
        super().__init__(name, config.symbols)
        self.started = False
        self.logger = config.logger
    def start(self):
        self.started = True
    def stop(self):
        self.started = False
    def new_data(self, symbol_data):
        self.logger.info( f'{self.name} new_data received {symbol_data=}' )
