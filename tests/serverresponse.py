from p2p.protocol.proto import ServerResponse as Message, ResponseStatus as Status
from p2p.protovol.proto import Headers, MethodTypes
import unittest
# defines protocols required by P2P-DI System

class ServerResponseTest(unittest.TestCase):
    """ a generic message used by servers and clients both """
    def test_to_dict(self):
        """ message to dict """
        msg_str = "Response 200 P2Pv1\nContentLength: 100\nContentType: text\n\nPayload"
        e = {
            "method": "GET",
            "version": "P2Pv1",
            "status": "200",
            "headers": {
                    "ContentLength": "100",
                    "ContentddType": "text"
                },
            "payload": "Payload"
        }
        msg = Message()
        msg.from_str(msg_str)
        self.assertEqual(msg.to_dict(), e)

        msg_str = "Response 400 P2Pv1\nContentLength: 20\n\nAnother Payload"
        e = {
            "method": "GET",
            "version": "P2Pv1",
            "status": "400",
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
        msg = Message("Success", Status.Success)
        self.assertEqual(str(msg), "Register 200 P2Pv1\n\nSuccess")
        pass 

if __name__ == "__main__":
    unittest.main()
