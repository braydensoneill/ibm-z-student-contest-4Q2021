import ibm_db
import sys, os
import codecs
from zoautil_py import datasets
import binascii

def run_sql():
    try:
        # connect to database
        connection = ibm_db.connect('','','')

        if connection:
            # print message for clarity during execution
            print("Connected to the database")
 
            # set encrytion password - found using SELECT DISTINCT REMARKS FROM SYSIBM.SYSCOLUMNS WHERE TBCREATOR = 'ZXP214';
            sql_password = '''
                SET ENCRYPTION PASSWORD = 'MakeMyDayZ'
            '''

            # select query for engineer information, decrypt location code
            sql_select = '''
                SELECT V.VID, V.VNAME, E.EID, E.ENAME, DECRYPT_CHAR(L.LCODE) as DECRYPTED_LCODE
                FROM ZXP214.VENDORS V
                JOIN ZXP214.ENGINEERS E ON V.VID = E.VID
                JOIN ZXP214.LOCATORS L ON E.EID = L.EID
                ORDER BY V.VID, E.EID
            '''

            # execute previous sql statements
            ibm_db.exec_immediate(connection, sql_password)
            statement = ibm_db.exec_immediate(connection, sql_select)

            # fetch column names
            columns = [ibm_db.field_name(statement, i) for i in range(ibm_db.num_fields(statement))]

            # print column names
            print("Column Names:")
            print(', '.join(columns))

            # pretty output title for sql data
            print("\nQuery Result:")

            # fetch row retrieved from sql statement
            while True:
                # return retrieved row as array
                row = ibm_db.fetch_assoc(statement)

                # break the loop if no more rows are returned
                if not row:
                    break
    
                # store retrieved row columns in individual columns
                data_to_lists(row["VID"], row["VNAME"], row["EID"], row["ENAME"], row["DECRYPTED_LCODE"])

                # print retrieved row
                print(row)
        else:
            print(f"Connection failed: {ibm_db.conn_errormsg()}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        if 'connection' in locals():
            ibm_db.close(connection)
            print("Connection closed")

    # end of function
    return

def data_to_lists(_v_id, _v_name, _e_id, _e_name, _l_code):
    # append parameters to their respective lists
    list_v_id.append(_v_id)
    list_v_name.append(_v_name)
    list_e_id.append(_e_id)
    list_e_name.append(_e_name)
    list_l_code.append(_l_code)

    # end of function
    return

def write_lists_to_file(_file_path_rows, _list_v_id, _list_v_name, _list_e_id, _list_e_name, _list_l_code):
    # use the length of the v_id to loop, will work for all as they are all the same length
    list_length = len(_list_v_id)

    # open file for writing
    with open(_file_path_rows, 'w') as file:

        # loop through the list
        for i in range(list_length):
            # format the string to be printed
            row = f'{_list_v_id[i]},"{_list_v_name[i]}",{_list_e_id[i]},"{_list_e_name[i]}","{_list_l_code[i]}"\n'

            # print string to file
            file.write(row)

    # print successful execution message        
    print(f'Data written to {_file_path_rows}')

    # end of function
    return

def write_file_to_dataset(_file_in, _dataset_out):
    # print message for clarity during execution
    print(f"Writing data from {_file_in} to {_dataset_out}..")

    # open the input file
    with open(_file_in, 'r') as file:

        # loop through all the sorted lines with an index
        for index, line in enumerate(file):
            # for the first line, do not append so that you start with a fresh file, [:-1] to ignore the \n
            if index == 0:
                datasets.write(_dataset_out, line[:-1], False)
            # append for the rest
            else:
                datasets.write(_dataset_out, line[:-1], True)

    # print successful execution message        
    print(f'Data written to {_dataset_out}')

    # end of function
    return

if __name__ == "__main__":
    # output files
    file_path_records = "drop3_file_records.txt"
    dataset_output_drop3 = "Z36434.OUTPUT(Q421DRP3)"

    # lists storing sql data
    list_v_id = []
    list_v_name = []
    list_e_id = []
    list_e_name = []
    list_l_code = []

    # part 1 - run sql select to retrieve data and store in lists
    run_sql()

    # part 2 - write cleaned data to file
    write_lists_to_file(file_path_records, list_v_id, list_v_name, list_e_id, list_e_name, list_l_code)

    # part 3 - write file to dataset
    write_file_to_dataset(file_path_records, dataset_output_drop3)
