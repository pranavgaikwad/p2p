import sys
import queue
import socket
import select
import datetime
from threading import Lock
from p2p.server.server import Server
from p2p.client.client import ClientEntry as Client
from p2p.proto.proto import Message, ServerResponse as Response
from p2p.proto.proto import ResponseStatus as Status, MethodTypes


class RegistrationServer(Server):
    """ Registration Server """
    PORT = 9999

    def __init__(self, host, port):
        super().__init__(host, port)
        self.mutex = Lock()

    def _reconcile(self):
        """ reconcile state of the server periodically """
        for client in self.clients:
            client.ttl = client.ttl - Server.INTERVAL
            if client.ttl <= 0:
                client.flag = Client.FLAG_INACTIVE
                self.logger.info("Setting client (%s, %s) inactive" % (client.host, client.port))
            else:
                client.flag = Client.FLAG_ACTIVE

    def _handle_register(self, conn, msg):
        """ handles register request """
        host = conn.getpeername()[0]
        port = conn.getpeername()[1]
        self.mutex.acquire()
        response = Response("Success", Status.Success.value)
        client = Client(host=host, port=port)
        try:
            p2port = msg.payload.split('\n')[1]
            client.p2port = p2port
            # TODO: improve logic
            if client in self.clients:
                idx = self.clients.index(client)
                self.clients[idx].ttl = Client.TTL
                self.clients[idx].flag = Client.FLAG_ACTIVE
            else:
                self.clients.append(client)
            self.logger.info("Registered new client (%s: %s)" % (client.host, p2port))
            response = Response("Success", Status.Success.value)
        except (KeyError, ValueError):
            self.logger.error("Failed registering new client (%s: %s) : Bad Message" % (client.host, client.port))
            response = Response("Error", Status.BadMessage.value)
        except Exception as e:
            self.logger.error("Failed registering new client (%s: %s) : %s" % (client.host, client.port, str(e)))
            response = Response("Internal Error", Status.InternalError.value)
        finally:
            self.mutex.release()
        return response

    def _handle_leave(self, conn, msg):
        """ handles leave request """
        self.mutex.acquire()
        c = Client(conn.getpeername()[0], conn.getpeername()[1])
        response = Response("Success", Status.Success.value)
        try:
            idx = self.clients.index(c)
            self.clients[idx].flag = Client.FLAG_INACTIVE
            self.logger.info("Removed client (%s: %s)" % (c.host, c.port))
            response = Response("Success", Status.Success.value)
        except (KeyError, ValueError):
            self.logger.error("Failed removing client (%s: %s)" % (c.host, c.port))
            response = Response("Error", Status.BadMessage.value)
        except:
            self.logger.error("Failed removing client (%s: %s) : Internal error" % (c.host, c.port))
            response = Response("Internal Error", Status.InternalError.value)
        finally:
            self.mutex.release()
        return response

    def _handle_pquery(self, conn, msg):
        """ handles query request """
        response = Response("Success", Status.Success.value)
        try:
            res = ""
            for c in self.clients:
                res = "%s%s," % (res, str(c))
            response.payload = res
        except Exception as e:
            self.logger.error("Failed querying list of clients : %s" % str(e))
        return response

    def _handle_keep_alive(self, conn, msg):
        """ handles keep-alive request """
        self.mutex.acquire()
        c = Client(conn.getpeername()[0], conn.getpeername()[1])
        response = Response("Success", Status.Success.value)
        try:
            idx = self.clients.index(c)
            self.clients[idx].ttl = Client.TTL
            self.clients[idx].flag = Client.FLAG_ACTIVE
            self.logger.info("Extended TTL for client (%s: %s)" % (c.host, c.port))
            response = Response("Success", Status.Success.value)
        except (KeyError, ValueError):
            self.logger.error("Failed extending TTL for client (%s: %s)" % (c.host, c.port))
            response = Response("Error", Status.BadMessage.value)
        except:
            self.logger.error("Failed extending TTL for client (%s: %s) : Internal Error" % (c.host, c.port))
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
            p2pmsg.from_str(msg.decode('utf-8'))

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
        finally:
            end_time = datetime.datetime.now()
            self.logger.info("Took %s ms to process request %s" %
                             ((end_time - start_time).microseconds / 1000, p2pmsg.method))
            # send some message back to the client no matter what
            self.messages[conn].put(response.to_bytes())

    def _new_connection_callback(self, conn):
        """ process new connection """
        pass


if __name__ == "__main__":
    rs = RegistrationServer("127.0.0.1", 9999)
    try:
        rs.start()
    except Exception as err:
        print("Stopping...%s" % str(err))
        rs.stop()
