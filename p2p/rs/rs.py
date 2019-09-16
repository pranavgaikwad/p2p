import sys
import queue
import socket
import select
from threading import Lock
from p2p.utils.server import Server
from p2p.protocol.proto import Message, MethodTypes

class Client(object):
    FLAG_ACTIVE = 0
    FLAG_INACTIVE = 1

    """ object to represent a P2PClient in RegistrationServer's list of clients """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.cookie = "%s: %s"%(host, port)
        self.flag = Client.FLAG_ACTIVE
        self.ttl = 3600
        self.activity = 0 
        self.last_active = 0

    def __str__(self):
        return "{ Host : %s Port : %s Cookie : %s Flag : %s TTL : %s Activity : %s Active %s }"%(self.host, self.port, self.cookie, self.flag, self.ttl, self.activity, self.last_active)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, c):
        return self.host == c.host and self.port == c.port

class RegistrationServer(Server):
    """ Registration Server """
    PORT = 9999

    def __init__(self, host, port):
        super().__init__(host, port)
        self.mutex = Lock()

    def _register(self, client):
        """ registers a new client """
        self.mutex.acquire()
        try:
            self.clients.append(client)
        finally:
            self.mutex.release()

    def _unregister(self, client):
        """ un-registers a new client """
        self.mutex.acquire()
        try:
            to_delete = None
            for idx, c in enumerate(self.clients):
                if c == client:
                    to_delete = idx
            del self.clients[idx]
        finally:
            self.mutex.release()

    def _handle_register(self, conn, msg):
        """ handles register request """
        host = conn.getpeername()[0]
        port = conn.getpeername()[1]
        client = Client(host=host, port=port)
        self.mutex.acquire()
        response = ""
        try:
            # TODO: improve logic
            if client in self.clients:
                self.clients.remove(client)
            self.clients.append(client)
            self.logger.info("Registered new client (%s: %s)"%(client.host, client.port))
            msg = Message()
            msg.method = "RES"
            msg.version = Message.VERSION
            msg.payload = "Success"
            response = str(msg)
        finally:
            self.mutex.release()
        return response

    def _handle_leave(self, conn, msg):
        """ handles leave request """
        self.mutex.acquire()
        c = Client(conn.getpeername()[0], conn.getpeername()[1])
        response = ""
        try:
            idx = self.clients.index(c)
            self.clients[idx].flag = Client.FLAG_INACTIVE
            self.logger.info("Removed client (%s: %s)"%(c.host, c.port))
            msg = Message()
            msg.method = "RES"
            msg.version = Message.VERSION
            msg.payload = "Success"
            response = str(msg)
        except (KeyError, ValueError):
            self.logger.info("Could not remove client (%s: %s)"%(c.host, c.port))
        finally:
            self.mutex.release()
        return response
    
    def _handle_pquery(self, conn, msg):
        """ handles query request """
        pass

    def _handle_keep_alive(self, conn, msg):
        """ handles keep-alive request """
        self.mutex.acquire()
        c = Client(conn.getpeername()[0], conn.getpeername()[1])
        response = ""
        try:
            idx = self.clients.index(c)
            self.clients[idx].ttl = 3600
            self.logger.info("Extended TTL for client (%s: %s)"%(c.host, c.port))
            msg = Message()
            msg.method = "RES"
            msg.version = Message.VERSION
            msg.payload = "Success"
            response = str(msg)
        except (KeyError, ValueError):
            self.logger.info("Could not extend TTL for client (%s: %s)"%(c.host, c.port))
        finally:
            self.mutex.release()
        return response

    def _new_message_callback(self, conn, msg):
        """ processes a message """
        p2pmsg = Message()
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
            response = func(conn, msg)
            self.messages[conn].put(bytes(str(response), 'utf-8'))
        except Exception as e:
            self.logger.error("Error processing message %s"%str(e))

    def _new_connection_callback(self, conn):
        """ process new connection """
        pass

if __name__ == "__main__":
    rs = RegistrationServer("127.0.0.1", 9999)
    try:
        rs.start()
    except Exception as err:
        print("Stopping...%s"%str(err))
        rs.stop()
