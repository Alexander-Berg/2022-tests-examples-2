#!/bin/bash
host_name=`hostname -f`
cd "$( dirname "${BASH_SOURCE[0]}" )"
ylast -j 6 -c last.conf -U https://${host_name} blackbox*.xml $1 2>/dev/null
