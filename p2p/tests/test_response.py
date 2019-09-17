from p2p.proto.proto import ServerResponse as Message, ResponseStatus as Status
from p2p.proto.proto import Headers, MethodTypes
import unittest


# defines protocols required by P2P-DI System

class ServerResponseTest(unittest.TestCase):
    """ a generic message used by servers and clients both """

    def test_to_dict(self):
        """ message to dict """
        msg_str = "Response 200 P2Pv1\nContentLength: 7\n\nSuccess"
        e = {
            "method": "Response",
            "version": "P2Pv1",
            "status": "200",
            "headers": {
                "ContentLength": "7",
            },
            "payload": "Success"
        }
        msg = Message("Success", Status.Success.value)
        msg.from_str(msg_str)
        self.assertEqual(msg.to_dict(), e)

        msg_str = "Response 400 P2Pv1\nContentLength: 6\n\nFailed"
        e = {
            "method": "Response",
            "version": "P2Pv1",
            "status": "400",
            "headers": {
                "ContentLength": "6",
            },
            "payload": "Failed"
        }
        msg = Message("Failed", Status.BadMessage.value)
        msg.from_str(msg_str)
        self.assertEqual(msg.to_dict(), e)

        msg_str = ""
        msg = Message("Failed", 0)
        with self.assertRaises(ValueError):
            msg.from_str(msg_str)

    def test_str(self):
        """ string representation of message """
        msg = Message("Success", Status.Success.value)
        self.assertEqual(str(msg), "Response 200 P2Pv1\n\nSuccess")
        pass


if __name__ == "__main__":
    unittest.main()
