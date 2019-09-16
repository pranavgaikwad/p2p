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
        time.sleep(4)
        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "Payload"
        client.send(msg.to_bytes())
        data = client.recv(1024)
        msg.method = MethodTypes.KeepAlive.name
        client.send(msg.to_bytes())
        data = client.recv(1024)
        msg.method = MethodTypes.Leave.name
        client.send(msg.to_bytes())
        data = client.recv(1024)
        self.buffer.append(data.decode('utf-8'))
        client.close()

    def test_start(self):
        """ starts the server and tries connecting """
        threads = []
        self.buffer = []
        rs = RegistrationServer('127.0.0.1', RegistrationServer.PORT)
        server_thread = threading.Thread(target=rs.start, kwargs=dict(timeout=25,))
        server_thread.start()
        time.sleep(5)
        for i in range(3):
            threads.append(threading.Thread(target=self._socket_connect_test))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        server_thread.join()
        self.assertEqual(['RES P2Pv1\n\nSuccess', 'RES P2Pv1\n\nSuccess', 'RES P2Pv1\n\nSuccess'], self.buffer)

    def test_stop(self):
        """ stops the server """
        pass

if __name__ == "__main__":
    unittest.main()
