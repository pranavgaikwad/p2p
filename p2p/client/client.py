import os
import time
import random
from ast import literal_eval
from collections import defaultdict
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM, error
from threading import Lock
from threading import Thread

from p2p.proto.proto import Message, MethodTypes, Headers
from p2p.proto.proto import ResponseStatus as Status
from p2p.proto.proto import ServerResponse as Response
from p2p.server.server import Server
from p2p.utils.app_constants import RS, RFC_PATH, GOAL_RFC_STATE, RFC_SET1
from p2p.utils.app_utils import logger, send, recv, retry, flatten, ForbiddenError, CriticalError, NotFoundError

SEP = Message.SR_FIELDS


class Peer:

    def __init__(self, host, port, initial_rfc_state, goal_rfc_state=GOAL_RFC_STATE):
        self.logger = logger()
        self.mutex = Lock()
        self.server = P2PServer(host, port, self)
        self._server_thread = None
        self.rfc_index = self._prepare_rfc_index(initial_rfc_state)
        self.rfc_data = {}
        self.goal_state = goal_rfc_state
        self.registered = False

    def __str__(self):
        return "{}:{}".format(self.server.host, self.server.port)

    def _prepare_rfc_index(self, initial_state):
        rfc_index = defaultdict(set)
        rfc_index[str(self)].update(initial_state.copy())
        return rfc_index

    def load_rfcs(self):
        """ loads RFCs into memory """
        for file in os.listdir(RFC_PATH):
            idx = file.split('/')[-1][3:7]
            if idx in flatten(self.rfc_index.values()):
                with open("{}/{}".format(RFC_PATH, file)) as f:
                    self.rfc_data[idx] = f.read()
        self.logger.info("Loaded {} RFCs".format(len(self.rfc_data)))

    def main(self):
        """ performs the main project task of downloading the RFCs from other peers """
        # wait for this peer to be registered with RS
        while not self.registered:
            continue

        start_time = time.perf_counter()

        # loop to fetch and merge RFC Index from other peers
        done = False
        while not done:
            try:
                remaining = self.goal_state - self._flatten(self.rfc_index)
                if not remaining:
                    self.logger.info("[CLIENT] RFC Index complete")
                    break

                active_peers = self.get_active_peers()

                for peer in active_peers:
                    # all missing RFCs
                    remaining = self.goal_state - self._flatten(self.rfc_index)

                    if remaining:
                        # missing RFCs available from this peer
                        peer_rfc_index = self.RFCQuery(peer)
                        interested = remaining & self._flatten(peer_rfc_index)

                        if interested:
                            self._update_rfc_index(peer_rfc_index)
                        else:
                            self.logger.info("[CLIENT] No RFCs of interest found from Peer {}".format(peer))
                    else:
                        done = True
                        self.logger.info("[CLIENT] RFC Index complete")
                        break
            except NotFoundError as e:
                self.logger.error("{}, stopping client task".format(e))
                break
            except CriticalError as e:
                self.logger.error("[CLIENT] Critical error encountered, stopping client task: {}".format(e))
                break

        times = defaultdict(list)

        # loop to fetch actual RFC data
        for peer, index in self.rfc_index.items():
            if peer != str(self):
                # fetch interested RFCs one at a time
                for rfc in index:
                    _start_time = time.perf_counter()
                    new_rfc = self.fetch_interested_rfc(peer, rfc)
                    times[peer].append((rfc, time.perf_counter() - _start_time))
                    self._update_rfc_data(new_rfc)

        cumulative_time = time.perf_counter() - start_time

        self.logger.info("[CLIENT] Task completed at peer: {}, final RFC count: {}".format(self, len(self.rfc_data)))

        return str(self), cumulative_time, dict(times)

    @retry(NotFoundError, tries=3, delay=2)
    def get_active_peers(self):
        """ PQuery wrapper with retry mechanism """
        active_peers = self.PQuery()
        if not active_peers:
            raise NotFoundError("[CLIENT] No active peers found")
        return active_peers

    def fetch_interested_rfc(self, peer, rfc):
        """ GetRFC wrapper """
        try:
            new_rfc = literal_eval(self.GetRFC(peer, rfc))  # dict_str -> Dict{rfc_number: rfc_data}
        except:
            raise Exception("Literal eval parsing error at peer: {}".format(self))
        return new_rfc

    def _update_rfc_index(self, interested):
        """ update this peers RFC Index """
        with self.mutex:
            self.rfc_index.update(interested)

    def _update_rfc_data(self, new_rfc):
        """ update this peers RFC Data """
        with self.mutex:
            self.rfc_data.update(new_rfc)

    @staticmethod
    def _flatten(data):
        """ flattens nested data structure into a set"""
        return set(flatten(data.values()))

    def start(self, tname=None):
        """ starts the P2PServer on this peer """
        self._server_thread = Thread(name=tname, target=self.server.start)
        self._server_thread.start()

    def stop(self):
        """ stops the P2PServer running on this peer """
        self.Leave()
        self._server_thread.join()

    def PQuery(self):
        """ sends PQuery message RS to get the list of active peers """
        msg = Message()
        msg.method = MethodTypes.PQuery.name
        msg.version = Message.VERSION
        msg.payload = "{}{}{}".format(self.server.host, SEP, self.server.port)
        msg.headers[Headers.Cookie.name] = self.server.cookie

        peers = []
        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                conn.connect(RS)
                send(conn, msg)
                response = Response().from_bytes(recv(conn))
                if response.payload:
                    peers = response.payload.split(SEP)
                self.logger.info("[CLIENT] {} active peer(s) found".format(len(peers)))
            except error as se:
                self.logger.error("[CLIENT] Socket error: {}".format(se))
            except Exception as e:
                self.logger.error("[CLIENT] Error while retrieving active peers: {}".format(e))
                raise CriticalError
        return peers

    def RFCQuery(self, peer):
        """ sends RFCQuery message to an active peer to get its RFC Index """
        msg = Message()
        msg.method = MethodTypes.RFCQuery.name
        msg.version = Message.VERSION

        index = dict()
        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                host, port = peer.split(':')
                conn.connect((host, int(port)))
                send(conn, msg)
                response = Response().from_bytes(recv(conn))
                if response.payload:
                    index = defaultdict(set, literal_eval(response.payload))
                self.logger.info("[CLIENT] RFC Index retrieved from peer {}".format(peer))
            except error as se:
                self.logger.error("[CLIENT] Socket error: {}".format(se))
            except Exception as e:
                self.logger.error("[CLIENT] Error while retrieving RFC Index from peer {}: {}".format(peer, e))
        return index

    def GetRFC(self, peer, rfc):
        """ sends GetRFC message to an active peer requesting a specific RFC of interest """
        msg = Message()
        msg.method = MethodTypes.GetRFC.name
        msg.version = Message.VERSION
        msg.payload = rfc

        new_rfc = {}
        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                host, port = peer.split(':')
                conn.connect((host, int(port)))
                send(conn, msg)
                response = Response().from_bytes(recv(conn))
                if response.payload:
                    new_rfc = response.payload
                self.logger.info("[CLIENT] {} new RFC fetched from peer {}".format(1, peer))
            except error as se:
                self.logger.error("[CLIENT] Socket error: {}".format(se))
            except Exception as e:
                self.logger.error("[CLIENT] Error while fetching new RFCs from peer {}: {}".format(peer, e))
        return new_rfc

    def Leave(self):
        """ sends Leave message to RS to rescind the registration of this peers P2PServer """
        self.server.stop()

        msg = Message()
        msg.method = MethodTypes.Leave.name
        msg.version = Message.VERSION
        msg.payload = "{}{}{}".format(self.server.host, SEP, self.server.port)
        msg.headers[Headers.Cookie.name] = self.server.cookie

        status = None
        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                conn.connect(RS)
                send(conn, msg)
                response = Response().from_bytes(recv(conn))
                status = response.status
                if int(status) == Status.Success.value:
                    self.logger.info("[Client] Successfully left P2P-DI system")
                else:
                    self.logger.error("[CLIENT] Failed to leave P2P-DI system")
                    self.start()
            except error as se:
                self.logger.error("[CLIENT] Socket error: {}".format(se))
            except Exception as e:
                self.logger.error("[CLIENT] Error while attempting to leave P2P-DI system: {}".format(e))
        return status


