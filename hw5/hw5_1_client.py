import xmlrpclib
import Image
import os
from glob import glob

host, port = "", 5021
server = xmlrpclib.ServerProxy('http://%s:%d' % (host, port))

clientbasepath = os.getcwd()

# get user's method selection
available_methods = server.system.listMethods()
nmethods = len(available_methods)
print 'Available methods from server:'
for i, method in enumerate(available_methods):
	print '\t%u. %s' % (i+1, method)

while True:
	try:
		meth_ix = int(raw_input('Select method--> '))
		if meth_ix>nmethods:
			print 'There is no method #%u. Please enter a number between 1 and %u.' % (meth_ix, nmethods)
		else: break
	except ValueError:
		print 'Please enter a valid number.'


# make a list of available images in this directory
imgextens = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp']
imgpaths = []
for imgexten in imgextens:
	imgpaths.extend(glob(os.path.join(clientbasepath, '*.%s' % imgexten)))

print 'Images in %s' % clientbasepath

# print available image paths
for i, imgpath in enumerate(imgpaths):
	print '\t%u. %s' % (i+1, os.path.split(imgpath)[1])

# get user's image selection
while True:
	try:
		img_ix = int(raw_input('Select image--> '))
		if img_ix>len(imgpaths):
			print 'There is no image #%u. Please enter a number between 1 and %u.' % (img_ix, len(imgpaths))
		else: break
	except ValueError:
		print 'Please enter a valid number.'

# load the selected image
imgpath = imgpaths[i-1]
img = Image.open(imgpath)


eval('server.%s(img)' % available_methods[meth_ix-1])

