#!/bin/sh
arc checkout trunk
arc pull

arc checkout -b testing/$VERSION

for i in $(arc pr list --label $LABEL | awk '{print $1}') ; do
    if [[ "$i" != "Id" ]]; then
        arc pr checkout $i
    fi
done
