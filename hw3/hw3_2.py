import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd

# load data
yahoo = pd.read_csv('hw3_2_data/yahoo_data.txt', sep='\t')
goog = pd.read_csv('hw3_2_data/google_data.txt', sep='\t')
temps = pd.read_csv('hw3_2_data/ny_temps.txt', sep='\t')

# initialize figure
fig, ax_stocks = plt.subplots(figsize=(9, 6))
ax_temp = ax_stocks.twinx()

# plot to axes
l1 = ax_stocks.plot(yahoo['Modified Julian Date'].values, yahoo['Stock Value'].values, c='purple', lw=1.5, label='Yahoo! Stock Value')
l2 = ax_stocks.plot(goog['Modified Julian Date'].values, goog['Stock Value'].values, c='b', lw=1.5, label='Google Stock Value')
l3 = ax_temp.plot(temps['Modified Julian Date'].values, temps['Max Temperature'].values, 'r', lw=1.5, dashes=[5,2], label='NY Mon. High Temp')

ax_stocks.set_ylabel('Value (Dollars)')
ax_temp.set_ylabel(u'Temperature (\xb0F)')
ax_stocks.set_xlabel('Date (MJD)')

# set title
ax_stocks.set_title('New York Temperature, Google, and Yahoo!')

# format y-axis
ax_stocks.yaxis.set_major_locator(MultipleLocator(100))
ax_stocks.yaxis.set_minor_locator(MultipleLocator(20))

# format x-axis
ax_stocks.set_xlim([48800, 55600])
ax_stocks.xaxis.set_major_locator(MultipleLocator(1000))
ax_stocks.xaxis.set_minor_locator(MultipleLocator(200))

# format y-axis
ax_temp.set_ylim([-150, 100])
ax_temp.yaxis.set_major_locator(MultipleLocator(50))
ax_temp.yaxis.set_minor_locator(MultipleLocator(10))

# add legend
lines = l1+l2+l3
labels = [l.get_label() for l in lines]
ax_temp.legend(lines, labels, loc='center left', frameon=False, fontsize=12)

plt.draw()
plt.show()

fig.savefig('stocks_RG.png')
