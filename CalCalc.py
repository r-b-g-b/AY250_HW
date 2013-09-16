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
		result = calculateWolframalpha(query)
		print 'Result (using WolframAlpha):'
	print result

def calculateWolframalpha(query="What is my IP address?"):

	appid = 'RQJA68-P6P3A5U75W'
	url = 'http://api.wolframalpha.com/v2/query?input=%s&appid=%s' % (query, appid)
	url = sub(' ', '+', url)
	contents = urlopen(url).read()
	#tree = ET.fromstring(contents)
	domtree = minidom.parseString(contents)

	success = checkQueryResult(domtree)
	if success:
		printSuccessfulQuery(domtree)
	else:
		printDidYouMeans(domtree)


def checkQueryResult(domtree):

	queryresult = domtree.getElementsByTagName('queryresult')[0]
	success = queryresult.getAttribute('success')=='true'
	if success:
		didyoumeans = domtree.getElementsByTagName('didyoumeans')
		if len(didyoumeans)>0:
			print 'WolframAlpha had some trouble parsing your response.\
			\nDid you mean:'
			for didyoumean in didyoumeans:
				pass
	return success

def printSuccessfulQuery(domtree):
	
	print 'WolframAlpha result:'

	for pod in domtree.getElementsByTagName('pod'):
		print pod.getAttribute('title')
		for elem in pod.getElementsByTagName('plaintext'):
			text = elem.childNodes[0].data
			if text is not None:
				text = re.sub('\n', '\n\t', text)
				print '\t'+text

def printDidYouMeans():
	pass

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description='Simple statement evaluator')
	
	argparser.add_argument('query', help='The query you wish to evaluate')
	argparser.add_argument('-w', action='store_true', dest='use_wolframalpha', default=False, help='Force program to evaluate using WolframAlpha')

	args = argparser.parse_args()

	if args.use_wolframalpha:
		calculateWolframalpha(args.query)
	else:
		calculate(args.query)