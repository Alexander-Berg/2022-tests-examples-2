#!/bin/bash
echo 'start...'

for i in {85000..99999}
do
    echo "download $i"
    BULKAURL="http://bulca-www.feeds.yandex.net:10020/rss-widget?limit=1000&feed_id=$i"
    SERVURL="http://localhost:9999/feeds/store/?feed_id=$i"
    curl --silent $BULKAURL | curl --silent -X POST --data-binary @- $SERVURL
done

