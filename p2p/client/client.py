from socket import socket, AF_INET, SOCK_STREAM
import random
from glob import glob
from datetime import datetime
from p2p.utils.logger import logger
from p2p.server.server import Server
from p2p.proto.proto import ResponseStatus as Status
from p2p.proto.proto import ServerResponse as Response
from p2p.proto.proto import Message, MethodTypes, Headers, ForbiddenError
from p2p.utils.app_constants import RS_PORT, RFC_PATH, GOAL_RFC_STATE
from threading import Lock


class Peer:
    def __init__(self):
        # self.server = P2PServer()
        # self.client = P2PClient()
        pass


class P2PServer(Server):

    def __init__(self, host, port, rfc_index, goal_rfc_state=GOAL_RFC_STATE):
        super().__init__(host, port)
        self.mutex = Lock()
        self.cookie = -1
        self.rfc_index = rfc_index  # set[str] containing rfc indices or initial state
        self.goal_state = goal_rfc_state
        self.rfc_data = {}

    def _load_rfcs(self):
        for file in glob(RFC_PATH + "/*.txt"):
            idx = file.split('/')[-1][3:7]
            if idx in self.rfc_index:
                self.rfc_data[idx] = open(file).read()
        self.logger("Loaded {} RFCs".format(len(self.rfc_data)))

    def _on_start(self):
        """ load RFCs in memory and register this peer """
        self._load_rfcs()

        with socket(AF_INET, SOCK_STREAM) as conn:
            conn.connect(('127.0.0.1', RS_PORT))

            msg = Message()
            msg.method = MethodTypes.Register.name
            msg.headers = {}
            msg.version = Message.VERSION
            msg.payload = "{}\n{}".format(self.host, self.port)

            try:
                conn.send(msg.to_bytes())
                response = Response().from_str(conn.recv(1024).decode("utf-8"))
                self.cookie = response.headers[Headers.Cookie.name]
                self.logger.info("Peer registered")
            except Exception as e:
                self.logger.error("Error while registering Peer: {}".format(e))

    def _reconcile(self):
        """ reconcile state of the server periodically """
        with socket(AF_INET, SOCK_STREAM) as conn:
            conn.connect(('127.0.0.1', RS_PORT))

            msg = Message()
            msg.method = MethodTypes.KeepAlive.name
            msg.headers = {Headers.Cookie.name: self.cookie}
            msg.version = Message.VERSION
            msg.payload = "{}\n{}".format(self.host, self.port)

            try:
                conn.send(msg.to_bytes())
                response = Response().from_str(conn.recv(1024).decode("utf-8"))
                if int(response.status) == 403:
                    raise ForbiddenError(response.payload)
                self.logger.info("TTL extended")
            except ForbiddenError as e:
                self.logger.error(e)
            except Exception as e:
                self.logger.error("Error while extending TTL: {}".format(e))

    def _handle_rfcquery(self, conn, msg):
        pass

    def _handle_getrfc(self, conn, msg):
        pass

    def _new_message_callback(self, conn, msg):
        """ processes a message """
        p2pmsg = Message()
        start_time = datetime.now()
        response = Response(response=Status.Unknown.name, status=Status.Unknown.value)
        try:
            p2pmsg.from_str(msg.decode('utf-8'))

            def handle(method):
                return {
                    MethodTypes.RFCQuery.name: self._handle_rfcquery,
                    MethodTypes.GetRFC.name: self._handle_getrfc,
                }[method]

            response = handle(p2pmsg.method)(conn, p2pmsg)
        except KeyError:
            self.logger.error("Method not allowed {}".format(p2pmsg.method))
            response.payload = "Method not allowed"
            response.status = Status.MethodNotAllowed.value
        except Exception as e:
            self.logger.error("Error processing message {}".format(e))
            response.payload = "Unknown error encountered"
            response.status = Status.Unknown.value
        finally:
            self.logger.info(
                "Took {} ms to process request {}".format((datetime.now() - start_time).microseconds / 1000,
                                                          p2pmsg.method))
            # send some message back to the client no matter what
            self.messages[conn].put(response.to_bytes())


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
    peer = P2PServer("127.0.0.1", random.randint(65400, 65500))
    try:
        peer.start()
    except Exception as err:
        print("Stopping...{}".format(err))
        peer.stop()
