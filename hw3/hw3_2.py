import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

class rectSelector(object):
	
	def __init__(self, fig, df):
		
		self.fig = fig
		self.df = df
		self.cid_on = fig.canvas.mpl_connect('button_press_event', self)
		self.cid_off = fig.canvas.mpl_connect('button_release_event', self)
		self.cid_move = None
		self.feats = {'lim1': [-np.inf, +np.inf], 'lim2': [-np.inf, +np.inf], 'feat1': None, 'feat2': None}

	def __call__(self, event):

		if event.inaxes is None: return
		if event.name=='button_press_event':
			self.on_press(event)
		elif event.name=='button_release_event':
			self.on_release(event)

	def on_press(self, event):
		
		if len(self.fig.axes[0].patches)>0:
			print 'press and patch was already there'
			self.rect['patch'].remove()
			self.feats['lim1'] = [-np.inf, +np.inf]
			self.feats['lim2'] = [-np.inf, +np.inf]
			self.filterData()
			plt.draw()


		(feat1, feat2) = [feat for ax, feat in ax2feat.iteritems() if ax==event.inaxes][0]
		
		self.feats = {'feat1': feat1, 'feat2': feat2,
					'lim1': [event.xdata]*2, 'lim2':[event.ydata]*2}

		self.initializeRect(event.xdata, event.ydata)

		event.inaxes.add_patch(self.rect['patch'])

		self.cid_move = self.fig.canvas.mpl_connect('motion_notify_event', self.on_move)

	def on_release(self, event):
		self.fig.canvas.mpl_disconnect(self.cid_move)

	def on_move(self, event):

		self.rect['w'] = event.xdata - self.rect['x']
		self.rect['h'] = event.ydata - self.rect['y']
		self.rect['patch'].set_width(self.rect['w'])
		self.rect['patch'].set_height(self.rect['h'])

		self.feats['lim1'] = [self.rect['x'], event.xdata]
		if event.xdata<self.rect['x']:
			self.feats['lim1'] = self.feats['lim1'][::-1]

		self.feats['lim2'] = [self.rect['y'], event.ydata]
		if event.ydata<self.rect['y']:
			self.feats['lim2'] = self.feats['lim2'][::-1]

		self.filterData()
		
		plt.show()
		
	def initializeRect(self, x, y):
		self.rect = {'x': x, 'y': y, 'w': 0., 'h': 0.}
		self.rect.update({'patch': Rectangle([self.rect['x'], self.rect['y']], self.rect['w'], self.rect['h'], alpha=0.3)})

	def filterData(self):

		feat1 = self.feats['feat1']
		feat2 = self.feats['feat2']
		lim1 = self.feats['lim1']
		lim2 = self.feats['lim2']
		df = self.df
		ix = np.vstack((df[feat1]>lim1[0], df[feat1]<lim1[1],
			df[feat2]>lim2[0], df[feat2]<lim2[1])).all(0)
		colors = np.array([colordict[i] for i in df['species']], dtype = 'S4')

		colors[~ix] = 'gray'

		for sc in scatters:
			sc.set_color(colors)


df = pd.read_csv('../../hw_3_data/flowers.csv')
df.columns = [i.replace(' ', '_') for i in df.columns]

features = list(df.columns)
features.remove('species')

fig, axs = plt.subplots(4, 4)

ax2feat, feat2ax = {}, {}
colordict = {'setosa': 'y', 'versicolor': 'c', 'virginica': 'm'}
colors = [colordict[i] for i in df['species']]
scatters = []
for i, feat_x in enumerate(features):
	for j, feat_y in enumerate(features[::-1]):
		scatters.append(axs[j][i].scatter(df[feat_x], df[feat_y], color=colors))
		ax2feat.update({axs[j][i]: (feat_x, feat_y)})
		feat2ax.update({(feat_x, feat_y): axs[i][j]})

[axs[0][i].set_title(feat_i) for i, feat_i in enumerate(features)]
[axs[j][0].set_ylabel(feat_j) for j, feat_j in enumerate(features[::-1])]
for i in range(len(features)):
	for j in range(len(features)):
		if i>0:
			axs[j, i].set_yticklabels('')
		if j<(len(features)-1):
			axs[j, i].set_xticklabels('')

plt.show()


rectSelector(fig, df)