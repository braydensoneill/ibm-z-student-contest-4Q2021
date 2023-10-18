import csv
import re
import requests
import sys, os
import codecs
from zoautil_py import datasets

def get_webpage(_link):
    # print message for clarity during execution
    print(f"Request page from link {_link}")

    # request page url
    page = requests.get(_link).text

    # end of function
    return page

def get_mapper(_webpage):
    # get mapper URL
    mapper = sorted(re.findall(r"data-z\[(.*)'", _webpage))
    mapper = [l[4:] for l in mapper]
    mapper[1] = ":" + mapper[1]
    mapper = ''.join(mapper)

    # print message for clarity during execution
    print(f"Mapper found")

    # end of function
    return mapper

def get_mapper_values(_mapper_json):
    for i in _mapper_json:
        if i['type'] == 'locator converter':
            locator = f"{i['url']['protocol']}://{i['url']['host']}:{i['url']['port']}{i['url']['path']}"
        elif i['type'] == 'address converter':
            address = f"{i['url']['protocol']}://{i['url']['host']}:{i['url']['port']}{i['url']['path']}"
        elif i['type'] == 'service details':
            service = f"{i['url']['protocol']}://{i['url']['host']}:{i['url']['port']}{i['url']['path']}"

    # print message for clarity during execution
    print(f"Parsed mapper_json data")

    # end of function
    return service, address, locator

def write_to_files():
    # get header info
    host, platform, os = get_header_values(service_details)

    # get location info
    location_list = get_location_values()
    
    # write header lines
    file_header = open(file_path_header, 'w')
    file_header.write(f"host:{str(host)} platform: {str(platform)} os: {str(os)}\n")
    file_header.write(f"{str(north)},{str(west)} {str(south)},{str(east)}\n")
    file_header.close()
    print(f"Data written to {file_path_header}")

    # write location lines
    file_location = open(file_path_location, 'w')
    file_location.write(''.join(location_list))
    file_location.close()
    print(f"Data written to {file_path_location}")

    # end of function
    return

def get_header_values(_service_details):
    # extract information from service details
    host = re.findall(r"<dt>Host<\/dt>\n[ \t]*<dd>(.*)<\/dd>", _service_details)[0]
    platform = re.findall(r"<dt>Platform<\/dt>\n[ \t]*<dd>(.*)<\/dd>", _service_details)[0]
    os = re.findall(r"<dt>OS<\/dt>\n[ \t]*<dd>(.*)<\/dd>", _service_details)[0]

    # end of function
    return host, platform, os

def get_location_values():
    record_list = []

    # read output from Drop3 and sort them in ascending order based on name
    with open(file_path_records) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        sorted_reader = sorted(list(csv_reader), key=lambda row: row[4])

        # add each formatted record to the list
        for field in sorted_reader:
            id, name, location = field[2:]
            latitude,longitude = process_csv_record(location)
            
            record = f"{str(id)},\"{str(name)}\",\"{str(location)}\",{str(latitude)},{str(longitude)}\n"
            record_list.append(record)

            print(record)

    #end of function
    return record_list

def process_csv_record(_location):
    global north, south, west, east

    addr_code = requests.get(locator.replace("{locator}", _location)).json()["address"]
    lat_long = requests.get(address.replace("{address}", addr_code)).json()
    latitude = lat_long["lat"]
    longitude = lat_long["lng"]

    if latitude is not None and longitude is not None:
        # set bounding box
        north = max(north, latitude) if north is not None else latitude
        south = min(south, latitude) if south is not None else latitude
        west = min(west, longitude) if west is not None else longitude
        east = max(east, longitude) if east is not None else longitude

    # end of function
    return latitude, longitude

def write_files_to_output_file(_file_path_header, _file_path_location, _file_path_output):
    # open the file to write to
    file_output = open(_file_path_output, 'w')

    # open the input file
    with open(_file_path_header, 'r') as file_header:
        # loop through all the sorted lines with an index
        for line in file_header:
            # for the first line, do not append so that you start with a fresh file, [:-1] to ignore the \n
            file_output.write(line)

    with open(_file_path_location, 'r') as file_location:
        # loop through all the sorted lines with an index
        for line in file_location:
            # for the first line, do not append so that you start with a fresh file, [:-1] to ignore the \n
            file_output.write(line)

    # print message for clarity during execution
    print(f"{_file_path_header} and {_file_path_location} combined to {_file_path_output}")        

    # end of function
    return

def write_output_file_to_dataset(_file_in, _dataset_out):
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
    # set file paths
    file_path_records = "drop3_file_records.txt"
    file_path_header = "drop4_file_header.txt"
    file_path_location = "drop4_file_location.txt"
    file_path_output = "drop4_file_output.txt"
    dataset_path_output = "Z36434.OUTPUT(Q421DRP4)"

    # set necessary variable defaults
    link = "http://192.86.32.12:5081/vehicles"
    service = address = locator = ""
    north = south = west = east = None
    location_list = []

    # get page
    webpage = get_webpage(link)

    # get mapper JSON
    mapper_json = requests.get(get_mapper(webpage)).json()

    # get service, address, locator from mapper json
    service, address, locator = get_mapper_values(mapper_json)

    # get HTML of service details
    service_details = requests.get(service).text

    # write to header,location files
    write_to_files()

    # write data from files to output file
    write_files_to_output_file(file_path_header, file_path_location, file_path_output)

    # write the final output to the output dataset
    write_output_file_to_dataset(file_path_output, dataset_path_output)

