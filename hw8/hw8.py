import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import pyplot as plt

from Tkinter import *
import Image
from StringIO import StringIO
import numpy as np
import urllib2
import json


def submitQuery():
	'''
	Sets imgurl to the first result of a Google image search for the string
	stored in query
	'''

	query2 = urllib2.quote(query.get())
	queryurl = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s'
	request = urllib2.Request(queryurl%query2, None, {'Referer': 'http://www.github.com/gibbonorbiter'})
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
	img = np.array(Image.open(buff))

	ax.imshow(img)
	fig.canvas.draw()
	# with open('tmp', 'wb') as f:
	# 	f.write(urllib2.urlopen(newimgurl).read())

	imgurl.set(newimgurl)

def weird(img):

	normdist = norm(0, 1)
	shift_x = np.int32(normdist.cdf(np.linspace(-2, 2, img.shape[1]))*img.shape[1])
	shift_y = np.int32(normdist.cdf(np.linspace(-2, 2, img.shape[0]))*img.shape[0])

	def shift_func(coords):

		return (shift_y[coords[0]], shift_x[coords[1]])

	img = ndi.geometric_transform(img, shift_func)
	ax.imshow(img)
	fig.canvas.draw()
	return img


def destroy():
	root.quit()
	root.destroy()

root = Tk()
root.wm_title("Image search")
	
fig = Figure(figsize=(5,4), dpi=100)
ax = fig.add_subplot(111)
ax.tick_params(\
    which='both',
    bottom='off',
    top='off',
    left='off',
    right='off',
    labelbottom='off',
    labelleft='off')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()

# add query field
query = StringVar(root)
query.set('...Enter search query...')
querylabel = Entry(root, textvariable=query)

# add image url field
imgurl = StringVar(root)
imgurl.set("...Image URL...")
imgurllabel = Label(root, textvariable=imgurl)

# add submit button
submit = Button(root, text="Submit", command=submitQuery)
# add quit button
quit = Button(root, text='Quit', command=destroy)

# add manipulation buttons
manips = ['Weird', 'Blur', 'Sharpen']
weirdbutton = Button(root, text='Weird', command=weird)
blurbutton = Button(root, text='Blur', command=blur)

# pack everything
querylabel.pack(side=TOP)
submit.pack(side=TOP)
imgurllabel.pack(side=TOP)
canvas.get_tk_widget().pack(side=LEFT, expand=1)
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
weirdbutton.pack(side=BOTTOM)
quit.pack(side=BOTTOM)
# manips.pack(side=BOTTOM)

root.mainloop()




