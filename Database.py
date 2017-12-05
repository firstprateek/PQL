import sys
import os
import random

PQL_TOC_KEY = 'PQL_DATABASE_TOC'
directory_path ="/Users/nguyenthaian/Documents/Advanced Computer Security/pql/PQL/Database/"
errors_list = ["Unspecified", "type_mismatch", "table_exists", "no_selected_db", "db_parse",
               "pql_parse", "int_range", "string_size"]

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
                    if line[count] == ',':
                        if second_temp == 0 and first_temp == 0: second_temp = first_temp
                        elif first_temp != 0: second_temp = first_temp + 1
                        first_temp = count
                        self.column_type.append(line[second_temp:first_temp])

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
                    if line[count] == ',':
                        if second_temp == 0 and first_temp == 0: second_temp = first_temp
                        elif first_temp != 0: second_temp = first_temp + 1
                        first_temp = count
                        row.append(line[second_temp:first_temp])
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



class Database :
    key_word_PQL = ''
    db_content = ''
    db_start_line = 0
    db_end_line = 0

    line = ''

    table_information = []
    list_of_tables = []

    all_tables = {}


    def Verify_Line(self, line):
        line = line.rstrip('\n')
        line = line.strip()

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
        self.list_of_tables.append(self.table_information)

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
            # if count == self.db_content.__len__() and self.db_content[count-1] != "\n":
            #     self.line = self.db_content[temp:]
            #     self.Get_Table_Information()
        print(self.list_of_tables)


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
        #print(self.db_content)
        # print(len(self.db_content))

    def Read_db_File(self, file_name):
        full_path = directory_path + file_name
        file = open(full_path, "r")
        for num, line in enumerate(file, 1):

            if self.key_word_PQL in line:
                self.db_start_line = num
            if len(line.strip()): self.db_end_line = num

        file.close()
        #print(self.db_start_line)
        #print(self.db_end_line)

    # def Verify_List_Table(self):
    #     for item in self.list_of_tables:
    #         #item[1] = str(int(item[1]) + 1)
    #         item[2] = str(int(item[2]) + 1)

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

            #print(table.column_type)
            #print(table.table_content)

            table_type_and_content = []
            table_type_and_content.append(table.column_type)
            table_type_and_content.append(table.table_content)
            self.all_tables [table.table_name] = table_type_and_content

            count = count + 1
            file.close()

        #print(self.all_tables['id'])



    def __init__(self, db_file):
        self.key_word_PQL = PQL_TOC_KEY
        self.db_content = ''
        self.db_start_line = 0
        self.db_end_line = 0
        self.all_tables = {}

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


