#!/bin/bash

set -e

function open_terminal() {
    title=$1
    command=$2
    platform="$(uname -s)"
    case "${platform}" in
        Linux*)     xterm -ls -xrm 'XTerm*selectToClipboard: true' -e "echo -e \"\033]0;$title\007\"; $command" &;;
        Darwin*)    osascript -e "tell application \"Terminal\" to do script \"cd $(pwd); $command\"";;
        *)          echo "Unsupported platform: $platform"; exit 1;
    esac
}

if [[ -z $1 ]];
then
    echo "You must specify uid"
    exit 1
fi

ya make api/bin

open_terminal "Api" "api/bin/takeout-api run development; read";

echo "Waiting until web-server is up..."
sleep 5

curl -X POST "http://127.0.0.1:5000/1/prepare_archive/?consumer=dev" -d "uid=$1&unixtime=$(date +%s)"
