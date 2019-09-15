import sys
import queue
import socket
import select
from threading import Lock
from p2p.utils.server import Server
from p2p.protocol.proto import Message, MethodTypes

class Client(object):
    """ object to represent a P2PClient in RegistrationServer's list of clients """
    def __init__(self, host, port, cookie, flag, ttl, activity, last_active):
        self.host = host
        self.port = port
        self.cookie = cookie 
        self.flag = flag
        self.ttl = ttl
        self.activity = activity 
        self.last_active = last_active

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
        pass

    def _handle_leave(self, conn, msg):
        """ handles leave request """
        pass
    
    def _handle_pquery(self, conn, msg):
        """ handles query request """
        pass

    def _handle_keep_alive(self, conn, msg):
        """ handles keep-alive request """
        pass

    def _new_message_callback(self, conn, msg):
        """ processes a message """
        p2pmsg = Message()
        try:
            p2pmsg.from_str(msg.decode('utf-8'))
            handler = {
                MethodTypes.Register.name: self._handle_register(conn, p2pmsg),
                MethodTypes.Leave.name: self._handle_leave(conn, p2pmsg),
                MethodTypes.PQuery.name: self._handle_pquery(conn, p2pmsg),
                MethodTypes.KeepAlive.name: self._handle_keep_alive(conn, p2pmsg)
            }
            response = handler[p2pmsg.method]
            self.messages[conn].put(b'Response')
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
