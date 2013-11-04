
from IPython.parallel import Client
import time
import numpy as np
import pandas as pd
import subprocess
from matplotlib import pyplot as plt

# ### Run IPython parallel
def run_ipython_parallel(engines, nthrows):
    tic = time.time()
    pi_est = eall.apply_sync(throw, nthrows/nengines)
    toc = time.time()
    time_elapsed = toc-tic
    pi_est = 4. * float(sum(pi_est)) / nthrows
    return time_elapsed

# ### Run serial
def run_serial(nthrows):
    tic = time.time()
    throw(nthrows)
    toc = time.time()
    time_elapsed = toc-tic
    return time_elapsed

# ### Throw n darts
def throw(n):
    from random import uniform
    nhits = 0
    for i in xrange(n):
        if sum([uniform(0, 1)**2, uniform(0, 1)**2])<1:
            nhits += 1
    return nhits

# Start cluster
subprocess.call(['ipcluster', 'start'])
engines = Client()
nengines = len(engines)

n_exps = range(2, 6) # nthrows = 10**n_exp
print n_exps

df = pd.DataFrame(columns = ['type', 'time', 'nthrows'])
for n_exp in n_exps:
    n = 10**n_exp
    n -= n%nengines # make sure the nthrows is a multiple of nengines
    print n
    for i in range(10):
        # run serial
        time_elapsed = run_serial(n)
        df = df.append(dict(type='serial', time=time_elapsed, nthrows=n_exp), ignore_index=True)
        # run IPython paralle
        time_elapsed = run_ipython_parallel(engines, n)
        df = df.append(dict(type='parallel_ipython', time=time_elapsed, nthrows=n_exp), ignore_index=True)

# ### Plot

gp = df.groupby(('type', 'nthrows'))

time_means = gp.time.apply(np.mean).unstack('type')
print time_means

fig, ax = plt.subplots()
np.log10(time_means).plot(marker='.', ax=ax);
ax.set_xlabel('log10( N throws )');
ax.set_ylabel('log10( duration )');

# ### Call engines using "apply_sync" and passing nthrows/nengines

