from ast import literal_eval

import matplotlib.pyplot as plt
import numpy as np


def plot_bar_x(x1, y1, title=None, filename=None):
    plt.bar(x1, y1, width=0.4, color='#ffab91')
    plt.xlabel("Peer")
    plt.ylabel("Cumulative Time")
    plt.xticks(x1)
    plt.yticks(np.linspace(0, max(y1), 20))
    plt.title(title, pad=10)
    plt.savefig(filename)
    plt.show()


with open('data1.txt') as f:
    data = literal_eval(f.read())
    data['P0'] = (0.000, {})

data = sorted(map(lambda i: (i[0], i[1][0]), data.items()), key=lambda i: i[0])
x_axis, y_axis = list(map(lambda d: d[0], data)), list(map(lambda d: d[1], data))

_title = "[Task-1] Time taken by each Peer to download 50 RFCs"
plot_bar_x(x_axis, y_axis, _title, "Task-1_Local")
