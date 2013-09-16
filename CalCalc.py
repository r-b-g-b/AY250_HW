#!/usr/bin python
import argparse
from urllib2 import urlopen
from xml.etree import ElementTree as ET
from xml.dom import minidom
from re import sub

def calculate(query="2*3"):

	try:
		result = eval(query)
		print 'Result:'
	except SyntaxError:
		result = calculate_wolframalpha(query)
		print 'Result (using WolframAlpha):'
	print result

def calculate_wolframalpha(query="What is my IP address?"):

	appid = 'RQJA68-P6P3A5U75W'
	url = 'http://api.wolframalpha.com/v2/query?input=%s&appid=%s' % (query, appid)
	url = sub(' ', '+', url)
	contents = urlopen(url).read()
	#tree = ET.fromstring(contents)
	domtree = minidom.parseString(contents)
	print domtree.toprettyxml()

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description='Simple statement evaluator')
	
	argparser.add_argument('query', help='The query you wish to evaluate')
	argparser.add_argument('-w', action='store_true', dest='use_wolframalpha', default=False, help='Force program to evaluate using WolframAlpha')

	args = argparser.parse_args()

	if args.use_wolframalpha:
		calculate_wolframalpha(args.query)
	else:
		calculate(args.query)