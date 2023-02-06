#!/bin/bash

>&2 echo "Don't forget to update dbid and uuid"
TVM_TIKET="$(ya tool tvmknife get_service_ticket sshkey --dst 2035593 --src 2013636)"

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
AMMO_DIR="$( realpath $SCRIPT_DIR/../ammo)";

>&2 echo "Ammo dir is: $AMMO_DIR"

# set this variable if you want to generate ammo instead
if [ "x$1" == "xammo" ]; then
>&2 echo "Generating ammo"
GEN_AMMO=../../scripts/generate_ammo_file.py
fi;

$GEN_AMMO curl -v \
  -H  'Host: contractor-fts-receiver.taxi.yandex.net' \
  -H "Content-Type: application/json" \
  -H "X-Ya-Service-Ticket: $TVM_TIKET" \
  -H "User-Agent: Taximeter 9.1 (1234)" \
  -H "X-Request-Application-Version: 9.1" \
  -H "X-YaTaxi-Park-Id: 7ad36bc7560449998acbe2c57a75c293" \
  -H "X-YaTaxi-Driver-Profile-Id: eb785a5cdf6a27cf1e4f9944bb5168f2" \
  -d "@$AMMO_DIR/one_contractor_multipos.json" \
  meqx6s4edfavnj4l.sas.yp-c.yandex.net/driver/v1/position/store
