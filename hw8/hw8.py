try:
    from enthought.traits.api import HasTraits, Str, \
            Int, Float, Enum, DelegatesTo, This, Instance, \
            Button
    from enthought.traits.ui.api import View, Item, Group
except:
    from traits.api import HasTraits, Str, \
            Int, Float, Enum, DelegatesTo, This, Instance, \
            Button
    from traitsui.api import View, Item, Group


import urllib2
import json

class ImageManip(HasTraits):
	
	query = Str('')
	submit = Button('Submit')

	imgurl = Str('')
	
	imgdisplay = None

	manips = ['Refresh', 'Blur', 'Sharpen']

	def _submit_fired(self):
		'''
		Sets self.imgurl to the first result of a Google image search for the string
		stored in self.query
		'''

		queryurl = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s'
		request = urllib2.Request(queryurl%self.query, None, {'Referer': 'http://www.github.com/gibbonorbiter'})
		response = urllib2.urlopen(request)

		results = json.load(response)
		self.imgurl = results['responseData']['results'][0]['url']

		imgresult = results['responseData']['results'][0]
		height,  width = int(imgresult['height']), int(imgresult['width'])
		# imgraw = requests.get(imgurl).content
		img = Image.fromstring('RGB', (height, width), imgraw)


	view = View('query', Item('submit', show_label=False), 'imgurl', buttons=['Cancel', 'OK'])


gui = ImageManip(query='')
gui.configure_traits()