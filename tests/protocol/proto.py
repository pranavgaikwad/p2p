import unittest
# defines protocols required by P2P-DI System

class Message(unittest.TestCase):
    """ a generic message used by servers and clients both """
    def test_encode(self):
        """ encodes the message into bytes """
        pass

    def test_decode(self):
        """ decodes the message from bytes """
        pass 
