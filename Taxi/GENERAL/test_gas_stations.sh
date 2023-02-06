#!/bin/bash

PARK_ID=$1
XSERVICE_CALLBACK=$2 # example: '{"clid":"643753731112", "gas_general_contract_id":"10271994", "billing_client_id":"110017337", "limit":100, "skip_tanker_callback":true}'
PASSPORT_SESSION=$3 # Session_id cookie
 

read -p "Press enter to drop gas_stations contract"

curl "https://taximeter-admin.taxi.tst.yandex-team.ru/test/remove_gas_cabinet?db=$PARK_ID" -H "cookie: Session_id=$PASSPORT_SESSION"

echo ''

read -p "Go to dispatcher and accept gas stations offer. Press enter to emulate partner-contracts callback"

XSERVICE_TICKET=$(ya tool tvmknife get_service_ticket sshkey --src 2013636 --dst 2001830)

curl -X POST https://taximeter-xservice.taxi.tst.yandex.net/gas_stations/create_cabinet -H "Content-Type: application/json" -d "$XSERVICE_CALLBACK" -H "X-Ya-Service-Ticket: $XSERVICE_TICKET" -v

