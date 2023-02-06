#!/bin/bash

TOKENS="e1de784094c94181aa8564096549bc84 AQABB_wAAAjbykUZhZIsTauD898asKRneg"
OUT_FILE=/tmp/oauth_test.log
EXPECTED=oauth_test.log

dns_name=`dnsdomainname`
host_name=`hostname`
URL=${host_name}.${dns_name}
cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "Testing OAuth response format" > $OUT_FILE

for token in $TOKENS; do
    REQUEST="http://$URL/blackbox?method=oauth&userip=1.2.3.4&oauth_token=${token}"
# xml
    echo "Request: " $REQUEST |tee -a $OUT_FILE
    wget -qO - $REQUEST >> $OUT_FILE
    echo >>$OUT_FILE
# json
    echo "Request: " $REQUEST |tee -a $OUT_FILE
    wget -qO - "${REQUEST}&format=json"|json_pp >> $OUT_FILE
    echo >>$OUT_FILE
done

diff -uw $EXPECTED $OUT_FILE
ret=$?

if [ $ret != "0" ]; then
    echo "TEST FAILED!"
    exit $ret
fi

echo -e "\nDone!"
