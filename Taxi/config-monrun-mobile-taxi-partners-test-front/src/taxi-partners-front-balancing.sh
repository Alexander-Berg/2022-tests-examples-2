#!/bin/bash

project=$1
action=$2

if [[ ${project} == '' ]] || [[ ${action} == '' ]]; then
    echo "You have to var/run this script as:"
    echo "$0 project action"
    echo "Projects can be: front, touch"
    echo "Actions can be: check, fclose, fopen, normal"
    exit 1
fi

if [[ ${project} == 'partners-front' ]]; then
    force_open_file="/var/run/partners-front-force-open";
    force_close_file="/var/run/partners-front-force-close";
    alive_file="/var/run/taxi-touch-alive";
    status=$(jhttp.sh -r m.taxi-partners.yandex.ru -n m.taxi-partners.yandex.ru -s https -p 443 -u /pong/ | cut -d \; -f 1)
fi

# probaly you should not change anything below this comment, beware
check () {
    if [[ -e ${force_open_file} ]]; then
        echo "1; ${service} force opened here"; return 0;
    fi

    if [[ -e ${force_close_file} ]]; then 
        echo "2; ${service} force closed here, rejecting"; 
        rm  ${alive_file} 2>/dev/null; return 1
    fi

    if [[ ${status} == '0' ]]; then 
        touch ${alive_file}; echo "0; ok"
    else 
        rm ${alive_file} 2>/dev/null; 
        echo "2; ${service} not runs here, rejecting"
        return 1;
    fi
}

fclose () {
    rm ${force_open_file} 2>/dev/null
    touch ${force_close_file}
}

fopen () {
    rm ${force_close_file} 2>/dev/null
    touch ${force_open_file}
}

normal () {
    rm ${force_close_file} 2>/dev/null
    rm ${force_open_file} 2>/dev/null
}
$2

