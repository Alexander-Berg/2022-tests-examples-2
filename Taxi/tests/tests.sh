#!/usr/bin/env bash

set -x
PWD=$(dirname $0)
$PWD/wait.sh billing-accounts || exit 1
$PWD/taxi-billing-accounts.sh || exit 1
