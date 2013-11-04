import multiprocessing

from random import uniform
def throw(n):
    nhits = 0
    for i in xrange(n):
        if sum([uniform(0, 1)**2, uniform(0, 1)**2])<1:
            nhits += 1
    return nhits

if __name__=='__main__':

	ncpus = multiprocessing.cpu_count()
	pool = multiprocessing.Pool(processes=ncpus)

	nthrows = 100
	result = pool.apply(throw, [nthrows/ncpus])
	# result.get()
	print '# cpus: %u' % ncpus
	print result
