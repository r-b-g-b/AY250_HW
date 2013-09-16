#!/usr/bin python
import argparse
from urllib2 import urlopen
from urllib import quote_plus
from xml.dom import minidom

def calculate(query="2*3"):

	try:
		result = eval(query)
		print 'Result:'
		print result

	except SyntaxError:
		result = calculateWolframalpha(query)

def calculateWolframalpha(query="What is my IP address?"):

	appid = 'RQJA68-P6P3A5U75W'
	query = quote_plus(query)
	url = 'http://api.wolframalpha.com/v2/query?input=%s&appid=%s' % (query, appid)
	contents = urlopen(url).read()
	domtree = minidom.parseString(contents)

	success = checkQueryResult(domtree)
	if success:
		printSuccessfulQuery(domtree)
	else:
		printDidYouMeans(domtree)


def checkQueryResult(domtree):

	queryresult = domtree.getElementsByTagName('queryresult')[0]
	return queryresult.getAttribute('success')=='true'

def printSuccessfulQuery(domtree):
	
	print 'WolframAlpha result:'

	for pod in domtree.getElementsByTagName('pod'):
		print pod.getAttribute('title')
		for elem in pod.getElementsByTagName('plaintext'):
			text = elem.childNodes[0].data
			if text is not None:
				text = text.replace('\n', '\n\t')
				print '\t'+text

def printDidYouMeans(domtree):

	print 'WolframAlpha had some trouble parsing your response.\
	\nDid you mean:'

	didyoumeans = domtree.getElementsByTagName('didyoumeans')[0]

	new_queries = []
	for i, didyoumean in enumerate(didyoumeans.getElementsByTagName('didyoumean')):
		dym_text = didyoumean.childNodes[0].data
		print '\t%u. %s' % (i+1, dym_text)
		new_queries.append(dym_text)
	print '(q) Quit'

	user_selection = raw_input('Select your response.')
	if user_selection=='Q':
		pass
	else:
		calculate(query=new_queries[int(user_selection)-1])

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description='Simple statement evaluator')
	
	argparser.add_argument('query', help='The query you wish to evaluate')
	argparser.add_argument('-w', action='store_true', dest='use_wolframalpha', default=False, help='Force program to evaluate using WolframAlpha')

	args = argparser.parse_args()

	if args.use_wolframalpha:
		calculateWolframalpha(args.query)
	else:
		calculate(args.query)