import os
from pathlib import Path

#  well known host and port for registration server
RS_HOST = "127.0.0.1"
RS_PORT = 9999
RS = (RS_HOST, RS_PORT)

RFC_PATH = os.path.join(Path(__file__).parent.parent.parent, "rfcs")
GOAL_RFC_STATE = set([str(n) for n in range(1001, 1061)])

# RFC_PATH = os.path.join(Path(__file__).parent.parent.parent, "dummy_rfcs")
# GOAL_RFC_STATE = set([str(n) for n in range(1001, 1011)])

MAX_BUFFER_SIZE = 8192
