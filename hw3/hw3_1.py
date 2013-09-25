import pandas as pd
import matplotlib.pyplot as plt

eff = pd.read_csv('hw3_1_data/Efficiency.txt', sep=' ')
pur = pd.read_csv('hw3_1_data/Purity.txt', sep=' ')

# plot efficiency data + error
fig, axs = plt.subplots(1, 2)
axs[0].plot(eff.frac_followed[1:], eff.frac_observed[1:], 'k')
axs[0].fill_between(eff.frac_followed[1:].values, 
	(eff.frac_observed[1:]-eff.frac_observed_uncertainty[1:]).values, 
	(eff.frac_observed[1:]+eff.frac_observed_uncertainty[1:]).values, edgecolor='0.5', color='0.75')

# plot unity line
axs[0].plot([0., 1.], [0., 1,], c='k')

# annotate
axs[0].annotate('Random\nguessing', [0.8, 0.8], [0.67, 0.5],
	arrowprops={'width': 1, 'frac': 0.2, 'color': 'k'})

# label everything
axs[0].set_title('Efficiency')
axs[0].set_ylabel('Fraction of high (z>4) GRBs observed')
axs[0].set_xlabel('Fraction of GRBs Followed Up')


# plot purity data + error
axs[1].plot(pur.frac_followed[1:], pur.frac_observed[1:], 'k')
axs[1].fill_between(pur.frac_followed[1:].values, 
	(pur.frac_observed[1:]-pur.frac_observed_uncertainty[1:]).values, 
	(pur.frac_observed[1:]+pur.frac_observed_uncertainty[1:]).values, edgecolor='0.5', color='0.75')

# label everything
axs[1].set_title('Purity')
axs[1].set_ylabel('Percent of observed high GRBs that are hight z (z>4)')
axs[1].set_xlabel('Fraction of GRBs Followed Up')