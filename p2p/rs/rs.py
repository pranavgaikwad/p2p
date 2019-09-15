import sys
import queue
import socket
import select
from p2p.logger import logger
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

class RegistrationServer(object):
    """ Registration Server """
    PORT = 9999

    def __init__(self, host, port):
        self.clients = []
        self.mutex = Lock()
        self.started = True
        self.conn = None
        self.host = host
        self.port = port
        self.logger = logger()

    def register(self, client):
        """ registers a new client """
        self.mutex.acquire()
        try:
            self.clients.append(client)
        finally:
            self.mutex.release()

    def unregister(self, client):
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

    def start(self):
        """ starts the server """
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setblocking(0)
        server_addr = (self.host, self.port)
        self.conn.bind(server_addr)
        self.conn.listen(5)
        inputs = [self.conn]
        outputs = []
        messages = {} # message queue
        while inputs and self.started:
            # listen for connections
            readable, writeable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                if s is self.conn:
                    conn, client = s.accept()
                    print("Accepted connection from %s"%str(client))
                    inputs.append(conn)
                    messages[conn] = queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        print("Received message '%s' from %s"%(str(data),str(s)))
                        messages[s].put(data)
                        if s not in outputs:
                            outputs.append(s)
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del messages[s]

            for s in writeable:
                print("Writeable...")
                try:
                    next_msg = messages[s].get_nowait()
                except queue.Queue.Empty:
                    print("Empty queue")
                    outputs.remove(s)
                else:
                    s.send(next_msg)

            for s in exceptional:
                print("Handling exception")
                inputs.remove(s)
                for s in outputs:
                    outputs.remove(s)
                s.close()
                del messages[s]

    def stop(self):
        """ stops the server """
        self.started = False
        pass

    def send(self, msg):
        """ sends a new message """
        pass

    def receive(self):
        """ receives a new message """
        pass

if __name__ == "__main__":
    rs = RegistrationServer("127.0.0.1", 9999)
    rs.start()
