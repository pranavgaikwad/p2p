import random
import datetime
from threading import Lock
from p2p.server.server import Server
from p2p.client.client import ClientEntry as Client
from p2p.proto.proto import Message, ServerResponse as Response
from p2p.proto.proto import ResponseStatus as Status, MethodTypes
from p2p.proto.proto import Headers, ForbiddenError
from p2p.utils.app_constants import RS_HOST, RS_PORT

random.seed(0)


class RegistrationServer(Server):
    """ Registration Server """

    def __init__(self, host, port):
        super().__init__(host, port)
        self.mutex = Lock()

    def _reconcile(self):
        """ reconcile state of the server periodically """
        active = 0
        for _, client in self.clients.items():
            if client.flag is Client.FLAG_ACTIVE:
                client.ttl = client.ttl - Server.INTERVAL
                if client.ttl <= 0:
                    client.flag = Client.FLAG_INACTIVE
                    self.logger.info("Setting client {} inactive".format(client))
                else:
                    active += 1
        self.logger.info("Reconcile status: {} clients active".format(active))

    def _handle_register(self, conn, msg):
        """ handles register request """
        client = None
        self.mutex.acquire()
        try:
            host, p2port = msg.payload.split(Message.SR_FIELDS)
            client = Client(host=host, p2port=p2port, cookie=random.randint(1000, 9999))
            self.clients[Client.id(host, p2port)] = client
            self.logger.info("Registered new client {}".format(client))
            response = Response("Success", Status.Success.value)
        except (KeyError, ValueError):
            self.logger.error("Failed registering new client {}: Bad Message".format(client))
            response = Response("Error", Status.BadMessage.value)
        except Exception as e:
            self.logger.error("Failed registering new client {}: {}".format(client, e))
            response = Response("Internal Error", Status.InternalError.value)
        finally:
            self.mutex.release()
        response.headers[Headers.Cookie.name] = client.cookie
        return response

    def _handle_leave(self, conn, msg):
        """ handles leave request """
        client = None
        self.mutex.acquire()
        try:
            host, p2port = msg.payload.split(Message.SR_FIELDS)
            client = Client.id(host, p2port)
            if not self._validate_cookie(client, msg):
                raise ForbiddenError
            self.clients[client].ttl = 0
            self.clients[client].flag = Client.FLAG_INACTIVE
            self.logger.info("Removed client {}".format(client))
            response = Response("Success", Status.Success.value)
        except (KeyError, ValueError):
            self.logger.error("Failed removing client {}".format(self.clients[client]))
            response = Response("Error", Status.BadMessage.value)
        except ForbiddenError:
            self.logger.error("Forbidden client: {}".format(self.clients[client]))
            response = Response("Forbidden", Status.Forbidden.value)
        except Exception as e:
            self.logger.error("Failed removing client {}: {}".format(self.clients[client], e))
            response = Response("Internal Error", Status.InternalError.value)
        finally:
            self.mutex.release()
        return response

    def _handle_pquery(self, conn, msg):
        """ handles query request """
        client = None
        response = Response("Success", Status.Success.value)
        try:
            host, p2port = msg.payload.split(Message.SR_FIELDS)
            client = Client.id(host, p2port)
            if not self._validate_cookie(client, msg):
                raise ForbiddenError

            active_peers = set()
            for _id, peer in self.clients.items():
                if peer.flag is Client.FLAG_ACTIVE:
                    active_peers.add(_id)
            if client in active_peers:
                active_peers.remove(client)  # remove the requesting client from the set of active peers
            self.logger.info("{} active Peers found".format(len(active_peers)))
            response.payload = Message.SR_FIELDS.join(active_peers)
        except ForbiddenError:
            self.logger.error("Forbidden client: {}".format(self.clients[client]))
            response = Response("Forbidden", Status.Forbidden.value)
        except Exception as e:
            self.logger.error("Failed querying list of clients: %s" % str(e))
            response = Response(Status.InternalError.name, Status.InternalError.value)
        return response

    def _handle_keep_alive(self, conn, msg):
        """ handles keep-alive request """
        client = None
        self.mutex.acquire()
        try:
            host, p2port = msg.payload.split(Message.SR_FIELDS)
            client = Client.id(host, p2port)
            if not self._validate_cookie(client, msg):
                raise ForbiddenError
            self.clients[client].ttl = Client.TTL
            self.clients[client].flag = Client.FLAG_ACTIVE
            self.logger.info("Extended TTL for client {}".format(self.clients[client]))
            response = Response("Success: TTL Extended", Status.Success.value)
        except (KeyError, ValueError) as e:
            self.logger.error("Failed extending TTL for client {}: {}".format(self.clients[client], e))
            response = Response("Error", Status.BadMessage.value)
        except ForbiddenError:
            self.logger.error("Forbidden client: {}".format(self.clients[client]))
            response = Response("Forbidden: Invalid cookie", Status.Forbidden.value)
        except Exception as e:
            self.logger.error("Failed extending TTL for client {}: {}".format(self.clients[client], e))
            response = Response("Internal Error", Status.InternalError.value)
        finally:
            self.mutex.release()
        return response

    def _new_message_callback(self, conn, msg):
        """ processes a message """
        p2pmsg = Message()
        start_time = datetime.datetime.now()
        response = Response("Success", Status.Success.value)
        try:
            p2pmsg.from_bytes(msg)

            def handler(x):
                return {
                    MethodTypes.Register.name: self._handle_register,
                    MethodTypes.Leave.name: self._handle_leave,
                    MethodTypes.PQuery.name: self._handle_pquery,
                    MethodTypes.KeepAlive.name: self._handle_keep_alive
                }[x]

            func = handler(p2pmsg.method)
            response = func(conn, p2pmsg)
        except KeyError:
            self.logger.error("Method not allowed %s" % msg)
            response.payload = "Method not allowed"
            response.status = Status.MethodNotAllowed.value
        except Exception as e:
            self.logger.error("Error processing message %s" % str(e))
            response.payload = "Unknown error encountered"
            response.status = Status.Unknown.value
        finally:
            end_time = datetime.datetime.now()
            self.logger.info("Took %s ms to process request %s" %
                             ((end_time - start_time).microseconds / 1000, p2pmsg.method))
            # send some message back to the client no matter what
            self.messages[conn].put(response.to_bytes())

    def _new_connection_callback(self, conn):
        """ process new connection """
        pass

    def _validate_cookie(self, client, msg):
        try:
            cookie = msg.headers[Headers.Cookie.name]
        except KeyError:
            raise ForbiddenError
        return self.clients[client].cookie == int(cookie)


if __name__ == "__main__":
    rs = RegistrationServer(RS_HOST, RS_PORT)
    try:
        rs.start()
    except Exception as err:
        print("Stopping... %s" % str(err))
        rs.stop()
