import sys
import os
import random
from enum import Enum

PQL_TOC_KEY = 'PQL_DATABASE_TOC'
directory_path = os.getcwd() + '/'
export_db_path = os.getcwd() + '/'
ErrorCode = {
    'db_parse':1, # the db name doesn't exist
    'no_selected_db' : 2, # no selected db
    'table_exists' : 3, # A table exist so can not create another one same name
    'type_mismatch' : 4, # the inserted value does not match type with the columne
    'int_range' : 5, # the value is greater than the limitation
    'string_size' : 6 # the string is too long
}
#
# The class of a table containing:
#           The first line is column-type
#           Each next line is row data
#
class Table:
    # table information
    table_name = '' #table name
    start_line = 0  #the starting line
    number_lines = 0 #the number of lines
    column_type = []
    array_columns_type = {}  #the array containing columns
    table_content = []          #the directory containing value : column

    # A function to detect information of each table
    # Code = 1, detect the first line of each table which is set of column types
    # Code = 0, detect each row of table
    def Get_Column_Type(self, line, code = 1):
        row = []  # An array to store a row data

        # Modify a line, remove \n and space
        line = line.rstrip('\n')
        line = line.strip()
        ####################

        first_temp = 0 # the first running pointer to get the index of ','
        second_temp = 0 # the second running pointer to get the staring point
        count = 0 # the running index

        number_of_type = 0 # the variable to evaluate how many element needed to get
        # Counting how many element
        for char in line:
            if char == ',': number_of_type = number_of_type + 1

        #Detecting the column type line
        if code == 1:
            while count < len(line):
                if number_of_type == 0:
                    self.column_type.append(line)
                    break
                else:
                    # running pointer in the string
                    if line[count] == ',':
                        if second_temp == 0 and first_temp == 0: second_temp = first_temp
                        elif first_temp != 0: second_temp = first_temp + 1
                        first_temp = count
                        self.column_type.append(line[second_temp:first_temp])

                    # Get the last part which is from ',' to ' '
                    elif count == len(line) - 1:
                        self.column_type.append(line[first_temp + 1:count + 1])

                count = count + 1

        #Detecting a row data
        elif code == 0:
            while count < len(line):
                if number_of_type == 0:
                    row.append(line)
                    break
                else:
                    # running pointer in the string
                    if line[count] == ',':
                        if second_temp == 0 and first_temp == 0: second_temp = first_temp
                        elif first_temp != 0: second_temp = first_temp + 1
                        first_temp = count
                        row.append(line[second_temp:first_temp])

                    # Get the last part which is from ',' to ' '
                    elif count == len(line) - 1:
                        row.append(line[first_temp + 1:count + 1])
                count = count + 1
            self.table_content.append(row)


#The table_content looks like [[row1], [row2], ... [row n]]
#The column_type looks like ['columname1:type1', ...,'columname n: type n']

    # Constructor of a table
    def __init__(self, _table_name, _start_line, _number_of_line):
        self.table_name = _table_name
        self.start_line = int(_start_line)
        self.number_lines = int(_number_of_line)
        self.column_type =[]
        self.array_columns_type = {}
        self.table_content = []

