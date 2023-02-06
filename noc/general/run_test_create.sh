#!/bin/sh

set -e

ya make
./conductor_ticket_create run ConductorTicketCreate --input "$(cat example_manual.json)" --local
echo
