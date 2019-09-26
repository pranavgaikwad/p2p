from socket import socket, AF_INET, SOCK_STREAM
import random
from ast import literal_eval
from threading import Thread
from glob import glob
from datetime import datetime
from p2p.utils.logger import logger
from p2p.server.server import Server
from p2p.proto.proto import ResponseStatus as Status
from p2p.proto.proto import ServerResponse as Response
from p2p.proto.proto import Message, MethodTypes, Headers, ForbiddenError, CriticalError
from p2p.utils.app_constants import RS, RFC_PATH, GOAL_RFC_STATE
from threading import Lock

SEP = Message.SR_FIELDS


class Peer:

    def __init__(self, host, port, rfc_index, goal_rfc_state=GOAL_RFC_STATE):
        self.logger = logger()
        self.server = P2PServer(host, port, self)
        self.rfc_index = rfc_index  # set[str] containing rfc indices or initial state
        self.goal_state = goal_rfc_state
        self.rfc_data = {}
        self.registered = False
        self.mutex = Lock()

    def load_rfcs(self):
        for file in glob(RFC_PATH + "/*.txt"):
            idx = file.split('/')[-1][3:7]
            if idx in self.rfc_index:
                self.rfc_data[idx] = open(file).read()
        self.logger.info("Loaded {} RFCs".format(len(self.rfc_data)))

    def main(self, client_task=False):
        # start P2PServer
        Thread(target=self.server.start).start()

        # perform P2PClient tasks
        if client_task:
            # wait for this peer to be registered
            while not self.registered:
                continue

            # perform client task
            done = False
            while not done:
                try:
                    for peer in self._get_active_peers():
                        remaining = self.goal_state - self.rfc_index
                        if remaining:
                            interested = remaining & self._get_peer_index(peer)
                            self._fetch_interested_rfcs(peer, interested)
                        else:
                            done = True
                            self.logger.info("[CLIENT] Client task completed")
                            break
                except CriticalError:
                    self.logger.error("[CLIENT] Critical error encountered, stopping client task")
                    break

    def _fetch_interested_rfcs(self, peer, interested):
        if interested:
            new_rfcs = map(literal_eval, self._get_rfcs(peer, interested))  # List[dict_str] -> List[Dict]
            with self.mutex:
                for rfc in new_rfcs:
                    self.rfc_index.update(rfc.keys())
                    self.rfc_data.update(rfc)
        else:
            self.logger.info("[CLIENT] No RFCs of interest found from Peer {}".format(peer))

    def _get_active_peers(self):
        msg = Message()
        msg.method = MethodTypes.PQuery.name
        msg.version = Message.VERSION
        msg.payload = "{}{}{}".format(self.server.host, SEP, self.server.port)
        msg.headers[Headers.Cookie.name] = self.server.cookie

        peers = []
        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                conn.connect(RS)
                conn.send(msg.to_bytes())
                response = Response().from_str(conn.recv(1024).decode("utf-8"))
                peers = response.payload.split(SEP)
                self.logger.info("[CLIENT] {} active Peer(s) found".format(len(peers)))
            except Exception as e:
                self.logger.error("[CLIENT] Error while retrieving active Peers: {}".format(e))
                raise CriticalError
        return peers

    def _get_peer_index(self, peer):
        msg = Message()
        msg.method = MethodTypes.RFCQuery.name
        msg.version = Message.VERSION

        index = set()
        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                host, port = peer.split(':')
                conn.connect((host, int(port)))
                conn.send(msg.to_bytes())
                response = Response().from_str(conn.recv(1024).decode("utf-8"))
                index = set(response.payload.split(SEP))
                self.logger.info("[CLIENT] RFC Index retrieved from Peer {}".format(peer))
            except Exception as e:
                self.logger.error("[CLIENT] Error while retrieving RFC Index from Peer {}: {}".format(peer, e))
        return index

    def _get_rfcs(self, peer, rfcs):
        msg = Message()
        msg.method = MethodTypes.GetRFC.name
        msg.version = Message.VERSION
        msg.payload = SEP.join(rfcs)

        new_rfcs = []
        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                host, port = peer.split(':')
                conn.connect((host, int(port)))
                conn.send(msg.to_bytes())
                response = Response().from_str(conn.recv(1024).decode("utf-8"))
                new_rfcs = response.payload.split(SEP)
                self.logger.info("[CLIENT] {} new RFCs fetched from Peer {}".format(len(new_rfcs), peer))
            except Exception as e:
                self.logger.error("[CLIENT] Error while fetching new RFCs from Peer {}: {}".format(peer, e))
        return new_rfcs

    def stop(self):
        self.server.stop()


