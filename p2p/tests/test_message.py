from p2p.proto.proto import Message, Headers, MethodTypes
import unittest


# defines protocols required by P2P-DI System

class MessageTest(unittest.TestCase):
    """ a generic message used by servers and clients both """

    def test_to_dict(self):
        """ message to dict """
        msg_str = "GET P2Pv1\nContentLength: 100\nContentType: text\n\nPayload"
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

        msg_str = "GET P2Pv1\nContentLength: 20\n\nAnother Payload"
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

        msg_str = ""
        msg = Message()
        with self.assertRaises(ValueError):
            msg.from_str(msg_str)

    def test_str(self):
        """ string representation of message """
        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "Payload"
        self.assertEqual(str(msg), "Register P2Pv1\n\nPayload")
        pass


if __name__ == "__main__":
    unittest.main()
