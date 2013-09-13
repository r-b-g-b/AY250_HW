#!/usr/bin python
import argparse

def calculate(query="2*3"):

	result = eval(query)
	print result

if __name__ == '__main__':
	argparser = argparse.ArgumentParser(description = 'Simple statement evaluator')
	argparser.add_argument('query', help = 'The query you wish to evaluate')
	args = argparser.parse_args()
	calculate(args.query)