class P2PServer(Server):

    def __init__(self, host, port, _peer):
        super().__init__(host, port)
        self.cookie = -1
        self.platform_peer = _peer  # platform peer is the host peer on which this P2PServer is running

    def _on_start(self):
        """ load RFCs in memory and register this peer """
        self.platform_peer.load_rfcs()

        with socket(AF_INET, SOCK_STREAM) as conn:
            conn.connect(RS)

            msg = Message()
            msg.method = MethodTypes.Register.name
            msg.headers = {}
            msg.version = Message.VERSION
            msg.payload = "{}{}{}".format(self.host, SEP, self.port)

            try:
                conn.send(msg.to_bytes())
                response = Response().from_str(conn.recv(1024).decode("utf-8"))
                self.cookie = response.headers[Headers.Cookie.name]
                self.platform_peer.registered = True
                self.logger.info("Peer registered")
            except Exception as e:
                self.logger.error("Error while registering Peer: {}".format(e))

    def _reconcile(self):
        """ reconcile state of the server periodically """
        with socket(AF_INET, SOCK_STREAM) as conn:
            conn.connect(RS)

            msg = Message()
            msg.method = MethodTypes.KeepAlive.name
            msg.headers = {Headers.Cookie.name: self.cookie}
            msg.version = Message.VERSION
            msg.payload = "{}{}{}".format(self.host, SEP, self.port)

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

    def _handle_rfcquery(self, _conn, _msg):
        """ return this peers RFC Index """
        try:
            payload = SEP.join(self.platform_peer.rfc_index)
            response = Response(payload, Status.Success.value)
        except Exception as e:
            self.logger.error("Failed to return RFC Index: {}".format(e))
            response = Response(Status.InternalError.name, Status.InternalError.value)
        return response

    def _handle_getrfc(self, _conn, _msg):
        """ return data for requested RFCs as List[Dict] where each Dict is {RFC Index: RFC Data}"""
        try:
            rfcs = _msg.payload.split(SEP)
            payload = SEP.join([str({rfc: self.platform_peer.rfc_data[rfc]}) for rfc in rfcs])
            response = Response(payload, Status.Success.value)
        except Exception as e:
            self.logger.error("Failed to return RFC Index: {}".format(e))
            response = Response(Status.InternalError.name, Status.InternalError.value)
        return response

    def _new_message_callback(self, conn, msg):
        """ processes a message """
        start_time = datetime.now()
        response = Response()
        p2pmsg = Message()
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


class ClientEntry(object):
    """ object to represent a P2PClient in RegistrationServer's list of clients """
    FLAG_ACTIVE = 1
    FLAG_INACTIVE = 0

    TTL = 7200

    def __init__(self, host, p2port, cookie=None):
        self.host = host  # host on which P2P server is running
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
        return self.host == c.host and self.p2port == c.p2port

    @staticmethod
    def id(host, p2port):
        return "{}:{}".format(host, p2port)


if __name__ == '__main__':
    s1 = {'1001', '1002', '1003', '1004', '1005'}
    s2 = {'1006', '1007', '1008', '1009', '1010'}
    p = Peer("127.0.0.1", random.randint(65400, 65500), s2)
    try:
        p.main()
    except Exception as err:
        print("Stopping... {}".format(err))
        p.stop()
