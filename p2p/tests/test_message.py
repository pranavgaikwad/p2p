from p2p.proto.proto import Message, Headers, MethodTypes
from p2p.proto.proto import ServerResponse as Response
import unittest


# defines protocols required by P2P-DI System

class MessageTest(unittest.TestCase):
    """ a generic message used by servers and clients both """

    def test_to_dict(self):
        """ message to dict """
        msg_str = "GET<fs>P2Pv1<hs>ContentLength: 100<fs>ContentType: text<cs>Payload"
        e = {
            "method": "GET",
            "version": "P2Pv1",
            "headers": {
                "ContentLength": "100",
                "ContentType": "text"
            },
            "payload": "Payload"
        }
        msg = Message()
        msg.from_str(msg_str)
        self.assertEqual(msg.to_dict(), e)

        msg_str = "GET<fs>P2Pv1<hs>ContentLength: 20<cs>Another Payload"
        e = {
            "method": "GET",
            "version": "P2Pv1",
            "headers": {
                "ContentLength": "20"
            },
            "payload": "Another Payload"
        }
        msg = Message()
        msg.from_str(msg_str)
        self.assertEqual(msg.to_dict(), e)

        msg_str = "GET<fs>P2Pv1<cs>Another Payload"
        e = {
            "method": "GET",
            "version": "P2Pv1",
            "headers": {},
            "payload": "Another Payload"
        }
        msg = Message()
        msg.from_str(msg_str)
        self.assertEqual(msg.to_dict(), e)

        msg_str = ""
        msg = Message()
        with self.assertRaises(ValueError):
            msg.from_str(msg_str)

    def test_str(self):
        """ string representation of message """
        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {'hf1': 'hv1', 'hf2': 'hv2'}
        msg.version = Message.VERSION
        msg.payload = "Payload"
        self.assertEqual(str(msg), "Register<fs>P2Pv1<hs>hf1: hv1<fs>hf2: hv2<cs>Payload")
        pass


if __name__ == "__main__":
    unittest.main()
