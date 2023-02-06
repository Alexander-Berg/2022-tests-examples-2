#!/usr/bin/env bash

SCRIPTFILE=module_parameters.sh
TMPDIR=/tmp/module_parameters_test
TMP_INTERFACE_FILE=/tmp/dummy_interfaces

oneTimeSetUp() {
    mkdir -p "$TMPDIR"
}

oneTimeTearDown() {
    rm -rf "$TMPDIR"
    rm -f "$TMP_INTERFACE_FILE"
}

tearDown() {
    rm -rf "$TMPDIR"
    mkdir -p "$TMPDIR"
    rm -f "$TMP_INTERFACE_FILE"
}

gen_interface_file() {
    local length="$1"
    local name="$2"
    for i in $(seq 1 "$length"); do
        echo "$i: $name$i: <BROADCAST,NOARP> mtu 1500 qdisc noop state DOWN mode DEFAULT group default qlen 1000" >> "$TMP_INTERFACE_FILE"
    done
}

ip() {
    cat "$TMP_INTERFACE_FILE"
}

test_check_name() {
    touch "$TMP_INTERFACE_FILE"
    assertContains "$(. $SCRIPTFILE)" "module_parameters"
}

test_incorrect_dummy_value() {
    touch "$TMP_INTERFACE_FILE"
    assertContains "$(. $SCRIPTFILE -d dummy -v zzz)" "is incorrect value to check"
}

test_less_dummies() {
    num_dummies=64
    gen_interface_file "$num_dummies" 'dummy'
    assertContains "$(. $SCRIPTFILE -d dummy -v 256)" "not equal to 256"
}

test_more_dummies() {
    num_dummies=280
    gen_interface_file "$num_dummies" 'dummy'
    assertContains "$(. $SCRIPTFILE -d dummy -v 256)" "not equal to 256"
}

test_ok_dummies() {
    num_dummies=256
    gen_interface_file "$num_dummies" 'dummy'
    assertNull "$(. $SCRIPTFILE -d dummy -v 256)"
}

test_ipvs_random_dir() {
    SOMEDIR=/tmp/somedir_test_354
    mkdir "$SOMEDIR"
    assertContains "$(. $SCRIPTFILE -d ipvs -v $SOMEDIR)" "source randomization is not enabled"
    rm -rf "$SOMEDIR"
}

test_ipvs_random_switch_not_exist() {
    echo zzz > "$TMPDIR/random_source_network"
    assertContains "$(. $SCRIPTFILE -d ipvs -v $TMPDIR)" "source randomization is not enabled"
}

test_ipvs_random_source_not_exist() {
    echo 0 > "$TMPDIR/random_source"
    assertContains "$(. $SCRIPTFILE -d ipvs -v $TMPDIR)" "invalid source randomization prefix"
}

test_ipvs_random_source_not_enabled() {
    echo 0 > "$TMPDIR/random_source"
    echo 2a02:6b8:6666:: > "$TMPDIR/random_source_network"
    assertContains "$(. $SCRIPTFILE -d ipvs -v $TMPDIR)" "source randomization is not enabled"
}

test_ipvs_random_source_network_incorrect() {
    echo 1 > "$TMPDIR/random_source"
    echo zzz > "$TMPDIR/random_source_network"
    assertContains "$(. $SCRIPTFILE -d ipvs -v $TMPDIR)" "invalid source randomization prefix"
}

test_ipvs_random_source_network_not_good() {
    echo 1 > "$TMPDIR/random_source"
    echo 2a02:6b8:9999:: > "$TMPDIR/random_source_network"
    assertContains "$(. $SCRIPTFILE -d ipvs -v $TMPDIR)" "invalid source randomization prefix"
}

test_ipvs_random_source_good() {
    echo 1 > "$TMPDIR/random_source"
    echo 2a02:6b8:6666:: > "$TMPDIR/random_source_network"
    assertNull "$(. $SCRIPTFILE -d ipvs -v $TMPDIR)"
}

