from threading import Lock
import socket

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
    RS_PORT = 9999

    def __init__(self):
        self.clients = []
        self.mutex = Lock()
        self.started = True

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
        while self.started:
            # listen for connections
            pass

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
