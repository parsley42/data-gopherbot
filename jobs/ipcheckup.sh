#!/bin/bash -e

# jobs/ipcheckup.sh - check and maybe update route53 dns

source $GOPHER_INSTALLDIR/lib/gopherbot_v1.sh

#set -x

DNSIP=$(getent hosts portal.linuxjedi.org | awk '{print $1}')
REALIP=$(curl api.ipify.org)

if [ ! "$DNSIP" -o ! "$REALIP" ]
then
	echo "Unable to obtain DNS or REAL IP"
	exit 1
fi

echo "DNSIP is $DNSIP, REALIP is $REALIP."

if [ "$DNSIP" != "$REALIP" ]
then
	UPDATE=$(cat <<EOF
{
  "Comment": "Update portal DNS",
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "portal.linuxjedi.org",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{ "Value": "$REALIP" }]
    }
  }]
}
EOF
)
	echo "$UPDATE" | aws route53 change-resource-record-sets --hosted-zone-id Z1T8MQ9PA6SJNR --change-batch file:///dev/stdin
	Say "Updated DNS record, portal.linuxjedi.org -> $REALIP"
fi
