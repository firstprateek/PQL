import re

class Parser:
	COMMANDS = [
		'use', 'show', 'create', 'select', 'insert',
		'delete', 'commit', 'drop'
 	]

 	# 'show', 'create', 'select', 'insert', 'update', 
 	# 	'delete', 'commit', 'drop'
 	# pattern = re.compile(r'[\s]*\s+[\s]*')

 	def sanitize_commas(self, query):
 		pattern = re.compile(r'[\s]*,[\s]*(?=[^()]*)')
 		query = re.sub(pattern, ', ', query)
 		return query

	def replace_white_space(self, sentence, replace_str):
		pattern = re.compile(r'\s+')
		sentence = re.sub(pattern, replace_str, sentence)
		return sentence	

	def build_query_parts(self, query):
			query_parts = re.split(r"""("[^"]*"|'[^']*')""", query)
			query_parts[::2] = map(lambda s: self.replace_white_space(s.lower(), "$!~^%"), query_parts[::2]) # outside quotes
			return "".join(query_parts).split("$!~^%")
	

			#checks for table name being alpha numeric etc
			# after building a command run it thorugh
			# entity check and column_name column_type check
	def use_command(self, query_parts):
		return [{
			"command": query_parts[0],
			"entity": query_parts[1]
		}]

	def create_command(self, query_parts):
		command = { "command": query_parts[0] }

		if query_parts[1] is not 'table':
			# error incorrect syntax
			command["entity"] = query_parts[1]
			return [command]

		command['entity'] = query_parts[2]
		command['values'] = []
		if query_parts[3][0] is not '(':
			# error incorrect syntax
			return [{}]
		
		command['values'] += { 
			'column_name': query_parts[3][1::],
			'column_type': re.sub(",", '', query_parts[4])
		}

		counter = 5;
		while (query_parts[counter] < len(query_parts)):
			value = { 
			'column_name': query_parts[counter], 
			'column_type': re.sub(",", '', query_parts[counter + 1])
			}

			if query_parts[counter + 1][-1] is ')':
				value['column_type'] = value['column_type'][:-1]
				command['values'] += value
				break;

			command['values'] += value
			counter += 2

		return [command]

	def show_command(self, query_parts):
		return [{
			'command': query_parts[0],
			'entity': query_parts[1]
		}]

	def insert_command(self, query_parts):
		command = { "command": query_parts[0] }

		if query_parts[1] is not 'into':
			# error incorrect syntax
			command["into"] = query_parts[1]
			return [command]

		command['entity'] = query_parts[2]

		if query_parts[3] is not 'values':
			# error incorrect syntax
			return [{}]
		
		command['values'] = []
		
		if query_parts[4][0] is not '(':
			# error incorrect syntax
			return [{}]

		counter = 5;
		while (query_parts[counter] < len(query_parts)):
			command['values'] += re.sub(",", '', query_parts[counter])
			
			if query_parts[counter + 1][-1] is ')':
				command['values'] += re.sub(",", '', query_parts[counter + 1])
				break;

			counter += 1

		return [command]


	# "select from from from;"
	# - second last has to be from
	# - last has to be table_name

	# - create list of columns from 2 to 3rd last and keep adding
	# 	- also keep removing commas

	def select_command(self, query_parts):
		command = { "command": query_parts[0] }

		if query_parts[-2] is not 'from':
			# throw syntax error
			return {}

		command["entity"] = query_parts[-1]

		command["column_list"] = map(lambda x: re.sub(",", '', x), query_parts[1:-2])

		return [command]

	def commit_command(self, query_parts):
		return [{
			"command": query_parts[0]
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
			query_parts = self.build_query_parts(self.sanitize_commas(query))
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

# {
# 	"command": "create",
# 	"entity": "test",
# 	"values": [ {"column_name": "id", "column_type": "int"}, {} ]
# }

# {
# 	"command": "select",
# 	"entity": "test",
# 	"values": [ 'id', 'name' ],
# 	"condition": "where",
# 	"argumnet": "id>3"
# }

# {
# 	"command": "use",
# 	"entity": 'foo'
# }

