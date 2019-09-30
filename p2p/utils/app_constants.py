import os
from pathlib import Path

# well known host and port for registration server
RS_HOST = "192.168.10.54"
# RS_HOST = "0.0.0.0"
RS_PORT = 65423
RS = (RS_HOST, RS_PORT)

MAX_BUFFER_SIZE = 8192

# RFC constants for latest RFC data
RFC_SET1 = {'8451', '8464', '8423', '8433', '8461', '8496', '8429', '8459', '8485', '8470'}  # 10 RFCs
RFC_SET2 = {'8428', '8436', '8487', '8438', '8486', '8455', '8445', '8460', '8483', '8493'}  # 10 RFCs
RFC_SET3 = {'8457', '8463', '8474', '8458', '8479', '8435', '8456', '8477', '8467', '8425'}  # 10 RFCs
RFC_SET4 = {'8475', '8462', '8432', '8426', '8481', '8443', '8437', '8449', '8441', '8447'}  # 10 RFCs
RFC_SET5 = {'8480', '8473', '8434', '8472', '8465', '8442', '8439', '8424', '8440', '8454'}  # 10 RFCs
RFC_SET6 = {'8431', '8466', '8478', '8471', '8453', '8450', '8430', '8446', '8484', '8427'}  # 10 RFCs
RFC_SET_EMPTY = set()  # 0 RFCs
GOAL_RFC_STATE = RFC_SET1 | RFC_SET2 | RFC_SET3 | RFC_SET4 | RFC_SET5 | RFC_SET6  # 60 RFCs

# RFC_PATH = os.path.join(Path(__file__).parent.parent.parent, "rfcs_very_large")
# RFC_PATH = os.path.join(Path(__file__).parent.parent.parent, "rfcs_large")
RFC_PATH = os.path.join(Path(__file__).parent.parent, "rfcs")
