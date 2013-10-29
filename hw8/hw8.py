try:
    from enthought.traits.api import HasTraits, Str, \
            Int, Float, Enum, DelegatesTo, This,Instance
    from enthought.traits.ui.api import View, Item, Group
except:
    from traits.api import HasTraits, Str, \
            Int, Float, Enum, DelegatesTo,This,Instance
    from traitsui.api import View, Item, Group


class SearchQuery(HasTraits):

	pass

class ImgURL(HasTraits):

	pass

class ImgDisplay(HasTraits):
	pass

class ImgManip(HasTraits):
	pass