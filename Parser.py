import re
import pdb


class Parser:
    COMMANDS = ['use', 'show', 'create', 'select', 'insert', 'delete', 'commit', 'drop', 'update']

    COLUMN_TYPES = ['int', 'string']

    # --------- Query Sanitization Start --------


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

        pattern = re.compile(r'(?!\B"[^"]*)[\s]*<[\s]*(?![=>])(?![^"]*"\B)')
        query = re.sub(pattern, ' < ', query)

        return query

    def replace_white_space(self, sentence, replace_str):
        pattern = re.compile(r'\s+')
        sentence = re.sub(pattern, replace_str, sentence)

        return sentence

    def sanitize_white_space(self, query):
        query_parts = re.split(r"""("[^"]*"|'[^']*')""", query)
        query_parts[::2] = list(
            map(lambda s: self.replace_white_space(s.lower(), "$!~^%"), query_parts[::2]))  # outside quotes

        return "".join(query_parts).split("$!~^%")

    def sanitize(self, query):
        query = self.sanitize_commas(query)
        query = self.sanitize_paranthesis(query)
        query = self.sanitize_operands(query)
        query = self.sanitize_white_space(query)

        return query

    # --------- Query Sanitization Finish --------
    def extract_string(self, test_string):
        if test_string[0] in ['"', "'"] and test_string[-1] in ['"', "'"]:
            return test_string[1:-1]
        else:
            return test_string

    def validate(self, query):
        # print("validate_query")
        # print(query)

        query_hash = query[0]
        if 'entity' not in query_hash:
            return query

        if 'error' in query_hash:
            return query

        if query_hash['entity'] == '':
            query[0]['error_flag'] = 'pql_parse_error'
            query[0]['error'] = 'Entity not selected'
            return query

        if not query_hash['entity'][0].isalpha() or not query_hash['entity'].isalnum():
            query[0]['error_flag'] = 'pql_parse_error'
            query[0]['error'] = 'Entity name incorrect format. Has to be alphanumeric starting with alphabet'
            return query

        if query[0]['command'] == 'create':
            if query_hash['values'] == []:
                query[0]['error_flag'] = 'pql_parse_error'
                query[0]['error'] = 'At least one column is required'
                return query

            for x in query_hash['values']:
                if not x['column_name'][0].isalpha() or not x['column_name'].isalnum():
                    query[0]['error_flag'] = 'pql_parse_error'
                    query[0][
                        'error'] = 'Column_name name incorrect format. Has to be alphanumeric starting with alphabet'
                    return query

                if x['column_type'] not in Parser.COLUMN_TYPES:
                    query[0]['error_flag'] = 'pql_parse_error'
                    query[0]['error'] = 'Column_type incorrect'
                    return query

        if query[0]['command'] == 'delete':
            if 'where' in query_hash:
                for x in query_hash['where']:
                    if isinstance(x, dict):
                        x['argument'] = self.extract_string(x['argument'])

        if query[0]['command'] == 'select':
            if 'where' in query_hash:
                for x in query_hash['where']:
                    if isinstance(x, dict):
                        x['argument'] = self.extract_string(x['argument'])

            for x in query_hash['column_list']:
                if not x[0].isalpha() or not x.isalnum():
                    query[0]['error_flag'] = 'pql_parse_error'
                    query[0][
                        'error'] = 'Column_name name incorrect format. Has to be alphanumeric starting with alphabet'
                    return query

        if query[0]['command'] == 'update':
            for x in query_hash['set']:
                if isinstance(x, dict):
                    x['argument'] = self.extract_string(x['argument'])

            if 'where' in query_hash:
                for x in query_hash['where']:
                    if isinstance(x, dict):
                        x['argument'] = self.extract_string(x['argument'])

        if query[0]['command'] == 'insert':
            query_hash['row_values'] = list(map(lambda x: self.extract_string(x), query_hash['row_values']))

            for x in query_hash['row_values']:
                if not x.isdigit():
                    if not x[0].isalpha() or not x.isalnum():
                        query[0]['error_flag'] = 'pql_parse_error'
                        query[0]['error'] = 'Column_value incorrect format. Has to be alphanumeric'
                        return query

        return query

    # ----- Command Implementation Start -----


    def use_command(self, query_parts):
        self._active_db = query_parts[1]
        error_flag = ''
        if len(query_parts) > 2:
        	error_flag = "pql_parse_error"

        return [{
            "command": query_parts[0],
            "entity": query_parts[1],
            "error": "",
            "error_flag": error_flag
        }]

    def create_command(self, query_parts):
        query_hash = {"command": query_parts[0], "error": ""}

        if query_parts[1] != 'table':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = '2nd word is not "table" in query'
            return [query_hash]

        query_hash['entity'] = query_parts[2]
        query_hash['values'] = []

        if len(query_parts[3::]) & 1:
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = "Syntax error at values."
            return [query_hash]

        if query_parts[3][0] != '(':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = "Opening paranthesis not provided for column_name list"
            return [query_hash]

        column_type = re.sub(",", '', query_parts[4])
        if column_type[-1] == ')':
            column_type = column_type[0:-1]

        query_hash['values'] += [{
            'column_name': query_parts[3][1::],
            'column_type': column_type
        }]

        counter = 5
        while counter < len(query_parts):
            value = {
                'column_name': query_parts[counter],
                'column_type': re.sub(",", '', query_parts[counter + 1])
            }

            if query_parts[counter + 1][-1] == ')':
                value['column_type'] = value['column_type'][:-1]
                query_hash['values'] += [value]
                break

            query_hash['values'] += [value]
            counter += 2

        return [query_hash]

    def show_command(self, query_parts):
        return [{
            'command': query_parts[0],
            'entity': query_parts[1], "error": ""
        }]

    def insert_command(self, query_parts):
        query_hash = {"command": query_parts[0], "error": ""}

        if query_parts[1] != 'into':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = '2nd word is not "into" in query'
            return [query_hash]

        query_hash['entity'] = query_parts[2]

        if query_parts[3] != 'values':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = '4th word is not "values" in query'
            return [query_hash]

        query_hash['row_values'] = []

        if len(query_parts[4::]) < 1:
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = "Atleast 1 value to insert"
            return [query_hash]

        if query_parts[4][0] != '(':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = "Opening paranthesis not provided for row values"
            return [query_hash]

        counter = 4
        while counter < len(query_parts):
            res = []

            # check if string is of string type
            if query_parts[counter].count('"') > 1 or query_parts[counter].count("'") > 1:
                if query_parts[counter][0] == '(':
                    res = [query_parts[counter][1::]]
                elif query_parts[counter][-1] == ')':
                    res = [query_parts[counter][0:-1]]
                else:
                    res = [query_parts[counter]]
            else:
                res = re.sub(",", '', query_parts[counter])
                res = re.sub("\(", '', res)
                res = [re.sub("\)", '', res)]

            query_hash['row_values'] += res

            if query_parts[counter][-1] == ')':
                break;
            # if query_parts[counter + 1][-1] == ')':
            # 	res = []
            # 	if query_parts[counter + 1].count('"') > 1 or query_parts[counter + 1].count("'") > 1:
            # 		res = [query_parts[counter + 1][0:-1]]
            # 	else:
            # 		res = [re.sub(",", '', query_parts[counter + 1][0:-1])]

            # 	query_hash['row_values'] += res
            # 	break

            counter += 1
        return [query_hash]

    def select_command(self, query_parts):
        query_hash = {"command": query_parts[0], "error": ""}

        where_query = []
        if 'where' in query_parts:
            index = query_parts.index('where')
            query_parts_1 = query_parts[0:index]
            where_query = query_parts[index::]
            query_parts = query_parts_1

        if query_parts[-2] != 'from':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = 'Table not mentioned'

            return [query_hash]

        query_hash["entity"] = query_parts[-1]

        query_hash["column_list"] = list(map(lambda x: re.sub(",", '', x), query_parts[1:-2]))

        if where_query:
            operations_query = [x for x in where_query[1::] if x != 'and' and x != 'or']

            if len(operations_query) % 3:
                query_hash['error_flag'] = 'pql_parse_error'
                query_hash['error'] = "Incorrect Syntax for values"
                return [query_hash]

            counter = 1
            query_hash["where"] = []

            while counter < len(where_query):
                query_hash["where"] += [{
                    'column_name': where_query[counter],
                    'operator': where_query[counter + 1],
                    'argument': where_query[counter + 2]
                }]

                if counter + 3 >= len(where_query):
                    break

                query_hash["where"] += [where_query[counter + 3]]

                counter += 4

        return [query_hash]

    def delete_command(self, query_parts):
        query_hash = {"command": query_parts[0], "error": ""}

        where_query = []
        if 'where' in query_parts:
            index = query_parts.index('where')
            query_parts_1 = query_parts[0:index]
            where_query = query_parts[index::]
            query_parts = query_parts_1

        if query_parts[1] != 'from':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = 'Table not mentioned'

            return [query_hash]

        query_hash["entity"] = query_parts[2]

        if where_query:
            operations_query = [x for x in where_query[1::] if x != 'and' and x != 'or']

            if len(operations_query) % 3:
                query_hash['error_flag'] = 'pql_parse_error'
                query_hash['error'] = "Incorrect Syntax for values"
                return [query_hash]

            counter = 1
            query_hash["where"] = []

            while counter < len(where_query):
                query_hash["where"] += [{
                    'column_name': where_query[counter],
                    'operator': where_query[counter + 1],
                    'argument': where_query[counter + 2]
                }]

                if counter + 3 >= len(where_query):
                    break

                query_hash["where"] += [where_query[counter + 3]]

                counter += 4

        return [query_hash]

    def commit_command(self, query_parts):
        return [{
            "command": query_parts[0], "error": ""
        }]

    def drop_command(self, query_parts):
        if query_parts[1] == 'database':
            return [{
                "command": "dropdb", "error": ""
            }]
        elif query_parts[1] == 'table':
            return [{
                "command": "drop",
                "entity": query_parts[2], "error": ""
            }]

    # ['update', 'test', 'set', 'name', '=', "'bob'", 'where', 'name', '=', "'jill'"]:
    def update_command(self, query_parts):
        query_hash = {
            "command": query_parts[0], "entity": query_parts[1], "error": ""
        }

        if query_parts[2] != 'set':
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = 'set not mentioned'

            return [query_hash]

        where_index = query_parts.index('where')
        set_index = query_parts.index('set')

        set_query_parts = query_parts[set_index:where_index]
        where_query_parts = query_parts[where_index::]

        set_arguments = set_query_parts[1::]
        if len(set_arguments) % 3:
            query_hash['error_flag'] = 'pql_parse_error'
            query_hash['error'] = "Incorrect Syntax for set"
            return [query_hash]

        counter = 1
        query_hash['set'] = []
        while counter < len(set_query_parts):
            argument = set_query_parts[counter + 2]
            if set_query_parts[counter + 2][-1] == ',':
                argument = argument[0:-1]

            query_hash['set'] += [{
                'column_name': set_query_parts[counter],
                'operator': set_query_parts[counter + 1],
                'argument': argument
            }]

            counter += 3

        if where_query_parts:
            operations_query = [x for x in where_query_parts[1::] if x != 'and' and x != 'or']

            if len(operations_query) % 3:
                query_hash['error_flag'] = 'pql_parse_error'
                query_hash['error'] = "Incorrect Syntax for values"
                return [query_hash]

            counter = 1
            query_hash["where"] = []

            while counter < len(where_query_parts):
                query_hash["where"] += [{
                    'column_name': where_query_parts[counter],
                    'operator': where_query_parts[counter + 1],
                    'argument': where_query_parts[counter + 2]
                }]

                if counter + 3 >= len(where_query_parts):
                    break

                query_hash["where"] += [where_query_parts[counter + 3]]

                counter += 4

        return [query_hash]

    # ----- Command Implementation Finished -----


    def build_command(self, query_parts):
        # print("sanitized query_parts is {}: ".format(query_parts))

        command = query_parts[0]
        if command not in Parser.COMMANDS:
            # print("This command {} is not implemented".format(command))

            return [{
                "command": query_parts[0],
                'error': "Incorrect command",
                "error_flag": "pql_parse_error"
            }]

        if command != 'use' and self._active_db == '':
            return [{'error_flag': 'no_selected_db', 'error': 'no_selected_db'}]

        return getattr(self, "{}_command".format(command))(query_parts)

    def build_query_list(self):
        input_query_list = list(
            map(lambda x: x.strip(), re.split(''';(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', self._input_string)))
        input_query_list = filter(None, input_query_list)

        query_list = []
        for query in input_query_list:
            # print("query is {}: ".format(query))
            sanitized_query_parts = self.sanitize(query)
            query_list += self.validate(self.build_command(sanitized_query_parts))

        return query_list

    def __init__(self, input):
        self._input_string = input.strip()
        self._active_db = ''

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
# 	"argument": "id>3"
# }

# {
# 	"command": "use",
# 	"entity": 'foo'
# }

