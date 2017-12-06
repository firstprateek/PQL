import sys
from Parser import Parser

input_string = "".join(sys.stdin.readlines())
pql_parser = Parser(input_string)
query_list = pql_parser.build_query_list()

print
print " ---------------- RESULT ---------------"
print
print query_list
print
print " ---------------- RESULT ---------------"
print