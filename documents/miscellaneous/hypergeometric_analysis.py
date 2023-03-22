
# M = total_population
# n = number_unique
# N = number_selected

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import hypergeom

# [total_population, number_unique, number_of_choices] = [20, 7, 12]
#
# rv = hypergeom(total_population, number_unique, number_of_choices)
#
# x = np.arange(0, number_unique+1)
#
# pmf_dogs = rv.pmf(x)
# breakpoint()
#
# fig = plt.figure()
#
# ax = fig.add_subplot(111)
#
# ax.plot(x, pmf_dogs, 'bo')
#
# ax.vlines(x, 0, pmf_dogs, lw=2)
#
# ax.set_xlabel('# of dogs in our group of chosen animals')
#
# ax.set_ylabel('hypergeom PMF')
#
# plt.show()


total_number_themes = 5000
number_unique_themes = 100
number_of_choices = 80

total_population = total_number_themes
number_unique = number_unique_themes
number_selected = number_of_choices

prob_num_selected = list(range(0, 30))

prb = hypergeom.cdf(
    prob_num_selected, total_population, number_unique, number_selected
)

fig = plt.figure()

ax = fig.add_subplot(111)

ax.plot(prob_num_selected, prb, 'bo')

ax.vlines(prob_num_selected, 0, prb, lw=2)

ax.set_xlabel('>= that num')

ax.set_ylabel('hypergeom CDF')

plt.show()
