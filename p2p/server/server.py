import time
import queue
import socket
import select
import errno
from math import inf
from p2p.utils.app_utils import logger, send, recv


class Server(object):
    """ multi-client server """

    # reconcile interval
    INTERVAL = 5

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.stopped = False
        self.conn = None
        self.logger = logger()
        self.messages = {}  # message queue

    def _new_connection_callback(self, conn):
        """ callback for new connection. override """
        pass

    def _new_message_callback(self, conn, msg):
        """ callback for new message. override """
        pass

    def _on_start(self):
        """ startup operations. override """
        pass

    def _reconcile(self):
        """ reconcile loop """
        pass

    def start(self, timeout=inf):
        """ starts the server """
        self._on_start()

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setblocking(0)
        self.conn.bind((self.host, self.port))
        self.conn.listen(5)

        inputs = [self.conn]
        outputs = []
        timeout = time.time() + timeout
        self.logger.info("Started server on (%s, %s)" % (self.host, self.port))
        while not self.stopped and inputs and time.time() < timeout:
            try:
                # listen for connections
                readable, writeable, exceptional = select.select(inputs, outputs, inputs, Server.INTERVAL)

                # reconcile state
                self._reconcile()

                for s in readable:
                    if s is self.conn:
                        conn, client = s.accept()
                        self.logger.info("Accepted connection from %s" % str(client))
                        inputs.append(conn)
                        self.messages[conn] = queue.Queue()
                        self._new_connection_callback(conn)
                    else:
                        data = recv(s)
                        if data:
                            self.logger.info(
                                "Received message {} from {}:{}".format(data, s.getpeername()[0], s.getpeername()[1]))
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
                    try:
                        next_msg = self.messages[s].get_nowait()
                    except queue.Empty:
                        outputs.remove(s)
                    except KeyError:
                        pass
                    else:
                        send(s, next_msg)

                for s in exceptional:
                    inputs.remove(s)
                    for s in outputs:
                        outputs.remove(s)
                    s.close()
                    del self.messages[s]

            except OSError as e:
                if e.errno == errno.EBADF:
                    self.stopped = True
                    continue
                raise e
        else:
            self.logger.info("Server running on {}:{} stopped".format(self.host, self.port))
            self.stop()

    def stop(self):
        """ stops the server """
        self.stopped = True
        try:
            self.conn.close()
        except OSError as e:
            self.logger.error('Error shutting down socket... {}'.format(e))
