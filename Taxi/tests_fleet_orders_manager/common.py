MOCK_USER_TICKET = 'valid_user_ticket'
PARTNER_PASSPORT_UID = '54591353'
YA_TEAM_PASSPORT_UID = '63504250'
YA_USER_HEADERS = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': YA_TEAM_PASSPORT_UID,
}
YA_TEAM_USER_HEADERS = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Yandex-UID': PARTNER_PASSPORT_UID,
}
