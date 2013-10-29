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

		queryurl = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s'
		request = urllib2.Request(queryurl%query, None, {'Referer': 'http://www.github.com/gibbonorbiter'})
		response = urllib2.urlopen(request)

		results = json.load(response)
		imgurl = results['responseData']['results'][0]['url']

	view = View('query', Item('submit', show_label=False), 'imgurl')


gui = ImageManip(query='')
gui.configure_traits()