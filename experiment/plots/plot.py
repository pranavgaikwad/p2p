from ast import literal_eval

import matplotlib.pyplot as plt
import numpy as np


def plot_bar_x(x1, y1, x2, y2, title=None, filename=None):
    N = 6
    width = 0.4
    ind = np.arange(N)
    fig, ax = plt.subplots()
    task1 = ax.bar(ind, y1, width=width, color='#ffab91')
    task2 = ax.bar(ind + width, y2, width=width, color='#a5d6a7')

    # add some
    ax.set_ylabel("Cumulative Time")
    ax.set_xlabel("Peer")
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(('P0', 'P1', 'P2', 'P3', 'P4', 'P5'))

    ax.legend((task1[0], task2[0]), ('Task-1', 'Task-2'))

    plt.yticks(np.linspace(0, max(y1 + y2), 20))
    plt.title(title, pad=10)
    plt.savefig(filename)
    plt.show()


with open('data1.txt') as f:
    data1 = literal_eval(f.read())
    data1['P0'] = (0.000, {})

with open('data2.txt') as f:
    data2 = literal_eval(f.read())

data1 = sorted(map(lambda i: (i[0], i[1][0]), data1.items()), key=lambda i: i[0])
data2 = sorted(map(lambda i: (i[0], i[1][0]), data2.items()), key=lambda i: i[0])
x_axis1, y_axis1 = list(map(lambda d: d[0], data1)), list(map(lambda d: d[1], data1))
x_axis2, y_axis2 = list(map(lambda d: d[0], data2)), list(map(lambda d: d[1], data2))

_title = "Time taken by each Peer to download 50 Very Large RFCs"
plot_bar_x(x_axis1, y_axis1, x_axis2, y_axis2, _title, "Local Very Large")
