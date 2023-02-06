#!/bin/bash
# this script installs osquery-yandex-generic-config and runs it under different tags.
# then checks packs, cpu and ram listed in the tags array.

osquery_packet="osquery-yandex-generic-config"
decorator_file='/etc/osquery/osquery.conf.d/51_decorator.conf'
packs_file='/etc/osquery/osquery.conf.d/60_packs.conf'
tag_file='/etc/osquery.tag'
flags_file='/etc/osquery/osquery.flags'

declare -a tags
tags[0]='ycloud-hv-config;0;512;bastion,selinux,file_operations,file_integrity'
tags[1]='ycloud-mdb-ch-config;1;50;selinux,file_operations,file_integrity'
tags[2]='ycloud-mdb-mg-config;1;50;selinux,file_operations,file_integrity'
tags[3]='ycloud-mdb-mysql-config;1;50;selinux,file_operations,file_integrity'
tags[4]='ycloud-mdb-pg-config;1;50;selinux,file_operations,file_integrity'
tags[5]='ycloud-mdb-rd-config;0;512;selinux,file_operations,file_integrity'
tags[6]='ycloud-mdb-zookeeper-config;1;50;selinux,file_operations,file_integrity'
tags[7]='ycloud-svc-apigw-config;0;512;file_integrity'
tags[8]='ycloud-svc-bastion-config;0;512;file_integrity'
tags[9]='ycloud-svc-billing-config;0;512;file_integrity'
tags[10]='ycloud-svc-cgw-config;0;512;file_integrity'
tags[11]='ycloud-svc-generic-config;0;512;file_integrity'
tags[12]='ycloud-svc-iam-config;0;512;bastion'
tags[13]='ycloud-svc-kikimrdn-config;0;512;file_integrity'
tags[14]='ycloud-svc-kikimruydb-config;1;50;'
tags[15]='ycloud-svc-lb-config;0;512;file_integrity'
tags[16]='ycloud-svc-mrkt-config;0;512;file_integrity'
tags[17]='ycloud-svc-oct-config;0;512;file_integrity'
tags[18]='ycloud-svc-serialssh-config;0;512;selinux,file_integrity'
tags[19]='ycloud-svc-snapshot-config;0;512;file_integrity'
tags[20]='ycloud-svc-solomon-config;0;512;file_integrity'
tags[21]='ycloud-svc-sqs-config;0;512;selinux,file_integrity'
tags[22]='ycloud-svc-yql-prod-config;0;512;selinux,file_operations'
tags[23]='yandex-bu-afisha-config;0;512;file_operations_afisha,file_integrity_afisha'
tags[24]='broken_tag;1;50;'
tags[25]='ycloud-svc-undefined-conf;1;50;'
tags[26]='ycloud-mdb-undefined-conf;1;50;'
tags[27]='ycloud-svc-apiadapter-config;0;512;file_integrity'
tags[28]='ycloud-svc-slbadapter-config;0;512;file_integrity'
tags[29]='yandex-bu-undefined-conf;0;512;'
tags[30]='ycloud-svc-s3-config;0;512;selinux'
tags[31]='ycloud-svc-yql-preprod-config;0;512;selinux,file_operations'
tags[32]='ycloud-mdb-k8master-config;1;50;selinux'
tags[33]='ycloud-hv-seccomp-config;0;512;bastion,selinux,file_operations,file_integrity'
tags[34]='yandex-passport-jump-config;0;512;'
tags[35]='ycloud-hv-head-config;0;512;'
tags[36]='ycloud-hv-seed-config;0;512;'
tags[37]='ycloud-svc-netinfra-config;0;512'

for i in "${tags[@]}"
do
    arr=(${i//;/ })
    echo ${arr[0]}
    echo ${arr[0]} > $tag_file
    apt install -y $osquery_packet >/dev/null 2>&1 
    # echo 1 if the decrator file content == current tag
    cat $decorator_file | grep -i ycloud | awk -F"'" -v arg1="${arr[0]}" '{ print $2 == arg1 }'
    # echo 1 if cpu and memory levels == needed for the current tag
    cat $flags_file | grep -i 'watchdog_level=' | awk -F"=" -v arg1="${arr[1]}" '{ print $2 == arg1 }'
    cat $flags_file | grep -i 'watchdog_memory_limit=' | awk -F"=" -v arg1="${arr[2]}" '{ print $2 == arg1 }'
    # echo 1 if packs are in the file
    arr1=(${arr[3]//,/ })
    for j in "${arr1[@]}"
    do
        cat $packs_file | grep -ci ${j}
    done
    osqueryctl config-check 2>&1| grep -i error

apt purge -y $osquery_packet >/dev/null 2>&1
done
