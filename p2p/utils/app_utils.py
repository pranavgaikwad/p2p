from p2p.utils.app_constants import MAX_BUFFER_SIZE
from struct import pack, unpack
import logging
import socket
import errno
import time
from functools import wraps
from itertools import chain


def logger():
    _logger = logging.getLogger(__name__)
    if not _logger.hasHandlers():
        _logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(threadName)s %(levelname)s %(asctime)-15s %(message)s', '%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    return _logger


def flatten(nested):
    return chain.from_iterable(nested)


def retry(exceptions, tries=3, delay=2, _logger=logger()):
    """ retry calling the decorated function """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = '{}, Retrying in {} seconds...'.format(e, mdelay)
                    _logger.warning(msg)
                    time.sleep(mdelay)
                    mtries -= 1
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def get_true_hostname():
    name = socket.gethostname()
    return socket.gethostbyname(name)


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


class ForbiddenError(Exception):
    pass


class CriticalError(Exception):
    pass


class NotFoundError(Exception):
    pass
