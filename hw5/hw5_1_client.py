import xmlrpclib
import PIL
import os
from glob import glob

host, port = "", 5021
server = xmlrpclib.ServerProxy('http://%s:%d' % (host, port))
available_methods = server.system.listMethods()

clientbasepath = os.getcwd()

imgextens = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp']
imgpaths = []
for imgexten in imgextens:
	imgpaths.extend(glob(os.path.join(clientbasepath, '*.%s' % imgexten)))

print 'Images in %s' % clientbasepath

for i, imgpath in enumerate(imgpaths):
	print '\t%u. %s' % (i+1, os.path.split(imgpath)[1])

done = False
while not done:
	try:
		img_ix = int(raw_input('Select image--> '))
		if img_ix>len(imgpaths):
			print 'There is no image #%u. Please enter a number between 1 and %u.' % (img_ix, len(imgpaths))
		else:
			break
	except ValueError:
		print 'Please enter a valid number'

imgpath = imgpaths[i-1]
img = Image.open(imgpath)

print 'Available methods from server:'
for i, method in enumerate(available_methods):
	print '\t%u. %s' % (i+1, method)
meth_ix = raw_input('Select method--> ')

result = 