class P2PServer(Server):

    def __init__(self, host, port, _peer):
        super().__init__(host, port)
        self.cookie = -1
        self.platform_peer = _peer  # platform peer is the host peer on which this P2PServer is running

    def _on_start(self):
        """ load RFCs in memory and register this peer """
        self.platform_peer.load_rfcs()
        self.Register()

    def _reconcile(self):
        """ reconcile state of the server periodically """
        self.KeepAlive()

    def _handle_rfcquery(self, _conn, _msg):
        """ return this peers RFC Index """
        try:
            with self.platform_peer.mutex:
                payload = str(dict(self.platform_peer.rfc_index))
                response = Response(payload, Status.Success.value)
        except Exception as e:
            self.logger.error("Failed to return RFC Index: {}".format(e))
            response = Response(Status.InternalError.name, Status.InternalError.value)
        return response

    def _handle_getrfc(self, _conn, _msg):
        """ return data for requested RFCs as List[Dict] where each Dict is {RFC Index: RFC Data}"""
        try:
            rfc = _msg.payload
            with self.platform_peer.mutex:
                payload = str({rfc: self.platform_peer.rfc_data[rfc]})
                response = Response(payload, Status.Success.value)
        except Exception as e:
            self.logger.error("Failed to return RFC data: {}".format(e))
            response = Response(Status.InternalError.name, Status.InternalError.value)
        return response

    def _new_message_callback(self, conn, msg):
        """ processes a message """
        start_time = datetime.now()
        response = Response()
        p2pmsg = Message()
        try:
            p2pmsg.from_bytes(msg)

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

    def Register(self):
        """ sends Register message to RS """
        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "{}{}{}".format(self.host, SEP, self.port)

        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                conn.connect(RS)
                send(conn, msg)
                response = Response().from_bytes(recv(conn))
                cookie = response.headers.get(Headers.Cookie.name, None)
                if not cookie:
                    raise Exception("Cookie not received from RS")
                self.cookie = cookie
                self.platform_peer.registered = True
                self.logger.info("Peer registered")
            except error as se:
                self.logger.error("Socket error: {}".format(se))
            except Exception as e:
                self.logger.error("Error while registering Peer: {}".format(e))

    def KeepAlive(self):
        """ sends KeepAlive message to RS """
        msg = Message()
        msg.method = MethodTypes.KeepAlive.name
        msg.headers = {Headers.Cookie.name: self.cookie}
        msg.version = Message.VERSION
        msg.payload = "{}{}{}".format(self.host, SEP, self.port)

        with socket(AF_INET, SOCK_STREAM) as conn:
            try:
                conn.connect(RS)
                send(conn, msg)
                response = Response().from_bytes(recv(conn))
                if int(response.status) == 403:
                    raise ForbiddenError(response.payload)
                self.logger.info("TTL extended")
            except ForbiddenError as e:
                self.logger.error(e)
            except error as se:
                self.logger.error("[CLIENT] Socket error: {}".format(se))
            except Exception as e:
                self.logger.error("Error while extending TTL: {}".format(e))


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
        return "{}:{}".format(self.host, self.p2port)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, c):
        return self.host == c.host and self.p2port == c.p2port

    @staticmethod
    def id(host, p2port):
        return "{}:{}".format(host, p2port)


if __name__ == '__main__':
    p = Peer("127.0.0.1", random.randint(65400, 65500), RFC_SET1)
    server_thread = None
    try:
        p.start()
        # t = Thread(target=p.main)
        # t.start()
        # t.join()
    except Exception as err:
        print("Stopping... {}".format(err))
        p.stop()
