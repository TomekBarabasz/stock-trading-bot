from .periodic_roc import PeriodicROC
from .indicatorsContainer import IndicatorContainer
from types import SimpleNamespace

def createIndicator(name, config, logger):
    config = SimpleNamespace(**config)
    config.logger = logger
    match config.type:
        case 'periodic_roc':
            return PeriodicROC(name, config)

def createIndicatorContainer(configuration, data_source, notification_sink, logger):
    ic = IndicatorContainer(data_source, notification_sink)
    for name, params in configuration.items():
        indicator = createIndicator(name, params, logger)
        logger.info(f'creating indicator {name} symbols={indicator.symbols}')
        ic.register(indicator)
    return ic
