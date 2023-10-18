import sys, os
import codecs
from zoautil_py import datasets

def find_valid_vendors():
    # print message for clarity during execution
    print(f"finding valid vendor codes..") 
    # open output files for writing
    with open(file_vendors_ascii, 'w') as ascii_output_file, open(file_vendors_hex, 'w') as hex_output_file:
        # loop over each input file
        for part_member_name in part_members:
            # read all lines from input file
            part_lines = datasets.read(f"ZXP.CONTEST.Q42021.SOURCE({part_member_name})").split("\n")
             # skip first line
            part_lines = part_lines[1:]
            # loop through each line
            for part_line in part_lines:
                # read 12-character string starting at character 36
                substring = part_line[36:48]  
                # convert hex to ASCII
                ascii_text = bytes.fromhex(substring).decode('ascii') 
                # if ASCII code begins with '8', print to output file
                if ascii_text.startswith('8'):
                    # write ASCII code to output file 1
                    ascii_output_file.write(part_line[:36] + '-' + ascii_text[-3:] + '\n')  
                    # write the hex code to output file 2
                    hex_output_file.write(part_line[:36] + '-' + substring + '\n') 
            # print message for clarity during execution
            print(f"vendor codes in part {dataset}({part_member_name}) parsed.")
    # print successful execution message
    print(f"ASCII vendor codes printed to '{file_vendors_ascii}'") 
    print(f"HEX vendor codes printed to '{file_vendors_hex}'") 

def find_valid_assemblies():
    # print message for clarity during execution
    print(f"finding valid assemblies..")
    # create a file for writing valid assembly names
    with open(file_assemblies, 'w') as valid_assemblies_file:
        # loop over each input file
        for assembly_member_name in assembly_members:
            # read all lines from input file
            assembly_lines = datasets.read(f"ZXP.CONTEST.Q42021.SOURCE({assembly_member_name})").split("\n")
            # flag to check if all GUIDs in the assembly are valid
            all_guids_valid = True
            # loop through each line
            for assembly_line in assembly_lines:
                # read first 36 characters from assembly_line
                guid_assembly = assembly_line[:36]
                # read hex output file
                with open(file_vendors_hex, 'r') as hex_output_file:
                    # flag to check if current GUID in the assembly is valid, default false
                    guid_valid = False
                    # loop each line in file
                    for part_line in hex_output_file:
                        # read first 36 characters from hex output file line
                        guid_part = part_line[:36]
                        # check if assembly line GUID matches any GUID in hex output file
                        if guid_part == guid_assembly:
                            # set the flag to indicate that the GUID is valid
                            guid_valid = True
                            break
                    # check if current GUID in assembly is not valid
                    if not guid_valid:
                        # if any guid is not valid then the whole assembly is not valid
                        all_guids_valid = False
                        break
            # check if all GUIDs in the assembly are valid
            if all_guids_valid:
                # add the assembly name to the list of valid assemblies
                valid_assemblies.append(assembly_member_name)
                # write the last three characters of the assembly name to the file
                valid_assemblies_file.write(assembly_member_name[-3:] + '\n')
                # print message for clarity during execution
                print(f'GUIDs in assembly {dataset}({assembly_member_name}) valid.')
    # print successful execution message
    print(f"valid assemblies printed to 'valid_assemblies.txt'")

def find_valid_vehicles():
    # print message for clarity during execution
    print(f"finding valid vehicles..") 
    # create an empty list to store the data to be written to the output dataset
    output_data = []
    # loop over each input file
    for vehicle_member_name in datasets.list_members('ZXP.CONTEST.Q42021.SOURCE'):
        # check if the member does not start with 'PART' or 'ASM'
        if not (vehicle_member_name.startswith('PART') or vehicle_member_name.startswith('ASM')):
            # find ASCII name for vehicle member
            vehicle_name = bytearray.fromhex(vehicle_member_name).decode('cp500')
            # read all lines from the input file
            vehicle_lines = datasets.read(f"ZXP.CONTEST.Q42021.SOURCE({vehicle_member_name})").split("\n")
            # iterate over each line in the vehicle data
            for vehicle_line in vehicle_lines:
                # read first eight characters to get repetition codes
                repetition_codes = vehicle_line[:8]
                repetitions_assembly_1 = int(repetition_codes[:4])
                repetitions_assembly_2 = int(repetition_codes[4:])
                # read repeating assembly names
                vehicle_assemblies = []
                # iterate through the assemblies in vehicle_line. 8 characters then 3 per assembly
                for i in range(1, repetitions_assembly_1 + 1):
                    vehicle_assemblies.append(vehicle_line[8:8+3*i])
                for i in range(1, repetitions_assembly_2 + 1):
                    vehicle_assemblies.append(vehicle_line[(8+3*repetitions_assembly_1) + 3 * (i-1):(8+3*repetitions_assembly_1)+(3*i)]) # dont question it
                # check if the repetition codes allow for how many assemblies are present
                if (8 + (3 * repetitions_assembly_1) + (3 * repetitions_assembly_2)) != len(vehicle_line):
                    break
                # check if all assemblies in vehicle_assemblies are valid
                if are_all_assemblies_valid(vehicle_assemblies):
                    # add the data to the list to be written to the output dataset
                    output_data.append(f"{vehicle_name} {', '.join(vehicle_assemblies)}")
                    # print message for clarity during execution
                    print(f"Assemblies in vehicle {dataset}({vehicle_member_name}) valid.")
    # convert the list to a string with newline characters
    output_content = '\n'.join(output_data)
    # write the output data to the output dataset using datasets.write
    datasets.write(dataset_output_drop1, output_content)
    # print successful execution message
    print(F"valid vehicle names printed to {dataset_output_drop1}")
                    
def are_all_assemblies_valid(vehicle_assemblies):
    # read the content of the assemblies file
    with open(file_assemblies, 'r') as assemblies_file:
        # read lines and remove leading/trailing whitespaces
        valid_assemblies_list = [line.strip() for line in assemblies_file.readlines()]
    # check if all assemblies in vehicle_assemblies are present in the valid_assemblies_list
    return all(assembly in valid_assemblies_list for assembly in vehicle_assemblies)

if __name__ == "__main__":
    # initialise necessary variables
    dataset = 'ZXP.CONTEST.Q42021.SOURCE'
    dataset_output_drop1 = 'Z36434.OUTPUT(Q421DRP1)'
    part_members = ['PART\$2', 'PART\$5', 'PART\$G', 'PART\$Q', 'PART\$T']
    assembly_members = ['ASM@305', 'ASM@419','ASM@441','ASM@501','ASM@787','ASM@917']
    valid_assemblies = []
    valid_vehicles = []
    file_vendors_ascii = 'drop1_file_vendors_ascii.txt'
    file_vendors_hex = 'drop1_file_vendors_hex.txt'
    file_assemblies = 'drop1_file_assemblies.txt'

    # part 1 - find valid vendors
    find_valid_vendors()

    # part 2 - find valid assemblies
    find_valid_assemblies()

    # part 3 - find valid vehicles
    find_valid_vehicles()