# A database class to store information of tables in the db file
#
class Database :
    # The key word which is to decide where the list of tables starts
    key_word_PQL = ''
    # A string which gets content from the db file from the starting line to the end line
    db_content = ''
    db_start_line = 0 # The starting line of the list of tables
    db_end_line = 0     # The end line
    line = '' # A variable is to save each line from the file. It makes easier to modify

    # Export
    export_file_name = ''
    # An array to save the information of each table
    #['table_name', 'start_line', 'number_of_line']
    table_information = []
    # A list of all tables
    # [[information of tab1], [information of table2], ...]
    list_of_tables = []
    # A dictionary formed 'table_name': [[table-column-type],[[row1 data], [row2 data], [row3 data], ...]]
    all_tables = {}
    # List of test queries
    command_list = []

    # # Get key
    def Get_Error_Key (_List_error, _value):
        for key, value in _List_error.items():
            if value == _value : return key
            else: return None
    # A function remove '\n' and ' ' in a line
    def Verify_Line(self, line):
        line = line.rstrip('\n')
        line = line.strip()
        line = line.translate(str.maketrans({"'":None}))

    # Function detecting a table information. It gets table-name, starting-line, number-of-line
    def Get_Table_Information(self):
        self.line.strip()
        first_temp = 0
        second_temp = 0
        count = 0

        while count < self.line.__len__():
            if self.line[count] == ',':
                if first_temp == 0: first_temp = count
                elif first_temp != 0 and second_temp == 0: second_temp = count
            count = count + 1

        self.table_information.append(self.line[:first_temp])
        self.table_information.append(self.line[first_temp + 1:second_temp])
        self.table_information.append(self.line[second_temp + 1:])

        # Add a table information into the list
        self.list_of_tables.append(self.table_information)

    # A function to detect each line which contains a table information
    def Get_List_Of_Tables(self):
        temp = 0
        count = 0
        self.db_content.strip()
        #Get information of each table
        while count < self.db_content.__len__():
            if self.db_content[count] == "\n":
                self.line = self.db_content[temp:count]
                self.Get_Table_Information()
                temp = count
                temp = temp + 1

                #clear table information
                self.table_information = []
            count = count + 1
        #print(self.list_of_tables)

    # A function to reach all contents which are all information existing in the db file, and remarked below the key word
    def Read_db_Content(self, file_name):
        full_path = directory_path + file_name
        file = open(full_path, "r")
        for num, line in enumerate(file, 1):
            if self.db_start_line != self.db_end_line:
                if num > self.db_start_line and num <= self.db_end_line:
                    # check line != " " or "\n"
                    line = line.rstrip("\n")
                    if len(line.strip()):
                        self.db_content = self.db_content + line
                        self.db_content = self.db_content + '\n'

        file.close()

    # Build exporting file name
    def Build_Output_File_Name(self):
        return self.export_file_name

    # Build a line to export
    def Build_A_Export_Line(self, _array):
        result = ''
        count = 0
        if _array ==[]:
            return "\n"
        else :
            while count < len(_array):
                if count < len(_array) - 1:
                    result = result + _array[count] + ','
                elif count == len(_array) - 1:
                    result = result + _array[count]
                count = count + 1
        return result + '\n'

        # Write down to a text file

    def Export_DB(self, _path=0):
        full_path = directory_path + self.export_file_name
        file = open(full_path, 'w')
        if self.list_of_tables:
            for temp in self.list_of_tables:
                table_name = temp[0]
                item = self.all_tables.get(table_name)
                file.write(self.Build_A_Export_Line(item[0]))
                for row_item in item[1]:
                    file.write(self.Build_A_Export_Line(row_item))
            file.write(self.key_word_PQL + '\n')
            for item in self.list_of_tables:
                file.write(self.Build_A_Export_Line(item))
        else:
            file.write(self.key_word_PQL + '\n')
        file.close()

    # A function to read the db file
    def Read_db_File(self, file_name):
        full_path = ''
        full_path = directory_path + file_name
        try:
            file = open(full_path, "r")
            for num, line in enumerate(file, 1):
                if self.key_word_PQL in line:
                    self.db_start_line = num
                if len(line.strip()): self.db_end_line = num
            file.close()
            # print(self.db_start_line)
            if self.db_start_line == 0:
                print("db_parse")
                exit(ErrorCode["db_parse"])
        except FileNotFoundError:
            self.Export_DB(self.export_file_name)

    # A function is to buil the dictionary , all_tables
    def Read_Table_Content(self, file_name):
        full_path = directory_path + file_name
        count = 0
        while count < len(self.list_of_tables):
            file = open(full_path, "r")
            table = Table(self.list_of_tables[count][0], self.list_of_tables[count][1], self.list_of_tables[count][2])
            #print(table.table_name)
            for num, line in enumerate(file, 1):
                if num == table.start_line + 1:
                    self.Verify_Line(line)
                    table.Get_Column_Type(line)
                    #print(table.column_type)
                    continue
                if num > table.start_line+1 and num <= table.number_lines + table.start_line:
                    self.Verify_Line(line)
                    table.Get_Column_Type(line, 0)
                    #print(table.table_content)
                    continue

            table_type_and_content = []
            table_type_and_content.append(table.column_type)
            table_type_and_content.append(table.table_content)
            self.all_tables [table.table_name] = table_type_and_content
            count = count + 1
            file.close()

