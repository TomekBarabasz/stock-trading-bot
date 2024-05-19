from data_source import createDataSource
from pushover import createPushoverSink
from indicators import createIndicatorContainer

def createNotificationSink(config):
    match config['type']:
        case 'pushover':
            return createPushoverSink(config['credentials_filename'])
        case _:
            raise NotImplemented

class Server:
    def __init__(self, data_source, notification_sink, indicators, logger):
        self.data_source = data_source
        self.notification_sink = notification_sink
        self.indicators = indicators
        self.logger = logger
    
    def run(self):
        self.logger.info("sever started")
        self.indicators.run()
        self.data_source.run()

def createServer(config,logger):
    data_source_config = config['data_source']
    data_source = createDataSource(data_source_config['type'], **data_source_config['params'], logger=logger)
    notification_sink = createNotificationSink(config['notification_sink'])
    periodic_updates = createIndicatorContainer(config['indicators'], data_source, notification_sink, logger)
    return Server(data_source,notification_sink,periodic_updates,logger)
