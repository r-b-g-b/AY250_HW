import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class rectSelector(object):
	def __call__(self, event):
		print event.keys
		self.event = event
	def __init__(self, event):
        for i in dir(event):
            print i, event[i]




df = pd.read_csv('../../hw_3_data/flowers.csv')
df.columns = [i.replace(' ', '_') for i in df.columns]

features = list(df.columns)
features.remove('species')

fig, axs = plt.subplots(4, 4)
colordict = {'setosa': 'b', 'versicolor': 'c', 'virginica': 'm'}
colors = [colordict[i] for i in df['species']]
for i, feat_i in enumerate(features):
	for j, feat_j in enumerate(features):
		axs[i][j].scatter(df[feat_i], df[feat_j], color=colors)

fig = plt.figure()
fig.canvas.mpl_connect('button_press_event', rectSelector)
