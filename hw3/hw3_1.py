import pandas as pd
import matplotlib.pyplot as plt

eff = pd.read_csv('hw3_1_data/Efficiency.txt', sep=' ')
pur = pd.read_csv('hw3_1_data/Purity.txt', sep=' ')


fig, axs = plt.subplots(1, 2)
axs[0].plot(eff.frac_followed[1:], eff.frac_observed[1:])
axs[0].fill_between(eff.frac_followed[1:].values, (eff.frac_observed[1:]-eff.frac_observed_uncertainty[1:]).values, (eff.frac_observed[1:]+eff.frac_observed_uncertainty[1:]).values, color='gray')