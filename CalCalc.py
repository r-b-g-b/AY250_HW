#!/usr/bin python
import argparse

def calculate(query="2*3"):

	result = eval(query)
	print 'Result: '
	print result


def calculate_wolframalpha(query="What is my IP address?"):

	print 'WolframAlpha result:'
	print 'temp'
	

if __name__ == '__main__':

	argparser = argparse.ArgumentParser(description='Simple statement evaluator')
	
	argparser.add_argument('query', help='The query you wish to evaluate')
	argparser.add_argument('-w', action='store_true', dest='use_wolframalpha', default=False)

	args = argparser.parse_args()

	if use_wolframalpha:
		calculate_wolframalpha(args.query)
	else:
		calculate(args.query)