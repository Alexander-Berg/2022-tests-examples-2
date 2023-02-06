#!/usr/local/bin/bash

set -e

export PATH=/bin:/usr/bin:/usr/local/bin:/Berkanavt/bin:/Berkanavt/gemini/bin:/Berkanavt/bin/scripts

master="sas-dev-gemini00.search.yandex.net"
gemini_list="sas-dev-gemini10.search.yandex.net sas-dev-gemini11.search.yandex.net sas-dev-gemini12.search.yandex.net sas-dev-gemini13.search.yandex.net sas-dev-gemini14.search.yandex.net sas-dev-gemini15.search.yandex.net"
walrus_list="walrus220 walrus580 walrus452 walrus167 walrus495 walrus604 walrus671 walrus393 walrus491 walrus031 walrus061 walrus559 walrus006 walrus378 walrus322 walrus603 walrus744 walrus683 walrus008 walrus044 walrus508 walrus055 walrus507 walrus470 walrus563 walrus040 walrus733 walrus742"
points="/Berkanavt/gemini/configs/global/points"


echo "MASTER $master"

for h in $gemini_list; do
    echo "GEMINI $h"
done

for h in $gemini_list; do
    m_points=$(gemini_lookup -m UsePoints -h ${h} -i $points -o /dev/stdout | awk '{print $1}' | sort -n | uniq | tr '\n' ' ')
    echo "SEGMENTED:$h $m_points"
done

for h in $gemini_list; do
    m_points=$(gemini_lookup -m UsePoints -h ${h} -R -i $points -o /dev/stdout | awk '{print $1}' | sort -n | uniq | tr '\n' ' ')
    echo "REPLICA:$h $m_points"
done

echo "MASTERWALRUS:$master $walrus_list"

