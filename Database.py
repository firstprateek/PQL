import sys

directory_path ="/Users/nguyenthaian/Documents/Advanced Computer Security/pql/PQL/Database/"
errors_list = ["Unspecified", "type_mismatch", "table_exists", "no_selected_db", "db_parse",
               "pql_parse", "int_range", "string_size"]

class Table:
    # table information
    table_name = '' #table name
    start_line = 0  #the starting line
    number_lines = 0 #the number of lines

    array_columns_type = []  #the array containing columns
    table_content = {}          #the directory containing value : column
    total_data =""

    # Read the table file
    def Read_File(self, file):
        full_path = directory_path + self.table_name
        try:
            file = open(full_path, "r")
        except IOError:
            print("table_no_exist")
            exit(0)
        self.total_data = file.read()
        print(self.total_data)
        file.close()

    def __init__(self, __table_file_name):
        self.table_name = __table_file_name
        self.Read_File(__table_file_name)

#class Database :

table_demo = Table("student.txt")


