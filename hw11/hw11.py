import pandas as pd
import pymc
from pymc import MCMC
from IPython.display import HTML
from matplotlib import pyplot as plt

df = pd.read_csv('laa_2011_april.txt', sep='\t', index_col=0)
HTML(df.head().to_html())

# ## (a) Maximum Likelihood Estimate of batting averages

avg_mle_april = df.H / df.AB.astype(float)
print 'Maximum Likelihood Estimate for each player'
print avg_mle_april

# ### Describe the model and save it to a file
import BattingAverage

# initialize the Markov Chain Monte Carlo model
M = MCMC(BattingAverage)

# ### the prior has the correct mean and variance
from scipy.stats import beta

B = beta(M.alpha, M.beta)
print """Beta distribution with alpha=%.4f and beta=%.4f yields mu=%.4f and sigma^2=%.4f
     """ % (M.alpha, M.beta, B.mean(), B.var())

# ## (b) Draw samples from the posterior
M.sample(20000, burn=2000, thin=20)

# ## (c) Check convergence of MCMC by plotting traces
fig, axs = plt.subplots(1, 3, figsize=(12, 4));
for i in range(3):
    axs[i].plot(M.avg.trace[:, i]);
    axs[i].set_title('Player %u' % i);
axs[0].set_ylabel('Batting average');
axs[1].set_xlabel('Sample');

# ## (d) Posterior mean and 95% CI for each player
avg_mcmc_mean = M.stats()['avg']['mean']
avg_mcmc_ci = M.stats()['avg']['95% HPD interval']

print
print 'MCMC mean for each player'
for m, ci in zip(avg_mcmc_mean, avg_mcmc_ci):
    print 'Mean: %.4f\tCI: (%.4f, %.4f)' % (m, ci[0], ci[1])

# transform confidence intervals for plotting
avg_mcmc_ci[:, 0] = avg_mcmc_mean - avg_mcmc_ci[:, 0]
avg_mcmc_ci[:, 1] = avg_mcmc_ci[:, 1] - avg_mcmc_mean

# ## (e) Full-season batting average versus MLE from April
df_full = pd.read_csv('laa_2011_full.txt', sep='\t')
avg_mle_full = df_full.H / df_full.AB.astype(float)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8));

# MLE: plot full-season average versus April average
ax1.scatter(avg_mle_full, avg_mle_april, s=50);
ax1.plot([0, 0.5], [0, 0.5], c='r', ls='--');
ax1.set_xlabel('Full-season AVG');
ax1.set_ylabel('April MLE');
ax1.set_title('Full-season AVG vs April MLE');

# MCMC: plot full-season average versus April average
ax2.errorbar(avg_mle_full, avg_mcmc_mean, yerr=avg_mcmc_ci.T, marker='.', mec='k', ms=15, ls='');
ax2.plot([0, 0.5], [0, 0.5], c='r', ls='--');
ax2.set_xlabel('Full-season AVG');
ax2.set_ylabel('April MCMC mean');
ax2.set_title('Full-season AVG vs April MCMC mean');

[a.set_aspect('equal') for a in (ax1, ax2)];
[a.set_xlim([0, 0.5]) for a in (ax1, ax2)];
[a.set_ylim([0, 0.5]) for a in (ax1, ax2)];

plt.draw(); plt.show();
