import wx
import xmlrpclib
from scipy.ndimage import imread
import os
from glob import glob
import Image
from numpy import array, uint8

class Frame(wx.Frame):
	
	def __init__(self, title, server):

		wx.Frame.__init__(self, None, title=title, size=(540, 150))
		
		self.server = server
		self.methods = server.system.listMethods()
		# set base directory
		self.clientbasedir = os.getcwd()

		# bind window close to confirmation dialog
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		# make the menu
		menuBar = wx.MenuBar()
		menu = wx.Menu()
		m_exit = menu.Append(wx.ID_EXIT, 'E&xit\tAlt-X', 'Close window and exit program.')

		self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
		menuBar.Append(menu, '%File')
		self.SetMenuBar(menuBar)

		# make the status bar
		self.statusbar = self.CreateStatusBar()

		# make a text panel
		panel = wx.Panel(self)
		box = wx.BoxSizer(wx.HORIZONTAL)

		# add a file select button
		m_fdialog = wx.Button(panel, label='Choose image')
		m_fdialog.Bind(wx.EVT_BUTTON, self.OnSelectImage)
		box.Add(m_fdialog, 0, wx.ALL, 10)

		# add a method select button
		method_list = wx.ListCtrl(panel)
		method_list.InsertColumn(0, 'Method')
		for i, method in enumerate(self.methods):
			if not method.startswith('_') and not method.startswith('system'):
				method_list.InsertStringItem(i, method)
		box.Add(method_list, 0, wx.ALL, 10)
		method_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectMethod)

		method_button = wx.Button(panel, label='Apply method to image')
		method_button.Bind(wx.EVT_BUTTON, self.OnRun)

		box.Add(method_button, 0, wx.ALL, 10)

		# add a close button
		m_close = wx.Button(panel, wx.ID_CLOSE, 'Close')
		m_close.Bind(wx.EVT_BUTTON, self.OnClose)
		box.Add(m_close, 0, wx.ALL, 10)

		panel.SetSizer(box)
		panel.Layout()

	def OnClose(self, event):
		dlg = wx.MessageDialog(self,
			'Do you really want to close this application?',
			'Confirm Exit', wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		dlg.Destroy()
		if result==wx.ID_OK:
			self.Destroy()

	def OnSelectImage(self, event):
		dlg = wx.FileDialog(self,
			wildcard='Images|*.jpeg;*.jpg;*.png;*.tif;*.tiff;*.bmp|\
			All files|*.*',
			defaultDir=self.clientbasedir,
			style = wx.OK|wx.CANCEL)
		# dlg.SetDirectory(self.clientbasedir)
		# dlg.SetWildcard('*.jpg*.jpeg*')
		if dlg.ShowModal() == wx.ID_OK:
			self.imgpath = dlg.GetPath()
		dlg.Destroy()

		self.img = Image.open(self.imgpath)
		self.imgshape = list(self.img.size)
		self.imgshape.extend([len(self.img.getbands())])
		self.imglist = array(self.img).flatten().tolist()

	def OnSelectMethod(self, event):
		self.method = self.methods[event.m_itemIndex]

	def OnRun(self, event):

		if not hasattr(self, 'img'):
			dlg = wx.MessageDialog(self, 'Please select an image.', 'Confirm', wx.OK)
			result = dlg.ShowModal()
			dlg.Destroy()
			return
		if not hasattr(self, 'method'):
			dlg = wx.MessageDialog(self, 'Please select a method.', 'Confirm', wx.OK)
			result = dlg.ShowModal()
			dlg.Destroy()
			return

		imglist2, imgshape2, suffix = eval('server.%s(self.imglist, self.imgshape, self.imgpath)' % self.method)
		self.img2 = Image.fromarray(array(imglist2).astype(uint8).reshape(imgshape2))
		
		# save images
		img_base, img_exten = os.path.splitext(self.imgpath)
		self.img.save(os.path.join('%s_client_original_%3.3u%s' % (img_base, suffix, img_exten)))
		self.img2.save(os.path.join('%s_client_%s_%3.3u%s' % (img_base, self.method, suffix, img_exten)))

host, port = "", 5021
server = xmlrpclib.ServerProxy('http://%s:%d' % (host, port), allow_none=True)

app = wx.App(redirect=True)
top = Frame('XML-RCP Server Client', server)
top.Show()
app.MainLoop()