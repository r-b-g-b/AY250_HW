from SimpleXMLRPCServer import SimpleXMLRPCServer
import PIL
import os
from glob import glob

class messWithImage:

	def __init__(self):

		self.serverbasedir = os.getcwd()

	def tile(self, img, imgpath=None, nx=4, ny=4):

		print 'Image has been tiled!'
		img2 = img.copy()

		outpath, outpath2 = saveImages(img, img2)

		return img2

	def flip(self, img, axis=0):
		'''
		Flips the image over its horizontal (0) or vertical (1) axis
		Input:
			img : the image array
			imgpath : relative filepath for the original image
		'''
		img2 = img.copy()

		if axis==0:
			img2 = img2.transpose(Image.FLIP_LEFT_RIGHT)
		elif axis==1:
			img2 = img2.transpose(Image.FLIP_TOP_BOTTOM)

		outpath, outpath2 = saveImages(img, img2)

		return img2

	def get_next_filepath(prefix='ServerImage_', exten='.png'):
		'''
		Given a file prefix, this function returns an unused filepath
		in the base directory
		'''

		done = False
		i = 0
		while not done:
			relpath = '%s%3.3u%s' % (prefix, i, exten)
			abspath = os.path.join(self.serverbasedir, relpath)
			if os.path.exists(abspath):
				i+=1
			else:
				return relpath

	def saveImages(img, img2):
		'''
		Given the original and modified images (type PIL Images)
		this function will built appropriate filepaths and save the
		images
		'''

		imgpath_base, imgpath_exten = os.path.splitext(img.filename)
		imgpath_serv_base = imgpath_base+'_server_original_'
		imgpath_serv_base2 = imgpath_base+'_server_flipped_'

		imgpath_serv = get_next_filepath(prefix=imgpath_serv_base, exten=imgpath_exten)
		imgpath_serv2 = get_next_filepath(prefix=imgpath_serv_base2, exten=imgpath_exten)

		img.save(os.path.join(self.serverbasedir, imgpath_serv))
		img2.save(os.path.join(self.serverbasedir, imgpath_serv2))

		return imgpath_serv, imgpath_serv2




host, port = "", 5021
server = SimpleXMLRPCServer((host, port), allow_none=True)
server.register_instance(messWithImage())
server.register_multicall_functions()
server.register_introspection_functions()

print "Server starting at: ", host, port

server.serve_forever()
