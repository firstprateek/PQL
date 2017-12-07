#!/usr/bin/python3.5

import sys
from Parser import Parser
from Database import Database

input_string = "".join(sys.stdin.readlines())
pql_parser = Parser(input_string)
query_list = pql_parser.build_query_list()

for x in query_list:
	if 'error_flag' in x:
		if x['error_flag'] == 'pql_parse_error':
			exit(6)
		if x['error_flag'] == 'no_selected_db':
			exit(5)

print("")
print(" ---------------- RESULT ---------------")
print("")
print(query_list)
print("")
print(" ---------------- RESULT ---------------")
print("")

pql_database = Database(query_list)
