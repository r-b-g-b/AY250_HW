import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import pyplot as plt

from Tkinter import *

import Image
from skimage import transform, filter
from scipy import signal as sig
from StringIO import StringIO
import numpy as np
import urllib2, json

class imageManip(object):

	def __init__(self):

		self.root = Tk()
		self.root.wm_title("Image search")
			
		self.fig = Figure(figsize=(5,4), dpi=100)
		self.ax = self.fig.add_subplot(111)
		self.ax.tick_params(\
		    which='both',
		    bottom='off',
		    top='off',
		    left='off',
		    right='off',
		    labelbottom='off',
		    labelleft='off')

		canvas = FigureCanvasTkAgg(self.fig, master=self.root)
		canvas.show()

		# add query field
		self.query = StringVar(self.root)
		self.query.set('...Enter search query...')
		querylabel = Entry(self.root, textvariable=self.query)
		self.queryurl = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s'

		# add image url field
		self.imgurl = StringVar(self.root)
		self.imgurl.set("...Image URL...")
		imgurllabel = Label(self.root, textvariable=self.imgurl)

		# add submit button
		submit = Button(self.root, text="Submit", command=self.submitQuery)
		# add quit button
		quit = Button(self.root, text='Quit', command=self.destroy)

		# add manipulation buttons
		blurbutton = Button(self.root, text='Blur', command=self.blur)
		flipbutton = Button(self.root, text='Flip', command=self.flip)
		fishbutton = Button(self.root, text='Fish', command=self.fish)

		# pack everything
		querylabel.pack(side=TOP)
		submit.pack(side=TOP)
		imgurllabel.pack(side=TOP)
		canvas.get_tk_widget().pack(side=LEFT, expand=1)
		canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
		blurbutton.pack(side=LEFT)
		flipbutton.pack(side=LEFT)
		fishbutton.pack(side=LEFT)
		quit.pack(side=RIGHT)
		# manips.pack(side=BOTTOM)


	def submitQuery(self):
		'''
		Sets imgurl to the first result of a Google image search for the string
		stored in query
		'''

		query2 = urllib2.quote(self.query.get())
		
		request = urllib2.Request(self.queryurl%query2, None, {'Referer': 'http://www.github.com/gibbonorbiter'})
		response = urllib2.urlopen(request)

		results = json.load(response)
		responseData = results['responseData']['results']
		if len(responseData)==0:
			print results
			return

		newimgurl = results['responseData']['results'][0]['url']
		buff = StringIO()
		buff.write(urllib2.urlopen(newimgurl).read())
		buff.seek(0)
		self.img = np.array(Image.open(buff))

		self.refreshimg()
		# with open('tmp', 'wb') as f:
		# 	f.write(urllib2.urlopen(newimgurl).read())

		self.imgurl.set(newimgurl)


	def blur(self):
		'''
		implements a simple mean blur
		'''
		wind = np.ones((10., 10.), dtype=float)
		wind = wind/wind.sum()
		if len(self.img.shape)>2:
			for i in xrange(self.img.shape[-1]):
				self.img[..., i] = sig.convolve2d(self.img[..., i], wind, 'same')
		else:
			self.img = sig.convolve2d(self.img, np.ones((10, 10)), 'same')

		self.refreshimg()


	def fish(self):
		'''
		expands the image to produce a fisheye effect
		code adapted from skimage demo
		'''
		def fisheye(xy):
			center = np.mean(xy, axis=0)
			xc, yc = (xy - center).T

			# Polar coordinates
			r = np.sqrt(xc**2 + yc**2)
			theta = np.arctan2(yc, xc)

			r = 0.87 * np.exp(r**(1/2.5) / 1.75)

			return np.column_stack(( \
				r * np.cos(theta), r * np.sin(theta)
				)) + center

		self.img = transform.warp(self.img, fisheye)
		self.refreshimg()

	def flip(self):
		'''
		flips the image over its horizontal axis
		'''
		self.img = self.img[::-1, ...]
		self.refreshimg()

	def refreshimg(self):
		'''
		redraws the image
		'''
		if len(self.img.shape)==2:
			self.ax.imshow(self.img, cmap='gray')
		else:
			self.ax.imshow(self.img)
		self.fig.canvas.draw()

	def destroy(self):
		'''
		stop the mainloop and close the window
		'''
		self.root.quit()
		self.root.destroy()


gui = imageManip()
gui.root.mainloop()
