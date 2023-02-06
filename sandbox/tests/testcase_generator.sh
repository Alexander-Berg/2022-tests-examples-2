#!/usr/bin/env bash

python="$(which python)"
cproc="$python ../__init__.py"

echo "Generate reference data for testcases..."
rm data/*.html data/*.fp

$cproc || [ "$?" == "1" ]

# Test generic functionality
$cproc --version
$cproc -v

for i in data/test*.txt ; do
    echo "    Processing '$i' with coredump_filter"
    $cproc $i > $i.html
    # test fingerprints
    $cproc $i -f > $i.fp
done

echo "Done"
