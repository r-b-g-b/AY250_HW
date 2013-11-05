from IPython.parallel import Client
import multiprocessing
import time
import numpy as np
import pandas as pd
import sys
# import subprocess

# ### Run IPython parallel
def run_ipython_parallel(engines, nthrows):
    '''
    Runs nthrows on the IPython cluster engines and returns the run duration
    '''
    tic = time.time()
    pi_est = engines.apply_sync(throw, nthrows/len(engines))
    toc = time.time()
    time_elapsed = toc-tic
    pi_est = 4. * float(sum(pi_est)) / nthrows
    return time_elapsed

# ### Run multiprocessing parallel
def run_multiproc_parallel(pool, nthrows):
    '''
    Runs nthrows in the multiprocessing pool and returns the run duration
    '''
    tic = time.time()
    ncpus = multiprocessing.cpu_count()
    pi_est = pool.map(throw, [nthrows/ncpus]*ncpus)
    toc = time.time()
    time_elapsed = toc-tic
    pi_est = 4. * float(sum(pi_est)) / nthrows
    return time_elapsed

# ### Run serial
def run_serial(nthrows):
    '''
    Runs nthrows serially and returns the run duration
    '''
    tic = time.time()
    throw(nthrows)
    toc = time.time()
    time_elapsed = toc-tic
    return time_elapsed

# ### Throw n darts
def throw(n):
    '''
    Performs a Monte Carlo approximation of pi
    Throws n darts into a unit square (i.e. uniformly samples the square)
    and sums the number of darts that land in a circle with unit radius
    centered at the lower left
    '''
    from random import uniform
    nhits = 0
    for i in xrange(n):
        if sum([uniform(0, 1)**2, uniform(0, 1)**2])<1:
            nhits += 1
    return nhits

def errorfill(x, y, yerr, ax = None, color = None, **kwargs):
    '''
    Given the x, y, and y errors, constructs a plot of those values
    '''

    if ax is None: fig, ax = plt.subplots()

    if color is None:
        color = ax._get_lines.color_cycle.next()

    x_hi = y + yerr
    x_lo = y - yerr
    l = ax.plot(x, y, color = color, **kwargs)
    l_up = ax.plot(x, y+yerr, color = color, alpha = 0.2)
    l_lo = ax.plot(x, y-yerr, color = color, alpha = 0.2)
    ax.fill_between(x, x_hi, x_lo, alpha = 0.2, color = color)
    
    return ax

def run(ns, engines, pool):
    '''
    Run serial, IPython parallel, and multiprocessing parallel
    '''
    nengines = len(engines)
    df = pd.DataFrame(columns = ['type', 'time', 'nthrows'])
    for n in ns:
        n -= n%nengines # make sure the nthrows is a multiple of nengines
        print 'Running %u throws' % n
        for i in range(3):
            
            # run serial
            time_elapsed = run_serial(n)
            df = df.append(dict(type='serial', time=time_elapsed, nthrows=n), ignore_index=True)
            
            # run IPython parallel
            time_elapsed = run_ipython_parallel(engines, n)
            df = df.append(dict(type='parallel_ipython', time=time_elapsed, nthrows=n), ignore_index=True)
            
            # run multiprocessing parallel
            time_elapsed= run_multiproc_parallel(pool, n)
            df = df.append(dict(type='parallel_multiproc', time=time_elapsed, nthrows=n), ignore_index=True)

    return df

def analyze(df):
    '''
    Takes a DataFrame containing timing data from all the runs.
    Calculates the simulation rate ("simrate") as the number of throws
    divided by the time to complete.

    Also calcualtes the mean times and rates for type (serial, ipython,
    multiprocessing) and number of throws

    Returns the time means, time errors and simrate means
    '''
    # calculate simulation rate
    df['simrate'] = df.nthrows / df.time
    
    # calculate means
    gp = df.groupby(('type', 'nthrows'))
    time_means = gp.time.apply(np.mean).unstack('type')
    time_errs = gp.time.apply(np.std).unstack('type')
    simrate_means = gp.simrate.apply(np.mean).unstack('type')

    return time_means, time_errs, simrate_means

def plot_results(ns, time_means, time_errs, simrate_means):
    '''
    Plots the mean times, mean simulation rates.
    Outputs the figure to a file "performance.png" in the current directory
    '''
    ### Plot
    from matplotlib import pyplot as plt
    fig = plt.figure()
    ax1 = fig.add_axes([0.125, 0.1, 0.8, 0.75])
    ax2 = plt.twinx(ax1)
    keys = ['serial', 'parallel_ipython', 'parallel_multiproc']
    for key in keys:
        errorfill(ns, time_means[key].values, \
            yerr=time_errs[key].values, marker='.', label=key+': time', ax=ax1);
        ax2.plot(ns, simrate_means[key].values, \
            ls='--', marker='.', label=key+': throw rate');

    [a.set_xscale('log') for a in (ax1, ax2)]
    [a.set_yscale('log') for a in (ax1, ax2)]
    [a.set_xlim([min(ns), max(ns)]) for a in (ax1, ax2)]
    [ax1.set_xticks(ns)]

    # combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='lower right', fontsize=10)

    # add text labels
    ax1.set_ylabel('Time (s)')
    ax2.set_ylabel('Throw rate (throws/s)')
    ax1.set_xlabel('N throws')
    title = 'Performance comparison\nSerial vs IPython/multiprocessing parallel'
    machine_descr = 'Unspecified computer'
    ax1.set_title('%s\n(%s)' % (title, machine_descr))

    # save figure
    fig.savefig('performance.png')
    plt.close();

if __name__=='__main__':
    
    # start IPython engines
    try:
        rc = Client()
    except IOError:
        print 'Please start an IPython cluster by entering\n\t>> ipcluster start\nin the terminal.'
        sys.exit(1)

    engines = rc[:]
    nengines = len(engines)
    print 'Using %u processors.' % nengines

    # start multiprocessing pool
    pool = multiprocessing.Pool()

    ns = 10**np.arange(2, 5)
    df = run(ns, engines, pool)

    time_means, time_errs, simrate_means = analyze(df)
    plot_results(ns, time_means, time_errs, simrate_means)