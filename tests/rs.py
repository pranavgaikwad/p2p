import time
import socket 
import unittest
import threading
from p2p.rs.rs import RegistrationServer
from p2p.protocol.proto import Message, MethodTypes

class RegistrationServerTest(unittest.TestCase): 
    """ Registration Server Tests"""
    def test_register(self):
        """ registers a new client """
        pass
    
    def test_unregister(self):
        """ un-registers a new client """
        pass
    
    def _socket_connect_test(self):
        """ connects to a server socket """
        client = socket.socket()
        client.connect(('127.0.0.1', RegistrationServer.PORT))
        time.sleep(5)
        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "Payload"
        client.send(bytes(str(msg), 'utf-8'))
        data = client.recv(1024)
        print(data.decode('utf-8'))
        client.close()

    def test_start(self):
        """ starts the server and tries connecting """
        threads = []
        for i in range(3):
            threads.append(threading.Thread(target=self._socket_connect_test))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def test_stop(self):
        """ stops the server """
        pass

    def test_send(self):
        """ sends a new message """
        pass

    def test_receive(self):
        """ receives a new message """
        pass

if __name__ == "__main__":
    unittest.main()
