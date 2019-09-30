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

    # special response types
    Response = 7


class Headers(Enum):
    """ headers """
    ContentLength = 1
    ContentType = 2
    Cookie = 3


class ResponseStatus(Enum):
    """ server response status """
    Success = 200
    BadMessage = 400
    Forbidden = 403
    MethodNotAllowed = 405
    InternalError = 500
    Unknown = 999


# defines protocols required by P2P-DI System
class Message(object):
    """ message """

    # component identifiers
    CP_META = 0
    CP_PAYLOAD = 1

    # meta identifiers
    MT_METHOD_VERSION = 0
    MT_HEADERS = 1

    # separators
    SR_COMPONENT = "<cs>"
    SR_FIELDS = "<fs>"
    SR_HEADERS = "<hs>"

    VERSION = "P2Pv1"

    def __init__(self):
        self.method = ""
        self.version = ""
        self.headers = {}
        self.payload = ""
        self.logger = logging.getLogger(__name__)

    def to_bytes(self):
        return bytes(self.__str__(), 'utf-8')

    def from_bytes(self, msg):
        return self.from_str(msg.decode('utf-8'))

    def from_str(self, msg):
        """ loads a message from string """
        try:
            meta, self.payload = self._get_components(msg)
            meta = meta.split(self.SR_HEADERS)
            self.method, self.version = meta[self.MT_METHOD_VERSION].split(self.SR_FIELDS)
            if len(meta) > 1:
                self.headers.update(self._get_headers(meta[self.MT_HEADERS]))
            return self
        except Exception as e:
            self.logger.error("Error parsing message: {}".format(e))
            raise ValueError("Invalid message {}".format(e))

    def __str__(self):
        method_version = self.SR_FIELDS.join([self.method, self.version])
        if self.headers:
            header_str = self.SR_FIELDS.join(["{}: {}".format(k, v) for k, v in self.headers.items()])
            meta = self.SR_HEADERS.join([method_version, header_str])
        else:
            meta = method_version
        return self.SR_COMPONENT.join([meta, self.payload])

    def to_dict(self):
        """ dict representation of message """
        d = self.__dict__
        del d['logger']
        return d

    def _get_components(self, msg):
        meta, payload = msg.split(self.SR_COMPONENT)
        return meta, payload

    def _get_headers(self, header_str):
        return dict([h.split(': ') for h in [_ for _ in header_str.split(self.SR_FIELDS)]])


class ServerResponse(Message):
    """ a special message sent by server as a response """

    # component identifiers
    CP_STATUS = 2

    def __init__(self, response=None, status=ResponseStatus.Success.value):
        super(ServerResponse, self).__init__()
        self.method = MethodTypes.Response.name
        self.version = Message.VERSION
        self.payload = response
        self.status = status

    def __str__(self):
        return self.SR_COMPONENT.join([super().__str__(), str(self.status)])

    def from_str(self, msg):
        """ loads a message from string """
        try:
            super().from_str(msg)
            self.status = msg.split(self.SR_COMPONENT)[self.CP_STATUS]
            return self
        except:
            raise ValueError("Invalid message")

    def _get_components(self, msg):
        meta, payload, _ = msg.split(self.SR_COMPONENT)
        return meta, payload
