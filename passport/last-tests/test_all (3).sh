#!/bin/bash
host_name=`hostname -f`
cd "$( dirname "${BASH_SOURCE[0]}" )"
ylast -j 6 -c last.conf -U localhost:10088 tvm*.xml -N 2>/dev/null
