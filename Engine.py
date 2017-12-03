import sys
from Parser import Parser

input_string = "".join(sys.stdin.readlines())
pql_parser = Parser(input_string)
commands_list = pql_parser.build_command_list()
print commands_list