import os
from pathlib import Path

RS_PORT = 9998

RFC_PATH = os.path.join(Path(__file__).parent.parent.parent, "rfcs")
GOAL_RFC_STATE = set([str(n) for n in range(1001, 1061)])
