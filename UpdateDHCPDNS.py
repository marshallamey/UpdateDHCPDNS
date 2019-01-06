#!/usr/bin/env python3 

"""
DHCP/DNS Update Script
Created by Marshall Amey
Technology Support Specialist
Redwood Day School
December 20, 2018

This script takes a .csv file exported from Filemaker Asset Management 
Database and generates all necessary files for DHCP and DNS

The filepath variable points to the directory that contains the templates 
folder and script

First, the script locates the serial number in each header template file and 
rewrites the file with an updated one.  The serial number is a 10 digit number 
with the format YYYYMMDDVV (Year, Mo, Day, Version).

Then, each template file is copied to the working directory with a new filename
and the inventory.csv file exported from FileMaker is reformatted to dhcpd.csv

Each device is added as a dictionary object to a list object that contains
the full inventory.  The list is sorted by ip address.

Next, all the files are opened and each device in the list is added to the 
appropriate file(s) based on its ip address.

Finally, any remaining necessary information is appended to the db.rdschool.org
file as a footer and all files are then closed.
"""

import re
import operator
import os
import csv
from datetime import date

# Absolute file path of working directory
filepath = '/Users/marshallamey/Projects/Work/DHCP/'
filenames = {
    'dhcp': 'dhcpd.master.conf',
    'fdns': 'db.rdschool.org',
    '0': 'db.189.13.173.in-addr.arpa',
    '1': 'db.1.168.192.in-addr.arpa',
    '2': 'db.2.168.192.in-addr.arpa',
    '3': 'db.3.168.192.in-addr.arpa',
    '4': 'db.4.168.192.in-addr.arpa',
    '7': 'db.7.168.192.in-addr.arpa',
    '8': 'db.8.168.192.in-addr.arpa',
    '9': 'db.9.168.192.in-addr.arpa',
    '10': 'db.10.in-addr.arpa',
}

d = date.today()
currentYear = d.year
currentMonth = d.month
currentDay = d.day

## UPDATE HEADER TEMPLATES
# For each header template with a serial number...
for filename in filenames.values():
    # Open the file
    file = open(f'{filepath}templates/header.{filename}', 'r+')
    header = file.read()
    print(f'Opening file:: {filepath}templates/header.{filename}')

    # Find the file serial number
    serial = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})', header)
    if not serial:
        print(f'No serial number in this file!')
        file.close()
        continue
    print(f'Found old serial number:: {serial[0]}')
    prevYear = int(serial[1])
    prevMonth= int(serial[2])
    prevDay = int(serial[3])
    prevVersion = int(serial[4])

    # Update the serial number
    # If current and previous dates are the same...
    if currentYear == prevYear and currentMonth == prevMonth and currentDay == prevDay:
        # Increment version number by 1 and replace serial
        currentVersion = prevVersion + 1
        newSerial = f'{currentYear:04d}{currentMonth:02d}{currentDay:02d}{currentVersion:02d}'
        print(f'Creating new serial number:: {newSerial}')
        newHeader = re.sub(r'\d{10}', newSerial, header, 1)        
    else:
        # Else replace serial with current date
        newSerial = f'{currentYear:04d}{currentMonth:02d}{currentDay:02d}00'
        print(f'Creating new serial number:: {newSerial}')
        newHeader = re.sub(r'\d{10}', newSerial, header, 1)

    # Overwrite the template file with new serial
    file.seek(0)
    file.truncate() 
    file.write(newHeader)  
    file.close()

## CREATE FILES
print('Copying header files to working directory...')
from shutil import copyfile
for file in os.listdir(f'{filepath}templates'):
    newName = re.match(r'header.(.*)', file)
    if newName:
        # Copy template file and remove header prefix in name
        copyfile(os.path.join(f'{filepath}templates/', file), os.path.join(f'{filepath}', file))
        os.rename(os.path.join(f'{filepath}', file), os.path.join(f'{filepath}', newName.group(1)))
        print(f'New file created:: {filepath}{newName.group(1)}')

