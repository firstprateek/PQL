import re
import pdb

class Parser:
	COMMANDS = [
		'use', 'show', 'create', 'select', 'insert', 'delete', 'commit', 'drop'
 	]

 	COLUMN_TYPES = [ 'int', 'string' ]

 	def sanitize_commas(self, query):
 		pattern = re.compile(r'[\s]*,[\s]*(?=[^()]*)')
 		query = re.sub(pattern, ', ', query)
 		
 		return query

 	def sanitize_paranthesis(self, query):
 		pattern = re.compile(r'(?!\B"[^"]*)\([\s]+(?![^"]*"\B)')
 		query = re.sub(pattern, '(', query)
 		pattern = re.compile(r'(?!\B"[^"]*)[\s]+\)(?![^"]*"\B)')
 		query = re.sub(pattern, ')', query)
 		
 		return query

 	def sanitize_operands(self, query):
 		pattern = re.compile(r'(?!\B"[^"]*)(?<![<!>])[\s]*=[\s]*(?![^"]*"\B)')
 		query = re.sub(pattern, ' = ', query)

 		pattern = re.compile(r'(?!\B"[^"]*)[\s]*<=[\s]*(?![^"]*"\B)')
 		query = re.sub(pattern, ' <= ', query)

 		pattern = re.compile(r'(?!\B"[^"]*)[\s]*>=[\s]*(?![^"]*"\B)')
 		query = re.sub(pattern, ' >= ', query)

 		pattern = re.compile(r'(?!\B"[^"]*)[\s]*!=[\s]*(?![^"]*"\B)')
 		query = re.sub(pattern, ' != ', query)

 		pattern = re.compile(r'(?!\B"[^"]*)[\s]*<>[\s]*(?![^"]*"\B)')
 		query = re.sub(pattern, ' <> ', query)

 		pattern = re.compile(r'(?!\B"[^"]*)(?<!\<)[\s]*>[\s]*(?!\=)(?![^"]*"\B)')
 		query = re.sub(pattern, ' > ', query)


 		pattern = re.compile(r'(?!\B"[^"]*)[\s]*>[\s]*(?![=>])(?![^"]*"\B)')
 		query = re.sub(pattern, ' < ', query)

 		return query

 	def replace_white_space(self, sentence, replace_str):
		pattern = re.compile(r'\s+')
		sentence = re.sub(pattern, replace_str, sentence)
		
		return sentence	

 	def sanitize_white_space(self, query):
		query_parts = re.split(r"""("[^"]*"|'[^']*')""", query)
		query_parts[::2] = map(lambda s: self.replace_white_space(s.lower(), "$!~^%"), query_parts[::2]) # outside quotes
		
		return "".join(query_parts).split("$!~^%")
	
 	def sanitize(self, query):
 		query = self.sanitize_commas(query)
 		query = self.sanitize_paranthesis(query)
 		query = self.sanitize_operands(query)
 		query = self.sanitize_white_space(query)

 		return query
 	# [{'command': 'use', 'entity': 'foo'}]
	def validate(self, query):
		# first make everything lower case
		# already lower case all
		# call this method in each command function
		# if query[entity] == not alpha numeric or starting with number
		# if others same
		print "validate_query"
		print query[0]
		query_hash = query[0]
		if 'entity' not in query_hash:
			return query

		if not query_hash['entity'][0].isalpha() or not query_hash['entity'].isalnum():
			#raise syntax error
			query[0]['error'] = 'Entity name incorrect format. Has to be alphanumeric starting with alphabet'
			return query

		if query[0]['command'] == 'create':
			for x in query_hash['values']:
				if not x['column_name'][0].isalpha() or not x['column_name'].isalnum():
					query[0]['error'] = 'Column_name name incorrect format. Has to be alphanumeric starting with alphabet'
					return query

				if x['column_type'] not in Parser.COLUMN_TYPES:
					query[0]['error'] = 'Column_type incorrect'
					return query


		if query[0]['command'] == 'select':
			for x in query_hash['column_list']:
				if not x[0].isalpha() or not x.isalnum():
					query[0]['error'] = 'Column_name name incorrect format. Has to be alphanumeric starting with alphabet'
					return query

		if query[0]['command'] == 'insert':
			for x in query_hash['column_values']:
				if not x.isalnum():
					query[0]['error'] = 'Column_value incorrect format. Has to be alphanumeric'
					return query


		return query
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
		
		# print query_parts
		print "query_parts"
		print query_parts
		print query_parts[1]
		if query_parts[1] != 'table':
			print "inside here"
			# error incorrect syntax
			command["error"] = '2nd word is not "table" in query'
			return [command]

		command['entity'] = query_parts[2]
		command['values'] = []
		
		if len(query_parts[3::]) & 1:
			# error incorrect syntax
			command["error"] = "Incorrect Syntax for values"
			return [command]

		if query_parts[3][0] != '(':
			# error incorrect syntax
			command["error"] = "opening paranthesis not provided for column_name list"
			return [command]
		
		command['values'] += [{ 
			'column_name': query_parts[3][1::],
			'column_type': re.sub(",", '', query_parts[4])
		}]

		counter = 5
		while counter < len(query_parts):
			# if query_parts[counter]

			value = { 
			'column_name': query_parts[counter], 
			'column_type': re.sub(",", '', query_parts[counter + 1])
			}

			if query_parts[counter + 1][-1] is ')':
				value['column_type'] = value['column_type'][:-1]
				command['values'] += [value]
				break

			command['values'] += [value]
			counter += 2

		return [command]

	def show_command(self, query_parts):
		return [{
			'command': query_parts[0],
			'entity': query_parts[1]
		}]
	# ['insert', 'into', 'test', 'values', '(1,', "'jon   ;;/n/n/r/r asdsad ')"]
	def insert_command(self, query_parts):
		command = { "command": query_parts[0] }

		if query_parts[1] != 'into':
			# error incorrect syntax
			command["error"] = '2nd word is not "into" in query'
			return [command]

		command['entity'] = query_parts[2]

		if query_parts[3] != 'values':
			# error incorrect syntax
			command["error"] = '4th word is not "values" in query'
			return [command]
		
		command['column_values'] = []
		
		if len(query_parts[4::]) & 1:
			# error incorrect syntax
			command["error"] = "Incorrect Syntax for values"
			return [command]

		if query_parts[4][0] != '(':
			# error incorrect syntax
			command["error"] = "opening paranthesis not provided for column_name list"
			return [command]

		counter = 4
		# print
		# print "query parts before"
		# print query_parts
		# print "query parts after"
		# print
		# query_parts[counter] = re.sub("\(", '', query_parts[counter])
		# print query_parts

		while counter < len(query_parts):
			# not if its a string[ a if condition else b
			res = []

			# check if string is of string type
			if query_parts[counter].count('"') > 1 or query_parts[counter].count("'") > 1:
				if query_parts[counter][0] == '(':
					res = [query_parts[counter][1::]]
			else:
				res = re.sub(",", '', query_parts[counter])
				res = [re.sub("\(", '', res)]
	
			
			command['column_values'] +=  res
			
			if query_parts[counter + 1][-1] == ')':	
				res = []
				if query_parts[counter + 1].count('"') > 1 or query_parts[counter + 1].count("'") > 1:
					res = [query_parts[counter + 1][0:-1]]
				else:
					res = [re.sub(",", '', query_parts[counter + 1][0:-1])]

				command['column_values'] += res
				break

			counter += 1

		print
		print "inser query"
		print [command]
		print

		return [command]


	# select name from test where name>='jill' and id = 3;
	# select from id from test where from>='jill' and id = 3;
	def select_command(self, query_parts):
		command = { "command": query_parts[0] }

		where_query = []
		if 'where' in query_parts:
			index = query_parts.index['where']	
			query_parts_1 = query_parts[0:index]
			where_query = query_parts[index::]
			query_parts = query_parts_1

		if query_parts[-2] != 'from':
			# throw syntax error
			command["error"] = "2nd word from end not 'from'"
			return [command]

		command["entity"] = query_parts[-1]

		command["column_list"] = map(lambda x: re.sub(",", '', x), query_parts[1:-2])

		if where_query:
			operations_query = [x for x in where_query[1::] if x != 'and']

			if len(operations_query) % 3:
				# error incorrect syntax
				command["error"] = "Incorrect Syntax for values"
				return [command]

			counter = 1
			command["where"] = []
			while counter < len(where_query):
				command["where"] += [{ 
				'column_name': where_query[counter], 
				'operator': where_query[counter + 1],
				'argumnet': where_query[counter + 2]
				}]

			command["where"] = [where_query[counter + 3]]
			
			counter += 4

		return [command]

	def commit_command(self, query_parts):
		return [{
			"command": query_parts[0]
		}]

	def build_command(self, query_parts):
		print "query_parts in: {}".format(query_parts)
		command = query_parts[0]
		if command not in Parser.COMMANDS:
			# throw error
			print "This command {}".format(command)
			return [{
				"command": query_parts[0], "error": "Incorrect command"
			}]
		
		return getattr(self, "{}_command".format(command))(query_parts)



	def build_command_list(self):
		query_list = list(map(lambda x: x.strip(), re.split(''';(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', self._input_string)))		
		
		command_list = []
		for query in query_list:
			query_parts = self.sanitize(query)
			print "print query parts"
			print query_parts
			print "build_commands"
			print self.build_command(query_parts)
			command_list += self.validate(self.build_command(query_parts))

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

