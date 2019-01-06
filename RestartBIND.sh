#!/bin/bash
#
# Restart BIND
#
if [ `whoami` != 'root' ]
then
    echo "You need to be root to do this!"
    exit 1
fi
#
echo "Copy configuration files"
scp -p db.rdschool.org root@zimbra:/var/cache/bind/
scp -p db.10.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.1.168.192.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.2.168.192.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.3.168.192.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.4.168.192.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.7.168.192.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.8.168.192.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.9.168.192.in-addr.arpa root@zimbra:/var/cache/bind/
scp -p db.189.13.173.in-addr.arpa root@zimbra:/var/cache/bind/

echo "Restart BIND zimbra"
ssh root@zimbra service bind9 restart
sleep 3
ssh root@zimbra tail -30 /var/log/named/named.log
