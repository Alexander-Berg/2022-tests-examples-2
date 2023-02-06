#!/bin/bash
echo "learning KIV"
./scripts/matrixnet.pl -c ./etc/test/kiv-learn.json
echo "learning MSK"
./scripts/matrixnet.pl -c ./etc/test/msk-learn.json
echo "learning SPB"
./scripts/matrixnet.pl -c ./etc/test/spb-learn.json
echo "learnig done"

echo "testing KIV"
./scripts/matrixnet.pl -c ./etc/test/kiv-test.json
echo "testing MSK"
./scripts/matrixnet.pl -c ./etc/test/msk-test.json
echo "testing SPB"
./scripts/matrixnet.pl -c ./etc/test/spb-test.json
echo "testing done"
