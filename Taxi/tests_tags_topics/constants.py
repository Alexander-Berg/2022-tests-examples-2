# Generated via `tvmknife unittest service -s 300 -d 200 | fold -s50`
_TAGS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIrAIQyAE:KeWLY2L_lGAGzB7'
    'zanv1HQvjUyD4nTI7ddrXm-H2-uRV5nSfm4gkNpJJ9rZrCBtqt'
    'jUvKAbQ7ySEsHTB-bqfQvuv7lL3eFWbG3ib2JaYYudaaQMQfFe'
    'e_o_fVHU0x4fGGafeyDQGxYiTIRuFDtKUdAR2LKA0NL8EN8uer'
    'HE5l4o'
)

# Generated via `tvmknife unittest service -s 301 -d 200 | fold -s50`
_PASSENGER_TAGS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIrQIQyAE:D4ytaE7ZMnQzIsK'
    'UmX1NDwHYdGTJYawhmtBSvgSNRWQqnY41LrvSJFHdg8f0HKtUI'
    'MpnVfqV46fHK3s-BDZjXuHmZ_r88qbdUrjLLnHvqB45n9dm3fi'
    'c9mvfhDpQ0jrS4VAlEe2lkZQXZGK7_McB_4RMAgnpOlwVhyPTk'
    'dDVnbo'
)

# Generated via `tvmknife unittest service -s 303 -d 200 | fold -s50`
_GROCERY_TAGS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIrwIQyAE:LYyr6Ph15i7AnRT'
    'fwq2EDGdf5Ya9PFUmqV2x-91kMMBixwXLaZQNku-EFDx53-AoH'
    'QjnTUfSrtG2z7DGCY6WIYMngtSsaQhpFOwHgIjvDrB7zh8HUMK'
    'oS9hB45iFSPdXxkgAVR9yMONPi4KW32D460y0jBov3CC-6dT_4'
    'LzZCX4'
)

# Generated via `tvmknife unittest service -s 302 -d 200 | fold -s50`
_EATS_TAGS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIrgIQyAE:WroBNwsfmid6Yr7'
    'NE3BqVG57085jbM7SeRI6-Mn5pb-JvgG66QLl5rYUaTg3NANsC'
    'Agr57GfQvYoixnbiZhWdVc78DTLfSagHYtPVlI4IZraqZ9bcnA'
    'FLv4BqVOSB3Cfe34rQf6IOk1TkrvtGagdNU0goSL8TK6piaJ6S'
    'FwmFZE'
)

# Generated via `tvmknife unittest service -s 400 -d 200 | fold -w 50`
_UNKNOWN_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIkAMQyAE:VZL2YDV11jiTdwZ'
    'RqYgH3EUxu__7eTRG7kffQvQ1CjWQntfPtj2Bq-i1GTied0M3W'
    'zcrDw9SZZjc9Z3hwqDYvCpabCDM40W3NqFcuER3e4OVxOS46tU'
    'hK0VORz6hx_CPTGiK6AHHI-llFKRI_zuoQiJ2uREId6J_Rziff'
    'bkNzqM'
)


TICKET_HEADER = 'X-Ya-Service-Ticket'

TAGS_SERVICE = 'tags'
PASSENGER_TAGS_SERVICE = 'passenger-tags'
GROCERY_TAGS_SERVICE = 'grocery-tags'
EATS_TAGS_SERVICE = 'eats-tags'
UNKNOWN_SERVICE = 'unknown'

TICKETS_BY_SERVICE = {
    TAGS_SERVICE: _TAGS_SERVICE_TICKET,
    PASSENGER_TAGS_SERVICE: _PASSENGER_TAGS_SERVICE_TICKET,
    GROCERY_TAGS_SERVICE: _GROCERY_TAGS_SERVICE_TICKET,
    EATS_TAGS_SERVICE: _EATS_TAGS_SERVICE_TICKET,
    UNKNOWN_SERVICE: _UNKNOWN_SERVICE_TICKET,
}
