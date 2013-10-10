from SimpleXMLRPCServer import SimpleXMLRPCServer
from numpy import array, uint8
from numpy.random import permutation
import Image
import os
from glob import glob

class messWithImage:
	'''
	A class containing image manipulation functions.
	Set the method parameter to determine which manipulation is performed.

	Input:

		img : the image array
		imgpath : relative filepath for the original image

		method:
			'flip' : flips the image vertically (axis=0) or horizontally (axis=1)
			'trip' : randomly permute the color channel for each pixel
			'swap_RG' : swap the red and green color channels
			'swap_RB' : swap the red and blue color channels
			'swap_GB' : swap the green and blue color channels
			'square' : square each value in the image array
	'''

	def __init__(self):

		self.serverbasedir = os.path.join(os.getcwd(), 'server')
		if not os.path.exists(self.serverbasedir):
			os.mkdir(self.serverbasedir)

		self.require_RGB = ['swap_RG', 'swap_RB', 'swap_GB', 'trip']

	def vflip(self):
		'''
		Flips the image on its vertical axis
		'''
		self.img2 = self.img2.transpose(Image.FLIP_LEFT_RIGHT)

	def hflip(self):
		'''
		Flips the image on its horizontal axis
		'''
		self.img2 = self.img2.transpose(Image.FLIP_TOP_BOTTOM)

	def trip(self):
		'''
		Randomly permutes the color channel for each pixel
		'''
		imgarr = array(self.img)
		imgarr2 = imgarr.copy()
		ncols, nrows = imgarr.shape[:2]
		print imgarr.shape
		for i in range(ncols):
			for j in range(nrows):
				imgarr2[i, j, :] = imgarr[i, j, permutation(range(3))]

		self.img2 = Image.fromarray(imgarr2)

	def square(self):
		'''
		Squares each value in the image array
		'''
		imgarr = array(self.img)
		imgarr2 = (imgarr**2.)
		imgarr2 = uint8(255. * (imgarr2 / imgarr2.max()))
		self.img2 = Image.fromarray(imgarr2)

	def swap_RG(self):
		'''
		Swaps the red and green color channels
		'''
		imgarr = array(self.img)
		imgarr2 = imgarr.copy()
		imgarr2[:, :, 0] = imgarr[:, :, 1]
		imgarr2[:, :, 1] = imgarr[:, :, 0]
		self.img2 = Image.fromarray(imgarr2)

	def swap_RB(self):
		'''
		Swaps the red and blue color channels
		'''
		imgarr = array(self.img)
		imgarr2 = imgarr.copy()
		imgarr2[:, :, 0] = imgarr[:, :, 2]
		imgarr2[:, :, 2] = imgarr[:, :, 0]
		self.img2 = Image.fromarray(imgarr2)

	def swap_GB(self):
		'''
		Swaps the green and blue color channels
		'''
		imgarr = array(self.img)
		imgarr2 = imgarr.copy()
		imgarr2[:, :, 1] = imgarr[:, :, 2]
		imgarr2[:, :, 2] = imgarr[:, :, 1]
		self.img2 = Image.fromarray(imgarr2)

	def mess(self, imglist, imgshape, imgpath, method):
		'''
		'''
		print 'Applying %s' % method
		self.imglist = imglist 
		self.imgshape = [imgshape[1], imgshape[0], imgshape[2]] # no f-ing idea why you need to do this
		self.imgpath = os.path.split(imgpath)[1] # take just the relative path
		self.img = Image.fromarray(array(imglist).astype(uint8).reshape(self.imgshape, order='C'))
		self.img2 = self.img.copy()
		self.method = method

		if (method in self.require_RGB) and (not len(self.imgshape)==3):
			print 'Image must be RGB format.'
			return [None]*3

		# call the user-selected method
		eval('self.%s()' % method)

		outpath, outpath2, suffix = self._saveImages()

		imgshape2 = list(self.img2.size)[::-1] # no f-ing idea why you need to do this
		imgshape2.extend([len(self.img2.getbands())])
		return array(self.img2).flatten().tolist(), imgshape2, suffix

	def _get_next_filepath(self, prefix='ServerImage_', exten='.png'):
		'''
		Given a file prefix, this function returns an unused filepath
		in the base directory
		'''

		done = False
		suffix = 0
		while not done:
			relpath = '%s%3.3u%s' % (prefix, suffix, exten)
			abspath = os.path.join(self.serverbasedir, relpath)
			if os.path.exists(abspath):
				suffix+=1
			else:
				return relpath, suffix

	def _saveImages(self):
		'''
		Given the original and modified images (type PIL Images)
		this function will built appropriate filepaths and save the
		images
		'''

		imgpath_base, imgpath_exten = os.path.splitext(self.imgpath)
		imgpath_serv_base = imgpath_base+'_server_%s_original_' % self.method
		imgpath_serv_base2 = imgpath_base+'_server_%s_' % self.method

		imgpath_serv, suffix = self._get_next_filepath(prefix=imgpath_serv_base, exten=imgpath_exten)
		imgpath_serv2, suffix = self._get_next_filepath(prefix=imgpath_serv_base2, exten=imgpath_exten)

		self.img.save(os.path.join(self.serverbasedir, imgpath_serv))
		self.img2.save(os.path.join(self.serverbasedir, imgpath_serv2))

		return imgpath_serv, imgpath_serv2, suffix


host, port = "", 5021
server = SimpleXMLRPCServer((host, port), allow_none=True)
server.register_instance(messWithImage())
server.register_multicall_functions()
server.register_introspection_functions()

print "Server starting at: ", host, port

try:
	server.serve_forever()
except:
	server.server_close()
