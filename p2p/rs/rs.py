import sys
import queue
import socket
import select
from p2p.logger import logger
from p2p.protocol.proto import Message, MethodTypes
from threading import Lock

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
class Server(object):
    """ multi-client server """
    PORT = 9999

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.stopped = False
        self.conn = None
        self.logger = logger()
        self.messages = {} # message queue

    def _new_connection_callback(self, conn):
        """ callback for new connection. override """
        pass

    def _new_message_callback(self, conn, msg):
        """ callback for new message. override """
        pass

    def start(self):
        """ starts the server """
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setblocking(0)
        server_addr = (self.host, self.port)
        self.conn.bind(server_addr)
        self.conn.listen(5)
        inputs = [self.conn]
        outputs = []
        while inputs and not self.stopped:
            # listen for connections
            readable, writeable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                if s is self.conn:
                    conn, client = s.accept()
                    self.logger.info("Accepted connection from %s"%str(client))
                    inputs.append(conn)
                    self.messages[conn] = queue.Queue()
                    self._new_connection_callback(conn)
                else:
                    data = s.recv(1024)
                    if data:
                        self.logger.info("Received message '%s' from %s"%(str(data),str(s)))
                        if s not in outputs:
                            outputs.append(s)
                        self._new_message_callback(s, data)
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del self.messages[s]

            for s in writeable:
                self.logger.info("In writeable...")
                try:
                    next_msg = self.messages[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                else:
                    s.send(next_msg)

            for s in exceptional:
                inputs.remove(s)
                for s in outputs:
                    outputs.remove(s)
                s.close()
                del self.messages[s]

    def stop(self):
        """ stops the server """
        self.stopped = True
        try:
            self.conn.shutdown(1)
            self.conn.close()
        except OSError:
            self.logger.error('Error shutting down socket...')


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
                MethodTypes.Register.name: _handle_register,
                MethodTypes.Leave.name: _handle_leave,
                MethodTypes.PQuery.name: _handle_pquery,
                MethodTypes.KeepAlive.name: _handle_keep_alive
            }
            func = handler[p2pmsg.method]
            self.func()
            self.messages.put(b'Response')
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
        print("Stopping...")
        rs.stop()
