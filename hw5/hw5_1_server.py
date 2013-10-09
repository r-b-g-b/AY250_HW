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
			'tile' : replicates the image (m: vertical copies, n: horizontal copies)
			'trip' : randomly permute the color channel for each pixel
			'swap_RG' : swap the red and green color channels
			'swap_RB' : swap the red and blue color channels
			'swap_GB' : swap the green and blue color channels


	'''

	def __init__(self):

		self.serverbasedir = os.getcwd()

	def mess(self, imglist, imgshape, imgpath, method, **kwargs):

		img = Image.fromarray(array(imglist).astype(uint8).reshape(imgshape))
		img2 = img.copy()

		if method=='flip':
		# Flips the image over its horizontal (0) or vertical (1) axis
			if axis==0:
				img2 = img2.transpose(Image.FLIP_LEFT_RIGHT)
			elif axis==1:
				img2 = img2.transpose(Image.FLIP_TOP_BOTTOM)

		if method=='tile':
			pass

		if method=='trip':
			
			ncols, nrows = img.shape
			for i in range(ncols):
				for j in range(nrows):
					img2[i, j, :] = img[i, j, permutation(np.arange(3))]

		if method=='swap_RG':
			img2[:, :, 0] = img[:, :, 1]
			img2[:, :, 1] = img[:, :, 0]

		if method=='swap_RB':
			img2[:, :, 0] = img[:, :, 2]
			img2[:, :, 2] = img[:, :, 0]

		if method=='swap_GB':
			img2[:, :, 1] = img[:, :, 2]
			img2[:, :, 2] = img[:, :, 1]

		outpath, outpath2, suffix = self._saveImages(img, img2, imgpath, method)

		imgshape2 = list(img2.size)
		imgshape2.extend([len(img2.getbands())])
		return array(img2).flatten().tolist(), imgshape2, suffix

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

	def _saveImages(self, img, img2, imgpath, modtype):
		'''
		Given the original and modified images (type PIL Images)
		this function will built appropriate filepaths and save the
		images
		'''

		imgpath_base, imgpath_exten = os.path.splitext(imgpath)
		imgpath_serv_base = imgpath_base+'_server_original_'
		imgpath_serv_base2 = imgpath_base+'_server_%s_' % modtype

		imgpath_serv, suffix = self._get_next_filepath(prefix=imgpath_serv_base, exten=imgpath_exten)
		imgpath_serv2, suffix = self._get_next_filepath(prefix=imgpath_serv_base2, exten=imgpath_exten)

		img.save(os.path.join(self.serverbasedir, imgpath_serv))
		img2.save(os.path.join(self.serverbasedir, imgpath_serv2))

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
