
# defines protocols required by P2P-DI System

class Message(object):
    """ a generic message used by servers and clients both """
    def __init__(self, payload, method, version, headers):
        self.payload = payload
        self.method = method
        self.version = version
        self.headers = headers

    def encode(self):
        """ encodes the message into bytes """
        pass

    def decode(self):
        """ decodes the message from bytes """
        pass 
