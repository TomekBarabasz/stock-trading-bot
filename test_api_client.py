
class TestClient:
    def __init__(self, testCfg):
        pass
    
    def __init__(self, address=DEFAULT_XAPI_ADDRESS, port=DEFAULT_XAPI_PORT, encrypt=True, logger=DummyLogger()):
        super(APIClient, self).__init__(address, port, encrypt,logger)
        if(not self.connect()):
            raise Exception("Cannot connect to " + address + ":" + str(port) + " after " + str(API_MAX_CONN_TRIES) + " retries")

    def execute(self, dictionary):
        raise NotImplemented()
        return None

    def disconnect(self):
        pass
        
    def commandExecute(self,commandName, arguments=None):
        raise NotImplemented()
        return None
