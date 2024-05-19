from abc import ABC,abstractmethod

class NotificationSink(ABC):
    @abstractmethod
    def notify(self, source, message, params):
        raise NotImplemented
    def __call__(self, source, message, params):
        self.notify(source, message,params)
