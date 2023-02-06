YA_TEAM_PASSPORT_UID = '63504250'

# `tvmknife unittest service --src 111 --dst 2024825`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxD5yns:WRHQq3LmrrjdLtaFsQ'
    'mkyhM9y8pMGuSnJXfCyUFCohJ8ANUPgH8AAhb0RNCiJJYk4z8ZDDU'
    'LoqBc-4p_sf7ARg3yPhASyX3TKbUG0ze3rCAr5EqKxxWYrdKHbdVF'
    'S4SN-vxeDKyaeKt-SJji2yZwl0GssOkVZdhGvIoC3AInpCA'
)
MOCK_USER_TICKET = 'valid_user_ticket'

YA_TEAM_HEADERS = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': YA_TEAM_PASSPORT_UID,
}
