#!/usr/bin/env python

import matplotlib.pyplot as plt
from numpy.random import normal
from numpy import arange
from itertools import chain


def parabola(x):
    return -0.4*(x*x) + 4*x - 6.5


xs = list(arange(2.0, 5.5, 0.25))
rand_xs = [x + normal(scale=0.1) for x in xs]
rand_ys = [x + normal(scale=0.2) - 1 for x in xs]


pxs = list(arange(1.5, 6.5, 0.2))

prand_xs = [x + normal(scale=0.2) for x in pxs]
prand_ys = [parabola(x) + normal(scale=0.2) for x in pxs]

# plt.scatter(rand_xs, rand_ys, alpha=0.2)
# plt.scatter(prand_xs, prand_ys, alpha=0.2)

plt.scatter(list(chain(rand_xs, prand_xs)), list(chain(rand_ys, prand_ys)), alpha=0.4, color='k')

xs_line = list(arange(1.25, 5.5, 0.1))
plt.plot(xs_line, [x - 1 for x in xs_line])

xs_para = list(arange(1, 6.7, 0.1))
plt.plot(xs_para, [parabola(x) + 0.15 for x in xs_para])

plt.xlabel('aspect 1')
plt.ylabel('aspect 2')
plt.show()
