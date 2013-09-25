import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd

goog = pd.read_csv('hw3_2_data/google_data.txt', sep='\t')
temps = pd.read_csv('hw3_2_data/ny_temps.txt', sep='\t')
yahoo = pd.read_csv('hw3_2_data/yahoo_data.txt', sep='\t')

fig, ax_stocks = plt.subplots()
ax_temp = ax_stocks.twinx()

ax_stocks.plot(goog['Modified Julian Date'].values, goog['Stock Value'].values, c='b')
ax_stocks.plot(yahoo['Modified Julian Date'].values, yahoo['Stock Value'].values, c='purple')
ax_temp.plot(temps['Modified Julian Date'].values, temps['Max Temperature'].values, 'r--')

ax_temp.set_ylim([-150, 100])
ax_temp.yaxis.set_major_locator(MultipleLocator(50))
ax_temp.yaxis.set_minor_locator(MultipleLocator(10))

plt.show()
plt.draw()


