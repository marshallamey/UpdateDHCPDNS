This script takes a .csv inventory file exported from the Filemaker Pro Asset Management 
Database and generates all necessary files for updating DHCP and DNS

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

# Usage

Once the .csv file has been exported to the working directory, start the script:
`
sudo ./StartDHCPUpdate.sh
`