test_governor_no_files() {
    for i in {0..15}; do
        mkdir -p "$TMPDIR/cpu$i"
    done
    assertContains "$(. $SCRIPTFILE -d governor -v $TMPDIR)" "scaling governor parameters not exist"
}

test_governor_all_not_in_performance() {
    for i in {0..15}; do
        mkdir -p "$TMPDIR/cpu$i/cpufreq"
        echo "powersave" > "$TMPDIR/cpu$i/cpufreq/scaling_governor"
    done
    assertContains "$(. $SCRIPTFILE -d governor -v $TMPDIR)" "scaling governor is not performance"
}

test_governor_not_all_in_performance() {
    for i in {0..15}; do
        mkdir -p "$TMPDIR/cpu$i/cpufreq"
        echo "powersave" > "$TMPDIR/cpu$i/cpufreq/scaling_governor"
    done
    echo "performance" > "$TMPDIR/cpu5/cpufreq/scaling_governor"
    echo "performance" > "$TMPDIR/cpu12/cpufreq/scaling_governor"
    assertContains "$(. $SCRIPTFILE -d governor -v $TMPDIR)" "scaling governor is not performance"
}

test_governor_good() {
    for i in {0..15}; do
        mkdir -p "$TMPDIR/cpu$i/cpufreq"
        echo "performance" > "$TMPDIR/cpu$i/cpufreq/scaling_governor"
    done
    assertNull "$(. $SCRIPTFILE -d governor -v $TMPDIR)"
}

test_iface_less_interfaces() {
    num_ifaces=3
    gen_interface_file "$num_ifaces" 'eth'
    echo "00:99.0 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" > "$TMPDIR/iface"
    echo "00:99.1 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" >> "$TMPDIR/iface"
    echo "00:98.0 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" >> "$TMPDIR/iface"
    echo "00:98.1 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" >> "$TMPDIR/iface"
    assertContains "$(. $SCRIPTFILE -d iface -v "$TMPDIR/iface")" "number of eth interfaces less than"
}

test_iface_more_interfaces() {
    num_ifaces=3
    gen_interface_file "$num_ifaces" 'eth'
    echo "00:99.0 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" > "$TMPDIR/iface"
    echo "00:99.1 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" >> "$TMPDIR/iface"
    assertContains "$(. $SCRIPTFILE -d iface -v "$TMPDIR/iface")" "number of eth interfaces more than"
}

test_iface_ok() {
    num_ifaces=2
    gen_interface_file "$num_ifaces" 'eth'
    echo "00:99.0 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" > "$TMPDIR/iface"
    echo "00:99.1 Ethernet controller: Intel 82540EM Gigabit Ethernet Controller" >> "$TMPDIR/iface"
    assertNull "$(. $SCRIPTFILE -d iface -v "$TMPDIR/iface")"
}

test_iface_chelsio() {
    # check that we ignore Chelsio cards, assuming there are no associated eth interfaces
    # at the moment you can look at man1-lb1a for an example
    num_ifaces=3
    gen_interface_file "$num_ifaces" 'eth'
    echo "02:00.0 Ethernet controller: Intel Corporation I350 Gigabit Network" > "$TMPDIR/iface"
    echo "02:00.1 Ethernet controller: Intel Corporation I350 Gigabit Network" >> "$TMPDIR/iface"
    echo "04:00.0 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+" >> "$TMPDIR/iface"
    echo "08:00.0 Ethernet controller: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "	Subsystem: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "08:00.1 Ethernet controller: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "	Subsystem: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "08:00.2 Ethernet controller: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "	Subsystem: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "08:00.3 Ethernet controller: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "	Subsystem: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "08:00.4 Ethernet controller: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    echo "	Subsystem: Chelsio Inc T580-SO-CR Ethernet Controller" >> "$TMPDIR/iface"
    assertNull "$(. $SCRIPTFILE -d iface -v "$TMPDIR/iface")"
}

## shunit2 not older than 2.1.7 required to be installed on your system
. shunit2
