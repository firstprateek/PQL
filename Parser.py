import re

class Parser:
	COMMANDS = [
		'use', 
 	]

 	# 'show', 'create', 'select', 'insert', 'update', 
 	# 	'delete', 'commit', 'drop'

	def replace_white_space(self, sentence, replace_str):
		pattern = re.compile(r'\s+')
		sentence = re.sub(pattern, replace_str, sentence)
		return sentence	

	def sanitize_query_parts(self, query):
			query_parts = re.split(r"""("[^"]*"|'[^']*')""", query)
			query_parts[::2] = map(lambda s: self.replace_white_space(s.lower(), "$!~^%"), query_parts[::2]) # outside quotes
			return "".join(query_parts).split("$!~^%")
	


	def use_command(self, query_parts):
		return [{
			"command": query_parts[0],
			"entity": query_parts[1]
		}]

	def build_command(self, query_parts):
		command = query_parts[0]
		if command not in Parser.COMMANDS:
			# throw error
			return {}
		
		return getattr(self, "{}_command".format(command))(query_parts)



	def build_command_list(self):
		query_list = list(map(lambda x: x.strip(), re.split(''';(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', self._input_string)))		
		
		command_list = []
		for query in query_list:
			query_parts = self.sanitize_query_parts(query)
			print(query_parts)
			command_list += self.build_command(query_parts)

		return command_list

	def __init__(self, input):
		self._input_string = input.strip()

# ['use', 'foo']
# ['create', 'table', 'test', '(id', 'int,', 'name', 'string)']
# ['show', 'tables']
# ['insert', 'into', 'test', 'values', '(1,', "'jon   ;;/n/n/r/r asdsad ')"]
# ['select', 'name,', 'id', 'from', 'test']
# ['commit']
# ['']

# {
# 	"command": "use",
# 	"entity": "<db_name>"
# }

# {
# 	"command": "create",
# 	"entity": "<table_name>",
# 	"values": {
# 		"id": "int",
# 		"name": "string"
# 	}
# }

# {
# 	"command": "commit"
# }

# {
# 	"command": "show",
# 	"entity": "<table_name>"
# }

# {
# 	"command": "insert",
# 	"entity": "<table_name>",
# 	"values": [1, 'jon']
# }

# {
# 	"command": "select",
# 	"entity": "<table_name>",
# 	"values"
# }