# Create a list to hold all devices in the inventory.csv file
with open(f'{filepath}inventory.csv') as f:
    devices = f.read()
with open(f'{filepath}dhcpd.csv', 'a') as f:
    f.write(devices)
inventory = []

# For every device in dhcpd.csv file...
inputCSV = csv.DictReader(open(f'{filepath}dhcpd.csv'))
for row in inputCSV:
    # Extract device data and add to inventory as a dictionary entry
    if row['device']:
        inventory.append({ 
            'deviceName': row['device'], 
            'macAddress': row['mac'], 
            'ipAddress': row['ip'] 
        })
    if row['deviceWL']:
        inventory.append({ 
            'deviceName': row['deviceWL'], 
            'macAddress': row['macWL'], 
            'ipAddress': row['ipWL'] 
        })

# Sort inventory list by IP address
inventory.sort(key=operator.itemgetter('ipAddress'))

## OPEN FILES
files = {}
for key, filename in filenames.items():
    files[key] = open(f'{filepath}{filename}', 'a')
print('Adding devices to files...')

## UPDATE FILES
prevIP2 = 'aaa'
prevIP3 = 'aaa'
prevIP4 = 'aaa'
for device in inventory:

    # Parse ip address for sorting/formatting 
    ip = re.match(r'(\d\d\d).(\d\d\d).(\d\d\d).(\d\d\d)', device['ipAddress'])
    ip1 = int(ip.group(1))
    ip2 = int(ip.group(2))
    ip3 = int(ip.group(3))
    ip4 = int(ip.group(4))

    # Add device to dhcpd.master.conf   
    files['dhcp'].write(f"host {device['deviceName']:30} {{ hardware ethernet  {device['macAddress']}; fixed-address  {ip1}.{ip2}.{ip3}.{ip4}; }}\n")
    
    # Add device to db.rdschool.org
    files['fdns'].write(f"{device['deviceName']:30} IN \t A \t\t {ip1}.{ip2}.{ip3}.{ip4}\n")
    
    # Add device to appropriate reverse DNS file
    if ip:
        # For 198.162.xxx.xxx addresses
        if ip1 == 192 and ip2 == 168:
            # Add new $ORIGIN header if the address category changes
            if (ip3 != prevIP3 or (ip3 == prevIP3 and ip2 != prevIP2)):
                files[str(ip3)].write(f"\n$ORIGIN {ip3}.{ip2}.{ip1}.in-addr.arpa.\n")
            # Add device if IP is not a duplicate
            if (ip4 != prevIP4 or ip3 != prevIP3 or ip2 != prevIP2):
                files[str(ip3)].write(f"{ip4:<10} IN \t PTR \t\t {device['deviceName']}.rdschool.org.\n")

        # For 10.xxx.xxx.xxx addresses
        if ip1 == 10:
            # Add new $ORIGIN header if the address category changes
            if (ip3 != prevIP3 or (ip3 == prevIP3 and ip2 != prevIP2)):
                files[str(ip1)].write(f"\n$ORIGIN {ip3}.{ip2}.{ip1}.in-addr.arpa.\n")
            # Add device if IP is not a duplicate
            if (ip4 != prevIP4 or ip3 != prevIP3 or ip2 != prevIP2):
                files[str(ip1)].write(f"{ip4:<10} IN \t PTR \t\t {device['deviceName']}.rdschool.org.\n")

        # Replace previous IP address        
        prevIP2 = ip2
        prevIP3 = ip3
        prevIP4 = ip4

# Add footer to db.rdschool.org
with open(f'{filepath}templates/footer.db.rdschool.org') as f:
    footer = f.read()
    files['fdns'].write(footer)        

## CLOSE FILES
for file in files:
    files[file].close()
print(f'Files completed. Added {len(inventory)} devices')