from IPython.parallel import Client
import multiprocessing
import time
import numpy as np
import pandas as pd

# import subprocess

# ### Run IPython parallel
def run_ipython_parallel(engines, nthrows):
    tic = time.time()
    pi_est = engines.apply_sync(throw, nthrows/len(engines))
    toc = time.time()
    time_elapsed = toc-tic
    pi_est = 4. * float(sum(pi_est)) / nthrows
    return time_elapsed

# ### Run multiprocessing parallel
def run_multiproc_parallel(pool, nthrows):
    tic = time.time()
    ncpus = multiprocessing.cpu_count()
    pi_est = pool.map(throw, [nthrows/ncpus]*ncpus)
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

# subprocess.call(['ipcluster', 'start'])
# start IPython engines
rc = Client()
engines = rc[:]
nengines = len(engines)
print 'Using %u processors.' % nengines

# start multiprocessing pool
pool = multiprocessing.Pool()

n_exps = range(2, 6) # 10**n

# ### Run serial, IPython parallel, and multiprocessing parallel
df = pd.DataFrame(columns = ['type', 'time', 'nthrows'])
for n_exp in n_exps:
    n = 10**n_exp
    n -= n%nengines # make sure the nthrows is a multiple of nengines
    for i in range(3):
        
        # run serial
        time_elapsed = run_serial(n)
        df = df.append(dict(type='serial', time=time_elapsed, nthrows=n_exp), ignore_index=True)
        
        # run IPython parallel
        time_elapsed = run_ipython_parallel(engines, n)
        df = df.append(dict(type='parallel_ipython', time=time_elapsed, nthrows=n_exp), ignore_index=True)
        
        # run multiprocessing parallel
        time_elapsed= run_multiproc_parallel(pool, n)
        df = df.append(dict(type='parallel_multiproc', time=time_elapsed, nthrows=n_exp), ignore_index=True)

# subprocess.call(['ipcluster', 'stop'])

df['simrate'] = 10**df.nthrows / df.time
gp = df.groupby(('type', 'nthrows'))

time_means = gp.time.apply(np.mean).unstack('type')
time_errs = gp.time.apply(np.std).unstack('type')
simrate_means = gp.simrate.apply(np.mean).unstack('type')
simrate_errs = gp.simrate.apply(np.std).unstack('type')
print df.head()
print time_means
print time_errs
print simrate_means
print simrate_errs

# ### Plot
from matplotlib import pyplot as plt
fig, ax1 = plt.subplots()
ax2 = plt.twinx(ax1)
keys = ['serial', 'parallel_ipython', 'parallel_multiproc']
for key in keys:
    ax1.errorbar(n_exps, np.log10(time_means[key].values), \
        yerr=np.log10(time_errs[key].values), marker='.', label=key);
    ax2.errorbar(n_exps, np.log10(simrate_means[key].values), \
        yerr=np.log10(simrate_errs[key].values), ls='--', marker='.');
ax1.legend(loc='best');
fig.savefig('performance.png')
plt.draw();
plt.show();