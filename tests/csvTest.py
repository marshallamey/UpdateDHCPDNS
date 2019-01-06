#!/usr/bin/env python3 
"""  
Verify the results of Filemaker Pro csv export
""" 
import re
import csv

inputCSV = csv.DictReader(open('./dhcpd.csv'))

for row in inputCSV:
    print(row)
    print('\n')
