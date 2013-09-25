import pandas as pd
import matplotlib.pyplot as plt

eff = pd.read_csv('hw3_1_data/Efficiency.txt', sep=' ')
pur = pd.read_csv('hw3_1_data/Purity.txt', sep=' ')

# plot efficiency data + error
fig, axs = plt.subplots(1, 2, figsize=(12, 6))
fig.set_facecolor('w')
[a.set_aspect('equal') for a in axs]

axs[0].plot(eff.frac_followed[1:], eff.frac_observed[1:], 'k')
axs[0].fill_between(eff.frac_followed[1:].values, 
	(eff.frac_observed[1:]-eff.frac_observed_uncertainty[1:]).values, 
	(eff.frac_observed[1:]+eff.frac_observed_uncertainty[1:]).values, edgecolor='0.5', color='0.75')

[a.set_ylim([-0.05, 1.05]) for a in axs]
[a.set_xlim([-0.05, 1.05]) for a in axs]

# plot 20% line
ix = abs(eff.frac_followed-0.2).argmin()
axs[0].plot([0.2, 0.2], [-0.05, eff.frac_observed.ix[ix]], c='k', ls='--', lw=2)

# plot unity line
axs[0].plot([0., 1.], [0., 1,], c='k')

# annotate
arrowprops = {'width': 1.5, 'frac': 0.2, 'shrink': 0.05, 'color': 'k'}
axs[0].annotate('Random\nguessing', [0.8, 0.8], [0.72, 0.5],
	arrowprops=arrowprops)
axs[0].annotate('Follow up 20% of\nbursts to capture ~55%\nof high-z events',
	[0.2, eff.frac_observed.ix[ix]], [0.4, 0.2], arrowprops=arrowprops)

# label everything
titlefontdict={'weight': 'bold', 'size': 20}
axs[0].set_title('Efficiency', fontdict=titlefontdict)
axs[0].set_ylabel('Fraction of high (z>4) GRBs observed')
axs[0].set_xlabel('Fraction of GRBs Followed Up')

# plot purity data + error
axs[1].plot(pur.frac_followed[1:], pur.frac_observed[1:], 'k')
axs[1].fill_between(pur.frac_followed[1:].values, 
	(pur.frac_observed[1:]-pur.frac_observed_uncertainty[1:]).values, 
	(pur.frac_observed[1:]+pur.frac_observed_uncertainty[1:]).values, edgecolor='0.5', color='0.75')

ix = abs(pur.frac_followed-0.2).argmin()
axs[1].plot([0.2, 0.2], [-0.05, pur.frac_observed.ix[ix]], c='k', ls='--', lw=2)

# label everything
axs[1].set_title('Purity', fontdict=titlefontdict)
axs[1].set_ylabel('Percent of observed high GRBs that are hight z (z>4)')
axs[1].set_xlabel('Fraction of GRBs Followed Up')

# plot "random" line
axs[1].plot([0., 1.], [18./135., 18./135.], c='k')

# annotate
axs[1].annotate('Random\nguessing', [0.6, 18./135.], [0.55, 0.45],
	arrowprops=arrowprops)
axs[1].annotate('If 20% of events are\nfollowed up, ~40% of\nthem will be high-z',
	[0.2, pur.frac_observed.ix[ix]], [0., 0.75], arrowprops=arrowprops)

fig.savefig('EfficiencyPurityAnnotated_RG.png')
plt.show()