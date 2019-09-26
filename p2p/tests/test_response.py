from p2p.proto.proto import ServerResponse as Message, ResponseStatus as Status
from p2p.proto.proto import Headers, MethodTypes
import unittest


# defines protocols required by P2P-DI System

class ServerResponseTest(unittest.TestCase):
    """ a generic message used by servers and clients both """

    def test_to_dict(self):
        """ message to dict """
        msg_str = "Response<fs>P2Pv1<hs>ContentLength: 7<cs>Success<cs>200"
        e = {
            "method": "Response",
            "version": "P2Pv1",
            "headers": {
                "ContentLength": "7"
            },
            "payload": "Success",
            "status": "200"
        }
        msg = Message()
        msg.from_str(msg_str)
        self.assertEqual(msg.to_dict(), e)

        msg_str = "Response<fs>P2Pv1<hs>ContentLength: 6<cs>Failed<cs>400"
        e = {
            "method": "Response",
            "version": "P2Pv1",
            "headers": {
                "ContentLength": "6",
            },
            "payload": "Failed",
            "status": "400"
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
        msg = Message()
        msg.method = MethodTypes.Response.name
        msg.headers = {'hf1': 'hv1', 'hf2': 'hv2'}
        msg.payload = "Success"
        msg.status = "200"
        self.assertEqual(str(msg), "Response<fs>P2Pv1<hs>hf1: hv1<fs>hf2: hv2<cs>Success<cs>200")
        pass


if __name__ == "__main__":
    unittest.main()
