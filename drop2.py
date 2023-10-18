import subprocess
import sys, os
import codecs
from zoautil_py import datasets

def count_elements(_list):
    # return length of parameter string
    return len(_list)

def write_array_to_file(_array, _file_path):
    # open file in write mode
    with open(_file_path, 'w') as file:
        # iterate list and write each element to new line
        for item in _array:
            file.write(f"{item}\n")

def find_agents():
    # print message for clarity during execution
    print("Finding hidden agents..")

    # list of all found hidden agents 
    hidden_agents = []

    # directory and pattern to be searched
    directory = "/z/zxp-contest/20211015"
    pattern = ".000*"

    # find command
    command = f'find {directory} -name "{pattern}"'
    
    # run find command and store output
    result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE)
    
    # split output into lines and store in array
    agent_directories = result.stdout.strip().split('\n')
    
    # store all hidden agents in the hidden_agents list
    for agent_directory in agent_directories:
        hidden_agents.append(agent_directory.split("\n"))

    # print successful execution message
    print(f"{count_elements(hidden_agents)} hidden agent directories printed to hidden_agents.txt")
    
    # return list of hidden agents
    return agent_directories

def find_encrypted_codes(_directories):
    # print message for _agent_directoriesclarity during execution
    print("Finding encrypted codes..")

    # list of all found encrypted codes
    encrypted_codes = []

    for _directory in _directories:
        # find command to list files in directory
        command = f'find {_directory} -type f'
        
        # run find command and store output
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE)
        
        # split output into lines
        lines = result.stdout.strip().split('\n')

        # truncate first 55 characters of each line
        truncated_lines = [line[55:] for line in lines]

        # extend the encrypted_codes list with truncated lines
        encrypted_codes.extend(truncated_lines)

    # print successful execution message
    print(f"{len(encrypted_codes)} encrypted codes printed to encrypted_codes.txt")

    # return list of encrypted codes
    return encrypted_codes

def decrypt_codes_1(_codes): # change to file parameter
    # print message for clarity during execution
    print("Decrypting codes using substitution cypher..")
    
    # list of all found decrypted codes
    decrypted_codes = []

    # original and altered alphabets
    alphabet_from = "0987654321zyxwvutsrqponmlkj@"
    alphabet_to = "abcdefghijklmnopqrstuvwxyz -"
    
    # substitution cypher - translate original characters to altered characters
    subsititution_cypher = str.maketrans(alphabet_from, alphabet_to)

    # convert each character in encrypted_code from alphabet_original to alphabet_altered
    for _code in _codes:
        decrypted_codes.append(_code.translate(subsititution_cypher))
    
    # print successful execution message
    print(f"{count_elements(decrypted_codes)} decrypted codes printed to decrypted_codes_1.txt")

    # return the list of decrypted codes
    return decrypted_codes

def decrypt_codes_2(_file_path):
    # print message for clarity during execution
    print("Decrypting codes using first letters of each word..")
    
    # list of all found decrypted codes
    decrypted_codes = []

    # open file and loop through each line - cant get it working with list like others
    with open(_file_path, 'r') as file:
        for line in file:
            # Split the line into words and get rid of spaces etc
            line = line.strip()
            words = line.split()
            # Extract the first character of each word and append to the list
            first_characters = [word[0] for word in words]
            decrypted_codes.append(''.join(first_characters))

    # print successful execution message
    print(f"{count_elements(decrypted_codes)} decrypted codes printed to decrypted_codes_2.txt")

    # return the list of decrypted codes
    return decrypted_codes

def decrypt_codes_3(_file_path):
    # print message for clarity during execution
    print("Trimming decrypted codes..")
    
    # list of all found decrypted codes
    decrypted_codes = []

    # open file and loop through each line - cant get it working with list like others
    with open(_file_path, 'r') as file:
        for line in file:
            last_characters = line[-9:] # last 8
            decrypted_codes.append(last_characters.upper()[:8]) # first 8 - avoid \n

    # print successful execution message
    print(f"{count_elements(decrypted_codes)} decrypted codes printed to decrypted_codes_3.txt")

    # return the list of decrypted codes
    return decrypted_codes

def sort_file_descending_to_dataset(_file_path_in, file_path_out):
    # print message for clarity during execution
    print("Sorting trimmed decrypted codes..")

    # Read the content of the file
    with open(_file_path_in, 'r') as file:
        lines = file.readlines()

    # Sort the lines in descending order
    sorted_lines = sorted(lines, reverse=True)

    # Write the sorted lines back to the file
    with open(file_path_out, 'w') as file:
        file.writelines(sorted_lines)

    # loop through all the sorted lines with an index
    for index, sorted_line in enumerate(sorted_lines):
        # for the first line, do not append so that you start with a fresh file
        if index == 0:
             datasets.write(dataset_output_drop2, sorted_line[:8], False)
        # append for the rest
        else:
            datasets.write(dataset_output_drop2, sorted_line[:8], True)

    # print message for clarity during execution
    print(f"Sorted codes printed to {file_path_out}")

if __name__ == "__main__":
    # initialise file paths
    file_hidden_agents = "drop2_file_hidden_agents.txt"
    file_encrypted = "drop2_file_encrypted.txt"
    file_decrypted_1 = "drop2_file_decrypted_1.txt"
    file_decrypted_2 = "drop2_file_decrypted_2.txt"
    file_decrypted_3 = "drop2_file_decrypted_3.txt"
    file_sorted = "drop2_file_sorted.txt"
    dataset_output_drop2 = "Z36434.OUTPUT(Q421DRP2)"

    # part 1 - find hidden agents, print to hidden_agents.txt
    hidden_agents = find_agents()
    write_array_to_file(hidden_agents, file_hidden_agents)

    # part 2 - find encrypted codes, print to encrypted_codes.txt
    encrypted_codes = find_encrypted_codes(hidden_agents)
    write_array_to_file(encrypted_codes, file_encrypted)

    # part 3 - decrypt the ecrypted file names using an alphabet substitution
    decrypted_codes_1 = decrypt_codes_1(encrypted_codes)
    write_array_to_file(decrypted_codes_1, file_decrypted_1)

    # part 4 - decrypt file again using first letter of each word
    decrypted_codes_2 = decrypt_codes_2(file_decrypted_1)
    write_array_to_file(decrypted_codes_2, file_decrypted_2)
 
    # part 4 - trim decrypted codes
    decrypted_codes_3 = decrypt_codes_3(file_decrypted_2)
    write_array_to_file(decrypted_codes_3, file_decrypted_3)

    # part 5 - sort trimmed decrypted codes in descending order
    sort_file_descending_to_dataset(file_decrypted_3, file_sorted)
