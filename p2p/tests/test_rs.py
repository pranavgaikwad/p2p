import time
import socket
import unittest
import threading
from p2p.server.rs import RegistrationServer
from p2p.proto.proto import Message, MethodTypes


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
        msg.payload = "nick-name\n7000"
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

    def _socket_error_test(self):
        """ connects to socket and fails the requests """
        client = socket.socket()
        client.connect(('127.0.0.1', RegistrationServer.PORT))
        time.sleep(2)
        msg = Message()
        msg.method = "Unknown"
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "Invalid message"
        client.send(msg.to_bytes())
        data = client.recv(1024)
        self.fail_buffer.append(data.decode('utf-8'))
        client.close()

    def test_start(self):
        """ starts the server and tries connecting """
        threads = []
        self.buffer = []
        self.fail_buffer = []
        rs = RegistrationServer('127.0.0.1', RegistrationServer.PORT)
        server_thread = threading.Thread(target=rs.start, kwargs=dict(timeout=30, ))
        server_thread.start()
        time.sleep(5)
        # test success tests
        for i in range(3):
            threads.append(threading.Thread(target=self._socket_connect_test))
            threads.append(threading.Thread(target=self._socket_error_test))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        server_thread.join()
        expected = 'Response 200 P2Pv1\n\nSuccess'

        self.assertEqual([expected, expected, expected], self.buffer)
        expected = 'Response 405 P2Pv1\n\nMethod not allowed'
        self.assertEqual([expected, expected, expected], self.fail_buffer)

    def test_stop(self):
        """ stops the server """
        pass


if __name__ == "__main__":
    unittest.main()
