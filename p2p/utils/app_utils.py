from p2p.utils.app_constants import MAX_BUFFER_SIZE
from struct import pack, unpack
import logging
import socket
import errno
import time


def logger():
    _logger = logging.getLogger(__name__)
    if not _logger.hasHandlers():
        console_handler = logging.StreamHandler()
        _logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s %(asctime)-15s %(message)s', '%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    return _logger


def send(sock, msg):
    if not isinstance(msg, bytes):
        msg = msg.to_bytes()
    msg = pack('>I', len(msg)) + msg
    sent = 0
    while sent != len(msg):
        upto = min(len(msg) - sent, MAX_BUFFER_SIZE)
        try:
            sent += sock.send(msg[sent: sent + upto])
        except socket.error as e:
            if e.errno == errno.EAGAIN:
                time.sleep(0.1)
                continue
            raise e


def recv(sock):
    raw_len = _recv(sock, 4)
    if not raw_len:
        return b''
    msg_len = unpack('>I', raw_len)[0]
    data = _recv(sock, msg_len)
    return data


def _recv(sock, msg_len):
    data = b''
    while len(data) < msg_len:
        packet = sock.recv(_get_buffer_size(msg_len, len(data)))
        if not packet:
            return data
        data += packet
    return data


def _get_buffer_size(msg_length, buffer_length):
    remaining_msg_size = msg_length - buffer_length
    if remaining_msg_size > MAX_BUFFER_SIZE:
        return MAX_BUFFER_SIZE
    return remaining_msg_size
