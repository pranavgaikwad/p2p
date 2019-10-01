import time
import random
from threading import Thread

from p2p.utils.app_constants import *
from p2p.utils.app_utils import NotFoundError
from p2p.server.rs import RegistrationServer
from p2p.client.client import Peer

random.seed(1)


def test():
    print("\nTESTING SCENARIO\n")

    rs = RegistrationServer(RS_HOST, RS_PORT)

    a = Peer("127.0.0.1", random.randint(64430, 64530), initial_rfc_state=RFC_SET_EMPTY)
    b = Peer("127.0.0.1", random.randint(64430, 64530), initial_rfc_state={'8451', '8464'})

    # start Registration Server
    rs_thread = Thread(name='RS', target=rs.start)
    rs_thread.start()
    print("Started Registration Server on {}:{}".format(rs.host, rs.port))

    # start P2PServer on A
    a_thread = Thread(target=a.start, args='A')
    a_thread.start()
    print("Started RFC Server at A on {}:{}".format(a.server.host, a.server.port))

    # start P2PServer on B
    b_thread = Thread(target=b.start, args='B')
    b_thread.start()
    print("Started RFC Server at B on {}:{}".format(b.server.host, b.server.port))

    # allow setup time
    delay = 2
    print("Thread setup delay, waiting for {} secs...".format(delay))
    time.sleep(delay)

    # A gets all active peers from RS, which in this case is just B
    print("RFC Client at A tries to fetch list of active peers from RS")
    active_peers = a.get_active_peers()
    print("Active peers returned by RS to A's RFC Client: {}".format(active_peers))
    peer_b = active_peers[0]

    # A gets B's RFCIndex
    print("RFC Client at A tries to fetch B's RFC Index")
    b_index = a.RFCQuery(peer_b)
    print("B's RFC Index: {}".format(b_index))
    b_index = a._flatten(b_index)

    # Download only one of the RFCs from B
    rfc = b_index.pop()
    print("RFC Client at A tries to fetch RFC{}".format(rfc))
    _rfc = a.fetch_interested_rfc(peer_b, rfc)
    print("First 200 bytes of RFC received... \n{}".format(str(_rfc)[:200]))

    # B leaves the system
    b.Leave()
    print("B leaves P2P-DI system")
    b_thread.join()

    # A pings RS to get all active peers, since no active peer is found A will throw a NotFoundError after 3 tries
    try:
        print("RFC Client at A tries to get active peers again...")
        a.get_active_peers()
    except NotFoundError as e:
        print("After 3 retries, RFC Client at A throws exception: {}".format(e))

    # cleanup
    print("Cleanup operations, stop RFC Server at A and Registration Server")
    a.Leave()
    a_thread.join()

    rs.stop()
    rs_thread.join()


if __name__ == '__main__':
    test()
