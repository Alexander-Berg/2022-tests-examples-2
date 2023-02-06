# /bin/bash

# time measure. calculates and shows spent time
# usage:
# source $(base)/_time.sh
# timer_start t1
# sleep 3
# timer_finish t1
# timer_show t1
# 00:00:03

function timer_start() {
    local name_start=__t_a_${1}
    declare -g ${name_start}=$(date +'%s')
}

function timer_finish() {
    local name_start=__t_a_${1}
    local name_finish=__t_b_${1}
    local name_len=__t_n_${1}
    local name_len2=__t_s_${1}
    declare -g ${name_finish}=$(date +'%s')
    declare -g ${name_len}=$[ ${!name_finish} - ${!name_start} ]
    local tt=${!name_len}
    local ss=$[ ${tt} % 60 ]; tt=$[ ${tt} / 60 ]
    local mm=$[ ${tt} % 60 ]; tt=$[ ${tt} / 60 ]
    declare -g ${name_len2}=$(printf '%02d:%02d:%02d' ${tt} ${mm} ${ss})
}

function timer_show() {
    local name_len2=__t_s_${1}
    echo "${!name_len2}"
}

