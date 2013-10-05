import wx
import xmlrpclib
import Image
import os
from glob import glob

host, port = "", 5021
server = xmlrpclib.ServerProxy('http://%s:%d' % (host, port))


class Frame(wx.Frame):
	
	def __init__(self, title, server):

		wx.Frame.__init__(self, None, title=title, size=(350, 300))
		
		self.server = server
		self.methods = server.available_methods()
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
		method_list = wx.ListCtrl(panel, label='Choose method')
		method_list.InsertColumn(0, 'Method')
		for i, method in enumerate(self.methods):
			method_list.InsertStringItem(i, method)
		box.Add(method_list, 0, wx.ALL, 10)

		method_button = wx.Button(panel, label='Apply method to image')
		method_button.Bind(EVT_BUTTON, self.OnRun)

		box.Add(m_method, 0, wx.ALL, 10)

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

	def OnRun(self, event):
		pass


app = wx.App(redirect=True)
top = Frame('XML-RCP Server Client', server)
top.Show()
app.MainLoop()