#!/usr/bin/env bash

SCRIPTFILE=power_status.sh
IPMITOOL_RESULT_OK='PS1 Status       | C8h | ok  | 10.88 | Presence detected\nPS2 Status       | C9h | ok  | 10.87 | Presence detected'
IPMITOOL_RESULT_NOK='PS1 Status       | C8h | ok  | 10.88 | Presence detected\nPS2 Status       | C9h | ok  | 10.87 | Presence detected, Failure detected'
IPMITOOL_RESULT_LOSS='PS1 Status       | C8h | ok  | 10.88 | Presence detected, Failure detected, Power Supply AC lost\nPS2 Status       | C9h | ok  | 10.87 | Presence detected'
IPMITOOL_RESULT_FAIL='Could not open device'

test_power_ok() {
    source "$SCRIPTFILE"
    unset ipmi_dev_exists
    ipmi_dev_exists() {
        return 0
    }
    sudo() {
        echo -e "$IPMITOOL_RESULT_OK"
    }
    result="$(power_check)"
    assertContains "$result" "power_status"
    assertContains "$result" "\"status\": \"OK"
    assertContains "$result" "\"description\": \"OK"
}

test_power_nok() {
    source "$SCRIPTFILE"
    unset ipmi_dev_exists
    ipmi_dev_exists() {
        return 0
    }
    sudo() {
        echo -e "$IPMITOOL_RESULT_NOK"
    }
    result="$(power_check)"
    assertContains "$result" "Failure detected"
}

test_power_no_ac() {
    source "$SCRIPTFILE"
    unset ipmi_dev_exists
    ipmi_dev_exists() {
        return 0
    }
    sudo() {
        echo -e "$IPMITOOL_RESULT_LOSS"
    }
    result="$(power_check)"
    assertContains "$result" "AC lost"
}

test_power_no_ipmi() {
    source "$SCRIPTFILE"
    unset ipmi_dev_exists
    ipmi_dev_exists() {
        return 1
    }
    sudo() {
        echo -e "$IPMITOOL_RESULT_OK"
    }
    result="$(power_check)"
    assertContains "$result" "no IPMI device found"
}

test_power_command_fail() {
    source "$SCRIPTFILE"
    unset ipmi_dev_exists
    ipmi_dev_exists() {
        return 0
    }
    sudo() {
        echo -e "$IPMITOOL_RESULT_FAIL"
    }
    result="$(power_check)"
    assertContains "$result" "could not open IPMI"
}

# shunit2 not older than 2.1.7 required to be installed on your system
. shunit2
