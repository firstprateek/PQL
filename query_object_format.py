use test5;
create table test (id int, name string);
insert into test values (1, 'jack');
insert into test values (2, 'jill');
insert into test values (3, 'john');
select name from test where name>='jill' and id = 3 or id <> 5;
commit;

{
	"command": "use",
	"entity": "test5",
	"error": "error_message"
}

{
	"command": "create",
	"entity": "test",
	"values": [ 
		{ "column_name": "id", "column_type": "int" }, 
		{ "column_name": "name", "column_type": "string" } 
	],
	"error": "error_message"	
}

{
	"command": "insert",
	"entity": "test",
	"row_values": [ '1', 'jack' ],
	"error": "error_message"
}

{
	"entity": "test",
	"command": "selet",
	"column_list": ['name'],
	"where": [
		{
			'column_name': 'name',
			'operator': '>='
			'argumnet': 'jill'
		},

		'and',

		{
			'column_name': "id", 
			'operator': "=",
			'argumnet': 3
		},

		'or',

		{
			'column_name': "id", 
			'operator': "<>",
			'argumnet': 5
		}

	]
}

{
	"command": "commit"
}