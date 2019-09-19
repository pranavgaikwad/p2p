import sys
from p2p.utils.logger import logger
from p2p.server.server import Server
from p2p.server.rs import RegistrationServer
from p2p.proto.proto import Message, MethodTypes, Headers, ServerResponse, ResponseStatus
from threading import Lock


class Peer:
    def __init__(self):
        pass


class P2PServer(Server):

    def __init__(self, host, port):
        super().__init__(host, port)
        self.mutex = Lock()
        self.cookie = None

    def _on_start(self):
        """ register this peer """
        self.conn.connect(('127.0.0.1', RegistrationServer.PORT))
        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "{}\n{}".format(self.host, self.port)
        self.conn.send(msg.to_bytes())
        response = ServerResponse().from_str(self.conn.recv(1024).decode("utf-8"))
        print(response)

    def _reconcile(self):
        """ reconcile state of the server periodically """
        pass

    def _new_message_callback(self, conn, msg):
        """ processes a message """
        pass


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

    def __init__(self, host, port, p2port=0, cookie=None):
        self.host = host
        self.port = port
        self.p2port = p2port  # port on which P2P server is running
        self.cookie = cookie
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

    @staticmethod
    def id(host, p2port):
        return "{}:{}".format(host, p2port)


if __name__ == '__main__':
    peer = P2PServer("127.0.0.1", 9900)
    try:
        peer.start()
    except Exception as err:
        print("Stopping...{}".format(err))
        peer.stop()
