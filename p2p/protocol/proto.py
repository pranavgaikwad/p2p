import struct
import logging
from enum import Enum

class MethodTypes(Enum):
    # peer to RS
    Register = 1
    Leave = 2 
    PQuery = 3
    KeepAlive = 4
    # peer to peer
    RFCQuery = 5 
    GetRFC = 6

class Headers(Enum):
    """ headers """
    ContentLength = 1
    ContentType = 2

# defines protocols required by P2P-DI System
class Message(object):
    """ message """
    VERSION = "P2Pv1"

    # separators 
    SR_HEADERS="\n"
    SR_FIELDS=" "
    
    def __init__(self):
        self.method = ""
        self.version = ""
        self.headers = {}
        self.payload = ""
        self.logger = logging.getLogger(__name__)

    def from_str(self, msg):
        """ loads a message from string """
        try:
            meta = msg.split('\n\n')[0]
            payload = msg.split('\n\n')[1]
            meta_lines = meta.split('\n')
            self.method = meta_lines[0].split(' ')[0]
            self.version = meta_lines[0].split(' ')[1]
            headers = {}
            for line in meta_lines[1:]:
                header = line.split(': ')[0]
                value = line.split(': ')[1]
                headers[header] = value
            self.headers = headers
            self.payload = payload
            return self
        except:
            raise ValueError("Invalid message")

    def __str__(self):
        headers_str = ""
        for header, value in self.headers.items():
            headers_str = "%s%s: %s\n"%(headers_str, header, value)
        return "%s%s%s%s%s%s%s"%(self.method, self.SR_FIELDS, self.version,
            self.SR_HEADERS, headers_str, self.SR_HEADERS, self.payload)

    def to_dict(self):
        """ dict representation of message """
        return {
            "method": self.method,
            "version": self.version,
            "headers": self.headers,
            "payload": self.payload
        }

