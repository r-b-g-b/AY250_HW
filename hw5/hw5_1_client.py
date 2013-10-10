import xmlrpclib
from scipy.ndimage import imread
import os
from glob import glob
import Image
from numpy import array, uint8

class Client(object):

	def __init__(self, server):

		self.clientbasedir = os.path.join(os.getcwd(), 'client')
		if not os.path.exists(self.clientbasedir):
			os.mkdir(self.clientbasedir)

		self.server = server

		self.imgformats = ['.bmp', '.gif', '.png', '.tif', '.tiff']
		self.methods = server.system.listMethods()
		self.methods = [m for m in self.methods if (not m.startswith('_')) and (not m.startswith('system.')) and (not m=='mess')]

	def mess(self):

		print 'Available methods...'
		self.method = self._get_user_input(self.methods, prompt='Select method: ')

		print 'Images...'
		self.imgfpaths = []
		for imgformat in self.imgformats: 
			self.imgfpaths.extend(glob(os.path.join(self.clientbasedir, '*%s' % imgformat)))
		if len(self.imgfpaths)==0:
			print 'No images found!'
			return

		options = self.imgfpaths
		options.extend(['Help'])
		self.imgpath = self._get_user_input(self.imgfpaths, prompt='Select image: ')
		if self.imgpath=='Help':
			print 'Documentation for %s:' % self.method
			print '\t%s\n' % self.server.system.methodHelp(self.method)
			return

		# get rid of alpha channel if it exists
		img = Image.open(self.imgpath)
		imgarr = array(img)
		if imgarr.shape[-1]>3:
			print 'Removing alpha channel'
			imgarr = imgarr[..., :3]
			img = Image.fromarray(imgarr)
		self.img = img

		self.imgshape = list(self.img.size)
		self.imgshape.extend([len(self.img.getbands())])
		self.imglist = array(self.img).flatten(order='C').tolist()

		# evaluate command on server
		imglist2, imgshape2, suffix = eval('self.server.mess(self.imglist, self.imgshape, self.imgpath, "%s")' % self.method)
		if imglist2 is None:
			print 'Image manipulation failed.'
			return


		self.img2 = Image.fromarray(array(imglist2).astype(uint8).reshape(imgshape2, order='C'))
		
		# save images
		img_base, img_exten = os.path.splitext(self.imgpath)
		self.img.save(os.path.join('%s_client_%s_original_%3.3u%s' % (img_base, self.method, suffix, img_exten)))
		self.img2.save(os.path.join('%s_client_%s_%3.3u%s' % (img_base, self.method, suffix, img_exten)))

	@staticmethod
	def _listify(x):

		xlist = []
		if x.shape==3:
			for i in range(3):
				xlist.extend(x[..., i].flatten(order='C'))
		elif x.shape==2:
			xlist.flatten(order='C')

		return xlist

	@staticmethod
	def _get_user_input(alist, prompt='Select: '):

		for i, a in enumerate(alist):
			print '%u. %s' % (i+1, a)
					# is it a number?
		print
		print '\n'
		done = False
		while not done:
			user_input = raw_input(prompt)
			try:
				ix = int(user_input)
			except:
				print 'Please enter a number.'

			# is it a valid number?
			try:
				selection = alist[ix-1]
				done = True
			except:
				print 'Please enter a valid number.'

		return selection

host, port = "", 5021
server = xmlrpclib.ServerProxy('http://%s:%d' % (host, port), allow_none=True)

client = Client(server)
client.mess()
option = ''
while 1:
	options = ['Another', 'Quit']
	option = client._get_user_input(options, prompt='Select option: ')
	if option=='Quit':
		break
	client.mess()


