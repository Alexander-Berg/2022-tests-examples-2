#!/usr/bin/env bash

SCRIPTFILE=bash_output.sh
. $SCRIPTFILE

test_ok() {
    output="$(json_output 'test' 1 'something went wrong')"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"WARN"
    assertContains "$output" "\"description\": \"something went wrong\""
    assertContains "$output" "\"tags\": []"
}

test_no_message() {
    output="$(json_output 'test' 0)"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK"
    assertContains "$output" "\"tags\": []"
}

test_one_tag() {
    output="$(json_output 'test' 0 'OK' 'all_good')"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": [\"all_good\"]"
}

test_three_tags() {
    output="$(json_output 'test' 0 'OK' 'all_good cool nice')"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": [\"all_good\", \"cool\", \"nice\"]"
}

test_no_tags_heat_sync() {
    output="$(json_output 'test' 0 'OK' '' 1)"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": [\"noc_heat\"]"
}

test_one_tag_heat_sync() {
    output="$(json_output 'test' 0 'OK' 'duty' 1)"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": [\"duty\", \"noc_heat\"]"
}

test_two_tags_heat_sync() {
    output="$(json_output 'test' 0 'OK' 'duty important' 1)"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": [\"duty\", \"important\", \"noc_heat\"]"
}

test_one_tag_and_it_s_num() {
    output="$(json_output 'test' 0 'OK' '9')"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": [\"9\"]"
}

test_some_tag_incorrect() {
    output="$(json_output 'test' 0 'OK' 'some 9 cool')"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": [\"some\", \"9\", \"cool\"]"
}

test_sync_to_heat_is_not_num() {
    output="$(json_output 'test' 0 'OK' '' 'z')"
    if ! echo "$output" | jq '.' > /dev/null; then
        fail "jq failed to parse result"
    fi
    assertContains "$output" "\"service\": \"test"
    assertContains "$output" "\"status\": \"OK"
    assertContains "$output" "\"description\": \"OK\""
    assertContains "$output" "\"tags\": []"
}

test_invalid_status() {
    res="$(json_output 'test' 8 2>&1)"
    assertContains "$res" "Invalid status"
}

## shunit2 not older than 2.1.7 required to be installed on your system
. shunit2
