import time
import random
from threading import Thread

from p2p.utils.app_constants import *
from p2p.server.rs import RegistrationServer
from p2p.client.client import Peer

random.seed(1)


def task1():
    rs = RegistrationServer(RS_HOST, RS_PORT)

    p0 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=GOAL_RFC_STATE)
    p1 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY)
    p2 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY)
    p3 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY)
    p4 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY)
    p5 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY)

    peers = [p0, p1, p2, p3, p4, p5]

    start = time.perf_counter()

    # start Registration Server
    rs_thread = Thread(target=rs.start)
    rs_thread.start()

    # start P2PServer on all peers
    for peer in peers:
        peer.start()

    tasks = [Thread(target=peer.main) for peer in peers]

    # start P2PClient task on all peers
    for task in tasks:
        task.start()

    # wait for all the tasks to complete
    for task in tasks:
        task.join()

    total_time = time.perf_counter() - start
    # print("Total time taken for all peers to fetch 60 RFCs: {} secs".format(total_time))

    # stop P2PServer on all peers
    for idx, peer in enumerate(peers):
        peer.stop()

    # stop Registration Server
    rs.stop()
    rs_thread.join()

    return total_time


def task2():
    rs = RegistrationServer(RS_HOST, RS_PORT)

    p0 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET1)
    p1 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET2)
    p2 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET3)
    p3 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET4)
    p4 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET5)
    p5 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET6)

    peers = [p0, p1, p2, p3, p4, p5]

    start = time.perf_counter()

    # start Registration Server
    rs_thread = Thread(target=rs.start)
    rs_thread.start()

    # start P2PServer on all peers
    for peer in peers:
        peer.start()

    tasks = [Thread(target=peer.main) for peer in peers]

    # start P2PClient task on all peers
    for task in tasks:
        task.start()

    # wait for all the tasks to complete
    for task in tasks:
        task.join()

    total_time = time.perf_counter() - start
    # print("Total time taken for all peers to fetch 60 RFCs: {} secs".format(total_time))

    # stop P2PServer on all peers
    for idx, peer in enumerate(peers):
        peer.stop()

    # stop Registration Server
    rs.stop()
    rs_thread.join()

    return total_time


if __name__ == '__main__':
    time1 = task1()
    # time.sleep(10)
    # time2 = task2()

    print("Task1:", time1)
    # print("Task2:", time2)
