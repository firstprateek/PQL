import sys
import os
import random

PQL_TOC_KEY = 'PQL_DATABASE_TOC'
directory_path ="/Users/nguyenthaian/Documents/Advanced Computer Security/pql/PQL/Database/"
errors_list = ["Unspecified", "type_mismatch", "table_exists", "no_selected_db", "db_parse",
               "pql_parse", "int_range", "string_size"]
export_db_path = "/Users/nguyenthaian/Documents/Advanced Computer Security/pql/PQL/output/"

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

    # A function to read the db file
    def Read_db_File(self, file_name):
        full_path = directory_path + file_name
        file = open(full_path, "r")
        for num, line in enumerate(file, 1):

            if self.key_word_PQL in line:
                self.db_start_line = num
            if len(line.strip()): self.db_end_line = num
        file.close()

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

    # Check if the table exist
    def Is_Table_Name_Valid(self, _table_name):
        for item in self.list_of_tables:
            if _table_name == item[0]: return True
        return  False

################# End Group #############################

################ Export DB ##############################
    # Build exporting file name
    def Build_Output_File_Name(self):
        return self.export_file_name

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

    def Export_DB(self):
        full_path = export_db_path + self.Build_Output_File_Name()
        file = open(full_path, 'w')
        #print(self.list_of_tables)
        #print(self.all_tables)
        for temp in self.list_of_tables:
            table_name = temp[0]
            item = self.all_tables.get(table_name)
            file.write(self.Build_A_Export_Line(item[0]))
            for row_item in item[1]:
                file.write(self.Build_A_Export_Line(row_item))
        file.write(self.key_word_PQL + '\n')
        for item in self.list_of_tables:
            file.write(self.Build_A_Export_Line(item))


    def __init__(self, db_file):
        self.key_word_PQL = PQL_TOC_KEY
        self.db_content = ''
        self.db_start_line = 0
        self.db_end_line = 0
        self.all_tables = {}
        self.export_file_name = db_file

        try:
            self.Read_db_File(db_file)
        except IOError:
            print("The database file doesn't exist.")
            exit(0)

        if self.db_end_line != self.db_start_line: self.Read_db_Content(db_file)
        else: exit(0)
        self.Get_List_Of_Tables()
        self.Read_Table_Content(db_file)


db = Database("test1.db")
db.Show_All_Table_Content()
db.Export_DB()
print(db.Is_Number_Valid(20))
print(db.Is_Table_Name_Valid('an'))


