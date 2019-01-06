#!/bin/bash

# Run python script
python3 UpdateDHCPDNS.py

# Update servers
./RestartBIND.sh
./RestartDHCP.sh