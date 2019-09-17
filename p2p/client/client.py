from p2p.utils.logger import logger


class P2PClient(object):
    """ Peer to Peer Client """

    def __init__(self, host, port):
        pass

    def connect(self, host, port):
        """ connects to a server or a peer """
        pass

    def send(self, msg):
        """ sends a message """
        pass

    def receive(self):
        """ receives a message """
        pass


class ClientEntry(object):
    """ object to represent a P2PClient in RegistrationServer's list of clients """
    FLAG_ACTIVE = 0
    FLAG_INACTIVE = 1

    TTL = 7200

    def __init__(self, host, port, p2port=0):
        self.host = host
        self.port = port
        self.p2port = p2port  # port on which P2P server is running
        self.cookie = "%s: %s" % (host, port)
        self.flag = ClientEntry.FLAG_ACTIVE
        self.ttl = ClientEntry.TTL
        self.activity = 0
        self.last_active = 0

    def __str__(self):
        return "%s:%s" % (self.host, self.p2port)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, c):
        return self.host == c.host and self.port == c.port
