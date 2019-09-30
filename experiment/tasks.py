import random
import queue
from threading import Thread
from pprint import pprint

from p2p.utils.app_constants import *
from p2p.server.rs import RegistrationServer
from p2p.client.client import Peer

random.seed(1)


def task1():
    rs = RegistrationServer(RS_HOST, RS_PORT)

    p0 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=GOAL_RFC_STATE)
    p1 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY, goal_rfc_state=GOAL_RFC_STATE)
    p2 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY, goal_rfc_state=GOAL_RFC_STATE)
    p3 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY, goal_rfc_state=GOAL_RFC_STATE)
    p4 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY, goal_rfc_state=GOAL_RFC_STATE)
    p5 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET_EMPTY, goal_rfc_state=GOAL_RFC_STATE)

    peers = {str(p1): ('P1', p1),
             str(p2): ('P2', p2),
             str(p3): ('P3', p3),
             str(p4): ('P4', p4),
             str(p5): ('P5', p5)}

    result_queue = queue.Queue()

    # start Registration Server
    rs_thread = Thread(target=rs.start)
    rs_thread.start()

    # start peer P0:
    p0_thread = Thread(target=p0.start)
    p0_thread.start()

    # start P2PServer on all other peers
    for (alias, peer) in peers.values():
        peer.start()

    t1 = Thread(target=lambda: result_queue.put(p1.main()))
    t2 = Thread(target=lambda: result_queue.put(p2.main()))
    t3 = Thread(target=lambda: result_queue.put(p3.main()))
    t4 = Thread(target=lambda: result_queue.put(p4.main()))
    t5 = Thread(target=lambda: result_queue.put(p5.main()))

    tasks = [t1, t2, t3, t4, t5]

    # start P2PClient task on all other peers
    for task in tasks:
        task.start()

    # wait for all the tasks to complete
    for task in tasks:
        task.join()

    # stop P2PServer on other peers
    for (_, peer) in peers.values():
        peer.stop()

    # stop P2PServer on P0
    p0.stop()
    p0_thread.join()

    # stop Registration Server
    rs.stop()
    rs_thread.join()

    peers[str(p0)] = ('P0', p0)

    return _map_alias(peers, result_queue)


def task2():
    rs = RegistrationServer(RS_HOST, RS_PORT)

    p0 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET1, goal_rfc_state=GOAL_RFC_STATE)
    p1 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET2, goal_rfc_state=GOAL_RFC_STATE)
    p2 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET3, goal_rfc_state=GOAL_RFC_STATE)
    p3 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET4, goal_rfc_state=GOAL_RFC_STATE)
    p4 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET5, goal_rfc_state=GOAL_RFC_STATE)
    p5 = Peer("127.0.0.1", random.randint(65430, 65530), initial_rfc_state=RFC_SET6, goal_rfc_state=GOAL_RFC_STATE)

    peers = {str(p0): ('P0', p0),
             str(p1): ('P1', p1),
             str(p2): ('P2', p2),
             str(p3): ('P3', p3),
             str(p4): ('P4', p4),
             str(p5): ('P5', p5)}

    result_queue = queue.Queue()

    # start Registration Server
    rs_thread = Thread(target=rs.start)
    rs_thread.start()

    # start P2PServer on all peers
    for (alias, peer) in peers.values():
        peer.start()

    t0 = Thread(target=lambda: result_queue.put(p0.main()))
    t1 = Thread(target=lambda: result_queue.put(p1.main()))
    t2 = Thread(target=lambda: result_queue.put(p2.main()))
    t3 = Thread(target=lambda: result_queue.put(p3.main()))
    t4 = Thread(target=lambda: result_queue.put(p4.main()))
    t5 = Thread(target=lambda: result_queue.put(p5.main()))

    tasks = [t0, t1, t2, t3, t4, t5]

    # start P2PClient task on all peers
    for task in tasks:
        task.start()

    # wait for all the tasks to complete
    for task in tasks:
        task.join()

    # stop P2PServer on all peers
    for (_, peer) in peers.values():
        peer.stop()

    # stop Registration Server
    rs.stop()
    rs_thread.join()

    return _map_alias(peers, result_queue)


def _map_alias(peers, result_queue):
    results = {}
    while not result_queue.empty():
        pstr, total, times = result_queue.get()
        d = {}
        for k, v in times.items():
            d[peers[k][0]] = v
        results[peers[pstr][0]] = (total, d)
    return results


def _total_time(results):
    """ since all peers are performing tasks in parallel, total time will be the max of all peers' cumulative time """
    total = 0
    for (cumulative_time, _) in results.values():
        if cumulative_time > total:
            total = cumulative_time
    return total


def _print(task, results):
    print("TASK {} Results:\n".format(task))
    pprint(results)
    print("\nTotal Time: {}".format(_total_time(results)))


if __name__ == '__main__':
    _print(1, task1())
    # _print(2, task2())