#########################################################
############## Display TOC function group################
#########################################################

    # A function is to print a specific row
    def Print_A_Line(self, _array):
        count = 0
        while count < len(_array):
            if count != len(_array) - 1:
                print(_array[count], end="|")
            elif count == len(_array) - 1:
                print(_array[count])
            count = count + 1

    # Show each row in a table
    def Show_A_Row(self, _row_data):
        number_of_item = 0
        while number_of_item < len(_row_data):
            #print(_row_data[number_of_item])
            temp = _row_data[number_of_item]
            self.Print_A_Line(temp)
            number_of_item = number_of_item + 1

    # Show all rows
    def Show_A_Table_Content (self, _table_name):
        print(_table_name)

        #Get content of the table
        #temp = [[columns type], [[row1], [row2], [row3]]]
        temp = self.all_tables[_table_name]
        temp_row_content = temp[1]

        #print each row
        self.Show_A_Row(temp_row_content)

    # Show all things of a table
    def Show_All_Table_Content(self):
        amount_of_table = 0
        while amount_of_table < len(self.all_tables):
            self.Show_A_Table_Content(self.list_of_tables[amount_of_table][0])
            amount_of_table = amount_of_table + 1


#########################################################
############## Query Operation Group ####################
#########################################################

    # Check the integer number
    def Is_Number_Valid(self, _number):
        if _number >= (-2)**63 + 1 and _number<= 2**63 + 1: return True
        return  False

    def _Query_USE(self, _query_use):
        db_name = _query_use.get('entity')
        self.export_file_name = db_name
        if db_name :
            # print(self.db_start_line)
            # print(self.db_end_line)
            # print(self.all_tables)
            # print(self.list_of_tables)
            self.Read_db_File(db_name)
            self.Read_db_Content(db_name)
            self.Get_List_Of_Tables()
            self.Read_Table_Content(db_name)
            # print(self.all_tables)
            # print(self.list_of_tables)

        else:
            # if db_name = ' ' print no_selected db
            print("no_selected_db")
            exit(ErrorCode["no_selected_db"])

    # Execute CREATE
    # Check if the table exist
    def Is_Table_Name_Valid(self, _table_name):
        for item in self.list_of_tables:
            if _table_name == item[0]:
                return True
        return False

    def Count_New_Line(self):
        result = 0
        if self.list_of_tables != [] :result = int(self.list_of_tables[len(self.list_of_tables)-1][1]) + int(self.list_of_tables[len(self.list_of_tables)-1][2])
        return result
    def _Query_CREATE(self, _query_create):
        tb_name = _query_create.get('entity')
        # check if the table exists or not
        if self.Is_Table_Name_Valid(tb_name) == False:
            if tb_name:
                #Update the information for the new table
                #begin
                new_tb = []
                new_line = self.Count_New_Line()
                new_tb.append(tb_name)
                new_tb.append(str(new_line))
                new_tb.append('1')
                self.list_of_tables.append(new_tb)

                #end

                #Get content for the new table
                content_new_tb = []
                col_declare = []
                value = _query_create['values']
                #check if the number of included columns is empty
                if value:
                    for item in value:
                        string = ''
                        col_name = item['column_name']
                        col_type = item['column_type']
                        string = col_name + ':' + col_type
                        col_declare.append(string)
                    content_new_tb.append(col_declare)
                    content_new_tb.append([])
                    self.all_tables[tb_name] = content_new_tb

                else:
                    print("Cannot create a new table which does not have any columns")
                    exit(0)
            else:
                print("Cannot create a new table without name.")
                exit(0)
        else:
            print("table_exists")
            exit(ErrorCode["table_exists"])

    # Execute INSERT
    def Get_Type_Of_A_Table(self, _tb_name):
        column = self.all_tables[_tb_name][0]
        type_of_col = []
        for item in column:
            index = item.index(':')
            type_of_col.append(item[index+1:])
        return type_of_col

    def Matching_Type(self, _type, _value):
        if _type == 'string' and _value.isdigit() == True:
            return False
        elif _type == 'string' and _value.isdigit() == False:
            return True
        elif _type == 'int' and _value.isdigit() == True:
            return True
        elif _type == 'int' and _value.isdigit() == False:
            return False

    def Increase_Number_Of_Line(self, _tb_name):
        count = 0;
        while count < len(self.list_of_tables):
            item = self.list_of_tables[count]
            if _tb_name == item[0]:
                self.list_of_tables[count][2] = str(int(self.list_of_tables[count][2]) + 1)
            count = count + 1

    def _Query_INSERT(self, _query_insert):
        tb_name = _query_insert['entity']
        if self.Is_Table_Name_Valid(tb_name) == True:
            if tb_name:
                # print(self.all_tables)
                # print(self.list_of_tables)
                self.Increase_Number_Of_Line(tb_name)

                content_db = self.all_tables[tb_name]

                row_insert_value = _query_insert['row_values']
                if len(row_insert_value) == len(content_db[0]):
                    inserted_row = []
                    cols_type = self.Get_Type_Of_A_Table(tb_name)
                    running_pointer = 0
                    while running_pointer < len(content_db[0]):
                        if self.Matching_Type(cols_type[running_pointer], row_insert_value[running_pointer]) == True:
                            inserted_row.append(row_insert_value[running_pointer])
                        else:
                            print('type_mismatch')
                            exit(ErrorCode['type_mismatch'])
                        running_pointer = running_pointer + 1
                    content_db[1].append(inserted_row)
                else:
                    print("Need to have values to insert")
                    exit(0)
        else:
            print("table_exists")
            exit(ErrorCode["table_exists"])
        # print(self.all_tables)
        # print(self.list_of_tables)

    # Execute select
    def Delete_Single_Quote(self, _string):
        return _string.replace("'","")

    def Get_Col_List(self, _tb_name):
        result_list = []
        temp = self.all_tables[_tb_name][0]
        #print(temp)
        for col in temp:
            location = col.find(':')
            column_name = col[:location]
            column_type = col[location + 1:]
            result_list.append(column_name)
        return (result_list)

    def Build_Condition(self, _value, _operator, _arg):
        result = False
        # print(_value)
        # print(_operator)
        # print(_arg)
        if _operator == '=':
            result = _value == _arg
        elif _operator == '<>' or _operator == '!=':
            result =  _value != _arg
        elif _operator == '>':
            result =  _value > _arg
        elif _operator == '>=':
            result =  _value >= _arg
        elif _operator == '<':
            result = _value < _arg
        elif _operator == '<=':
            result =  _value <= _arg
        return  result

    def Connection_Condition(self, _value1, _con, _value2):
        if _con is 'and': return  _value1 and _value2
        elif _con is 'or': return  _value1 or _value2
        else: return  False

    def Show_Select_Result(self, _tb_name, _array_result_, _array_index):
        print(_tb_name)
        result = []
        for i in _array_result_:
            temp = []
            for j in _array_index:
                temp.append(i[int(j)])
            result.append(temp)
        self.Show_A_Row(result)

    def _Query_SELECT(self, _query_select, Code=0):
        tb_name = _query_select['entity']
        selected_col_list = []
        if self.Is_Table_Name_Valid(tb_name):
            if tb_name :
                col_list = self.Get_Col_List(tb_name)
                #print(col_list)
                temp = _query_select['column_list']
                if len(temp) == 1 and temp[0] == '*':
                    selected_col_list = col_list
                else:
                    selected_col_list = temp
                #print(selected_col_list)

                # check query has condition or not
                try:
                    _has_condition = _query_select['where'] != []
                except KeyError:
                    _has_condition = False
                # has some conditions
                pointer = 0
                result_of_all_conditions = []
                last_condition_result = []
                if _has_condition:
                    while pointer < len(_query_select['where']):
                        if pointer % 2 == 0:
                            result_a_condition = []
                            condition = _query_select['where'][pointer]
                            number_col = 0
                            temp = self.all_tables[tb_name][0]
                            #print(temp)
                            for item in temp:
                                if condition['column_name'] in item:
                                    number_col = temp.index(item)
                            #print(number_col)
                            all_row_data = self.all_tables[tb_name][1]
                            #print(all_row_data)

                            result_a_row = []
                            for row in all_row_data:
                                #print(row)
                                row[number_col] = self.Delete_Single_Quote(row[number_col])
                                #print(row[number_col])
                                condition['operator'] = self.Delete_Single_Quote(condition['operator'])
                                condition['argument'] = self.Delete_Single_Quote(condition['argument'])
                                temp = self.Build_Condition(row[number_col], condition['operator'], condition['argument'])
                                result_a_condition.append(temp)
                            result_of_all_conditions.append(result_a_condition)
                        pointer = pointer + 1
                    # print(result_of_all_conditions)
                    last_condition_result = result_of_all_conditions[0]

                    _has_connection = False
                    for _item in _query_select['where']:
                        if _item == 'and' or _item == 'or': _has_connection = True
                    #print(_has_connection)
                    if _has_connection:
                        i = 1
                        connection = 0
                        while connection < len(_query_select['where']):
                            if connection % 2 == 1:
                                link = _query_select['where'][connection]
                                for val in result_of_all_conditions[i]:
                                    index_val = result_of_all_conditions[i].index(val)
                                    last_condition_result[index_val] = self.Connection_Condition(
                                        last_condition_result[index_val], link, val)
                                i = i + 1
                            connection = connection + 1
                        #print(last_condition_result)
                # no condition, set all TRUE
                else:
                    row_result = []
                    all_row = self.all_tables[tb_name][1]
                    for i in all_row:
                        row_result.append(True)
                    result_of_all_conditions.append(row_result)

                    for item in result_of_all_conditions[0]:
                        last_condition_result.append(item)
                #print(result_of_all_conditions)
                run_result = 0
                selected_row = []
                #print(last_condition_result)
                while run_result < len(last_condition_result):
                    if last_condition_result[run_result] == True:
                        x = self.all_tables[tb_name][1]
                        # print(x[run_result])
                        selected_row.append(x[run_result])
                    run_result = run_result + 1
                # print(selected_row)
                # print(selected_col_list)
                index_result = []
                for v in selected_col_list:
                    colum_tab = self.all_tables[tb_name][0]
                    for k in colum_tab:
                        if v in k: index_result.append(colum_tab.index(k))
                # print(index_result)
                if Code == 0 : self.Show_Select_Result(tb_name,selected_row, index_result)
                if Code ==1 : return selected_row
        else:
            print("db_parse")
            exit(ErrorCode['db_parse'])

    # Execute Show
    def _Query_SHOW(self, _query):
        _tables = _query['entity']
        if _tables == 'tables':
            self.Show_All_Table_Content()
        elif self.Is_Table_Name_Valid(_query['entity']):
            self.Show_A_Table_Content(_query['entity'])
        else:
            print('You mean showing all tables')
            exit(0)

    # Execute Commit
    def _Query_COMMIT(self,_query):
        self.Export_DB(0)

    # Execute Drop Table
    def _Query_DROP(self, _query):
        tb_name = _query['entity']
        print(self.all_tables)
        if self.Is_Table_Name_Valid(tb_name):
                del self.all_tables[tb_name]
                for i in self.list_of_tables:
                    if i[0] == tb_name:
                        self.list_of_tables.remove(i)
        else:
            print('table_exist')
            exit(ErrorCode['table_exists'])

    # Execute Drop Database
    def Remove_DB(self, _query):
        db_name = _query['entity']
        if db_name:
            full_path = directory_path + db_name
            try:
                os.remove(full_path)
            except FileNotFoundError:
                print("no_selected_db")
                exit(ErrorCode["no_selected_db"])
        else:
            print("no_selected_db")
            exit(ErrorCode["no_selected_db"])

    def _Query_DROPDB(self, _query):
        self.Remove_DB(_query)

    # Execute Delete
    # Reduce number line
    def Reduce_Number_Line(self, _tb_name):
        for i in self.list_of_tables:
            if _tb_name == i[0]:
                i[2] = str(int(i[2]) - 1)
    def _Query_DELETE(self, _query):
        _entity = _query['entity']
        _has_condition = True
        try:
            _where = _query['where']
        except:
            _has_condition = False
            _where = False
        if _has_condition:
            _newquery = {'command':'select', 'entity':_entity, 'column_list':['*'], 'where':_where}
        else:
            _newquery = {'command': 'select', 'entity': _entity, 'column_list': ['*']}
        selected_row = self._Query_SELECT(_newquery,1)
        #print(selected_row)
        row_content = self.all_tables[_entity][1]
        #print(row_content)
        for i in selected_row:
            for j in row_content:
                if i == j:
                    row_content.remove(j)
                    self.Reduce_Number_Line(_entity)

    #Execute Update
    def Get_Col_Type(self, _tb_name, _col_name):
        col_list = self.all_tables[_tb_name][0]
        for i in col_list:
            if _col_name in i:
                index = 0
                index = i.index(":")
                return i[index+1:]
        return ''

    def Get_Index_Col(self, _tb_name, _col_name):
        col_list = self.all_tables[_tb_name][0]
        for i in col_list:
            if _col_name in i:
                return col_list.index(i)
        return 0
    def _Query_UPDATE(self, _query):
        _entity = _query['entity']
        _has_condition = False
        try:
            _where = _query['where']
            _has_condition = True
        except KeyError:
            _where = False
            _has_condition = False
        _set = _query['set']
        if _has_condition:
            _newquery = {'command':'select', 'entity':_entity, 'column_list':['*'], 'where':_where}
        else:
            _newquery = {'command': 'select', 'entity': _entity, 'column_list': ['*']}
        selected_row = self._Query_SELECT(_newquery, 1)
        row_col_type = self.all_tables[_entity][0]
        row_content = self.all_tables[_entity][1]
        i = 0
        index_col = []
        new_value = []
        match = []
        while i < len(_set):
            _cname = _set[i]['column_name']
            _newvalue = _set[i].get('argument')
            _ctype = self.Get_Col_Type(_entity, _cname)
            new_value.append(_newvalue)
            index_col.append(self.Get_Index_Col(_entity, _cname))
            bo = _ctype.isdigit() == _newvalue.isdigit()
            if _ctype == 'string' and _newvalue.isdigit() == False:
                bo = True
            elif _ctype == 'int' and _newvalue.isdigit( )== True:
                bo = True
            elif _ctype == 'int' and _newvalue.isdigit() == False:
                bo = False
            elif _ctype == 'string' and _newvalue.isdigit() == True:
                bo = False
            match.append(bo)
            i = i + 1
        #print(match)
        if False in match:
            print(_query['error'])
            #print(self.all_tables[_entity][1])
            exit(0)
        else:
            row_index = 0
            while row_index < len(selected_row):
                row = []
                row = selected_row[row_index]
                for v in index_col:
                    if row[int(v)].isdigit() == new_value[index_col.index(v)].isdigit():
                        row[int(v)] = new_value[index_col.index(v)]
                row_index = row_index + 1

    # Testing System
    def System_Test(self):
        for _query in self.command_list:
            if _query['command'] == 'use':
                self._Query_USE(_query)
            elif _query['command'] =='create':
                self._Query_CREATE(_query)
            elif _query['command'] =='insert':
                self._Query_INSERT(_query)
            elif _query['command'] == 'select':
                self._Query_SELECT(_query)
            elif _query['command'] =='show':
                self._Query_SHOW(_query)
            elif _query['command'] =='commit':
                self._Query_COMMIT(_query)
            elif _query['command'] == 'drop':
                self._Query_DROP(_query)
            elif _query['command'] == 'dropdb':
                self._Query_DROPDB(_query)
            elif _query['command'] == 'delete':
                self._Query_DELETE(_query)
            elif _query['command'] == 'update':
                self._Query_UPDATE(_query)

    def __init__(self, _command_list):
        self.key_word_PQL = PQL_TOC_KEY
        self.db_content = ''
        self.db_start_line = 0
        self.db_end_line = 0
        self.all_tables = {}
        self.list_of_tables = []
        self.command_list = _command_list
        self.System_Test()

