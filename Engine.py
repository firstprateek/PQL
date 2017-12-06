#!/usr/bin/python3.5

import sys
from Parser import Parser
from Database import Database

input_string = "".join(sys.stdin.readlines())
pql_parser = Parser(input_string)
query_list = pql_parser.build_query_list()

print("")
print(" ---------------- RESULT ---------------")
print("")
print(query_list)
print("")
print(" ---------------- RESULT ---------------")
print("")

pql_database = Database(query_list)
