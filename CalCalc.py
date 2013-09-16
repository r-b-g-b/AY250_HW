#!/usr/bin python
import argparse
from urllib2 import urlopen
from urllib import quote_plus
from xml.dom import minidom

def calculate(query="2*3"):

	try:
		result = eval(query)
		print 'Result:\n'+'-'*20
		print result+'\n'

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
	
	print 'WolframAlpha result:\n'+'-'*20

	for pod in domtree.getElementsByTagName('pod'):
		for elem in pod.getElementsByTagName('plaintext')[0].childNodes:
			print pod.getAttribute('title')
			text = elem.data
			if text is not None:
				text = text.replace('\n', '\n\t')
				print '\t'+text+'\n'

def printDidYouMeans(domtree):

	print 'WolframAlpha had some trouble parsing your response.\n\nDid you mean:'

	didyoumeans = domtree.getElementsByTagName('didyoumeans')[0]

	new_queries = []
	for i, didyoumean in enumerate(didyoumeans.getElementsByTagName('didyoumean')):
		dym_text = didyoumean.childNodes[0].data
		print '\t%u. %s' % (i+1, dym_text)
		new_queries.append(dym_text)
	print '\t(q) Quit\n'

	# Get user selection, make sure it is allowed
	allowed_inputs = [str(i) for i in range(1, len(new_queries)+1)]
	allowed_inputs.append('q')
	valid_input = False
	while not valid_input:
		user_selection = raw_input('Select your response: ').lower()
		if user_selection in allowed_inputs:
			valid_input = True
		else:
			print 'Invalid selection. Please choose from (%s)\n.' % ', '.join(allowed_inputs)

	if user_selection=='q':
		valid_input = True
	else:
		print '\n'
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