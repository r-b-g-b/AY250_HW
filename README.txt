Takes some query as input and attempts to get an answer. For simple queries (arithmetic, simple Python statements), this code uses Python's "eval" statement to get an answer. More complex queries are sent to WolframAlpha for evaluation. The result is printed as formatted text. If WolframAlpha is unable to find an answer, the user is given a choice of possible alternative questions to resubmit.

Input
	query: a string with some question you'd like answered
Output
	result: multiple possibilities. For simple Python evaluation, the actual value is returned. For WolframAlpha queries, the XML DOM tree is returned. For unsuccessful attempts, None is returned.
		