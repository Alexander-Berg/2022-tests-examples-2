#!/bin/bash
LAST_EXECUTABLE=ylast
OUTPUT_FILE=/opt/tmp/regression.txt
TESTED_OUTPUT=../ut_last/canondata/test.test_regression/regression.txt
$LAST_EXECUTABLE -V -c ./last.conf ./regression.xml 2>/dev/null | tail -n "+8" | head -n -6| grep -v -e "^Date: " -e "^Host: " -e "^Connection: " -e "^Server: " -e "^Content-Type: " -e "^X-Request-Id: " -e "^XRTIQ: " -e "^XRTIH: " >$OUTPUT_FILE
diff -uw $TESTED_OUTPUT $OUTPUT_FILE
ret=$?
if [ "$ret" != "0" ]; then
    echo "Test output (saved in $OUTPUT_FILE) differs from $TESTED_OUTPUT"
    exit $ret
else
    echo "Test successful, everything matches!"
fi
rm $OUTPUT_FILE
