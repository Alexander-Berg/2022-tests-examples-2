from . import (Data, LoginPrompt, ExpectLogin, LoginEcho, PasswordEcho, PasswordPrompt, ExpectPassword, USERNAME,
               PASSWORD, Motd, CommandPrompt, AuthError, MOCK_COMMAND, WriteCommandEcho, ExpectCommand,
               WriteErrorCommand, WriteCommand, AskQuestion, PasswordError)
HOSTNAME = b"sr-1s-test"
USERNAME = b"admin"

PROMPT_VARIANTS = [
    "\n[]\nA:admin@sr-1s-test# ",
    "\n[]\nA:monitor-nocauth@test# ",
    "[ro:configure router \"Base\"]\nA:admin@sr-1s-test# ",
    "*[pr:configure system lldp]\nA:admin@sr-1s-test# ",
    "!*[ro:/configure]\nA:gescheit@myt-32z4# ",  # ro mode
    "*[pr:/configure]\nA:korlatyanu-nocauth@lab-vla-32z2# ",
]

COMMAND_ERROR_VARIANTS = [
    b"                    ^^\nMINOR: MGMT_CORE #2201: Unknown element - 'tt'",
    b"                    ^^\nMINOR: CLI #2001: Missing element value - 'destination-address'",
    b"                    ^^\nMINOR: MGMT_AGENT #2005: Invalid element value - 'destination-address' could not transmit request to resolve \"8.8.8.87.7\"",
    b'MINOR: MGMT_CORE #224: configure policy-options policy-statement "PE_IMPORT_STOR_VRF" named-entry "DEFRAGMENTATORS" action as-path replace - Entry does not exist - configure policy-options as-path "(64998, 64998)"',

]

PAGER_VARIANTS = [
    b"\nPress Q to quit, Enter to print next line or any other key to print next page."
]
