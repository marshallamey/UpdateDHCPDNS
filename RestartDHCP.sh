#!/bin/bash
#
# Restart DHCP
#
if [ `whoami` != 'root' ]
then
    echo "You need to be root to do this!"
    exit 1
fi
#
echo "Copy configuration files"
scp -p dhcpd.master.conf root@zimbra:/etc/dhcp/
scp -p dhcpd.master.conf root@squid:/etc/dhcp/

echo "Restart DHCP zimbra"
ssh root@zimbra service isc-dhcp-server restart
sleep 3
ssh root@zimbra tail -30 /var/log/dhcp-server/dhcpd.log

echo "Restart DHCP squid"
ssh root@squid service isc-dhcp-server restart
sleep 3
ssh root@squid tail -30 /var/log/dhcp-server/dhcpd.log

