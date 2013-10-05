from SimpleXMLRPCServer import SimpleXMLRPCServer
import PIL
import os
from glob import glob

basepath = os.getcwd()

class messWithImage:
	def tile(self, img, imgpath=None, nx=4, ny=4):

		print 'Image has been tiled!'
		img2 = img.copy()

		if imgpath is None:
			imgpath = get_next_filepath(basepath, 'ServerFlipImage_')
		img2.save(imgpath)
	
		return img2

	def flip(self, img, imgpath=None, axis=0):
		'''
		Flips the image over its horizontal (0) or vertical (1) axis
		'''
		img2 = img.copy()

		if axis==0:
			img2 = img2[::-1, :, ...]
		elif axis==1:
			img2 = img2[:, ::-1, ...]

		if imgpath is None:
			imgpath = get_next_filepath(basepath, 'ServerFlipImage_')
		img2.save(imgpath)

		return img2

	def get_next_filepath(direc, prefix='ServerImage_', exten='.png'):
		
		done = False
		i = 0
		while not done:
			relpath = '%s_%3.3u.%s' % (prefix, i, exten)
			abspath = os.path.join(direct, relpath)
			if os.path.exists(abspath)
				i+=1
			else:
				return abspath






host, port = "", 5021
server = SimpleXMLRPCServer((host, port), allow_none=True)
server.register_instance(messWithImage())
server.register_multicall_functions()
server.register_introspection_functions()

print "Server starting at: ", host port