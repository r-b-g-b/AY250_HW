#!/usr/bin python
import argparse
from urllib2 import urlopen
from urllib import quote_plus
from xml.dom import minidom

def calculate(query="2*3", use_wolframalpha=False):

	if use_wolframalpha:
		result = calculateWolframalpha(query)

	else:
		try:
			result = eval(query)
			print 'Result:\n'+'-'*20
			print str(result)+'\n'

		except:
			print 'Python evaluator could not parse your query.\nSending query to WolframAlpha...'
			result = calculateWolframalpha(query)

	return result


def calculateWolframalpha(query="What is my IP address?"):

	appid = 'RQJA68-P6P3A5U75W'
	query = quote_plus(query)
	url = 'http://api.wolframalpha.com/v2/query?input=%s&appid=%s' % (query, appid)
	contents = urlopen(url).read()
	domtree = minidom.parseString(contents)

	success = checkQueryResult(domtree)
	if success:
		result = printSuccessfulQuery(domtree)
	else:
		result = printDidYouMeans(domtree)

	return result


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

	return domtree

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
		pass
	else:
		print '\n'
		calculate(query=new_queries[int(user_selection)-1])

	return None

def test_math():
	query = '2**4.-16'
	result = calculate(query)
	assert result<0.0001

def test_string():
	query = "'ham'+'burger'"
	result = calculate(query)
	assert result=='hamburger'

def test_list():
	query = "[1, 2, 3, 4]"
	result = calculate(query)
	assert len(result)==4

def test_dict():
	query = "{'mamasemamasa': 'mamacoosa'}"
	result = calculate(query)
	assert result['mamasemamasa']=='mamacoosa'

def test_wolfram():
	query = 'What is the capitol of France?'
	result = calculate(query)
	assert result.__module__=='xml.dom.minidom'

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description='Simple statement evaluator')
	
	argparser.add_argument('-s', action='store', dest='query', help='The query you wish to evaluate')
	argparser.add_argument('-w', action='store_true', dest='use_wolframalpha', default=False, help='Force program to evaluate using WolframAlpha')

	args = argparser.parse_args()

	if args.use_wolframalpha:
		calculateWolframalpha(args.query, args.use_wolframalpha)
	else:
		calculate(args.query)