#!/usr/bin python
import argparse
import urllib2
from xml.etree import ElementTree as ET
import re

def calculate(query="2*3"):

	result = eval(query)
	print 'Result: '
	print result

def calculate_wolframalpha(query="What is my IP address?"):

	appid = 'RQJA68-P6P3A5U75W'
	url = 'http://api.wolframalpha.com/v2/query?input=%s&appid=%s' % (query, appid)
	url = re.sub(' ', '+', url)
	contents = urllib2.urlopen(url).read()
	tree = ET.fromstring(contents)
	
	print 'WolframAlpha result:'
	for pod in tree.iter('pod'):
		print pod.attrib['title']
		for elem in pod.iter('plaintext'):
			text = elem.text
			if text is not None:
				text = re.sub('\n', '\n\t', text)
				print '\t'+text

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description='Simple statement evaluator')
	
	argparser.add_argument('query', help='The query you wish to evaluate')
	argparser.add_argument('-w', action='store_true', dest='use_wolframalpha', default=False)

	args = argparser.parse_args()

	if args.use_wolframalpha:
		calculate_wolframalpha(args.query)
	else:
		calculate(args.query)