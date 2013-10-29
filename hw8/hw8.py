import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from Tkinter import *
import Image, ImageTk
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
	im = Image.open(buff).

	with open('tmp', 'wb') as f:
		f.write(urllib2.urlopen(newimgurl).read())

	imgurl.set(newimgurl)


root = Tk()
root.wm_title("Image search")
	
# fig = Figure(figsize=(5,4), dpi=100)
# ax = fig.add_subplot(111)


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()

# add text fields
query = StringVar(root)
query.set('...Enter search query...')
querylabel = Entry(root, textvariable=query)

imgurl = StringVar(root)
imgurl.set("...Image URL...")
imgurllabel = Label(root, textvariable=imgurl)

submit = Button(root, text="Submit", command=submitQuery)

img = Image.open('tmp')
tkimg = ImageTk.PhotoImage(img)
imglabel = Label(root, image=tkimg)

querylabel.pack(side=TOP)
submit.pack(side=TOP)
imgurllabel.pack(side=TOP)
canvas.get_tk_widget().pack(side=LEFT, expand=1)
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

# manips.pack(side=BOTTOM)

manips = ['Refresh', 'Blur', 'Sharpen']

root.mainloop()

