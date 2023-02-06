# tvmknife unittest service -s 111 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:NOJknuvn5r082stvLiaASO1AljvpT5r9gQ'
    'mxdanGuZAada_awqpYtIK1Ke1THWJZIN-EY2RKr90E0Jj21IOVBklwgkKswfqODqb4Wm'
    'Sz89KXpdKuOkmZbWqjhs_Y7lrVLfPJ-Wjd2TzcTnXyl7FnoTx_5UCa8pz_WVWFE1bCnQM'
)

# tvmknife unittest user -d 54591353 -e test --scopes read,write
DISPATCHER_USER_TICKET = (
    '3:user:CA0Q__________9_GiEKBQj5_oMaEPn-gxoaBHJlYWQaBXdyaXRlIN'
    'KF2MwEKAE:BKP9e6YK4ZP5vZa-DYW2p_43EwFjTKxnhyPPvaIQx35PZxbW5B9'
    'lO98FoeiW9MNIygxXy_248Le8nBNlkzXLz2LnrKnkb5H1lfpc2hP_JhZK9-id'
    '8NAbix3GhfO5guBSAxT-rB0iYQ0Sl6wgcoCn0vY-RRKhdMni36eU8rb_4dg'
)

# tvmknife unittest user -d 1120000000083978 -e prod_yateam --scopes read,write
SUPPORT_USER_TICKET = (
    '3:user:CAwQ__________9_GikKCQiKkJ2RpdT-ARCKkJ2RpdT-ARoEcmVhZBoFd'
    '3JpdGUg0oXYzAQoAg:PDx7DnqrAKf22PaztpPe0gaVU3SQ9CG3IfMxzVhkKy4LTW'
    'KC5Wh4D29FOgVdwxlOs5llzccbvraC0TM5p3Dd2zDP_ARfTH7PbyUjHEyuneYheE'
    'gPy7GSf-_hQeA-wIOl0_zU9bUWsKwulSQScWE2DL3sR8dN0On8kCIakOpsuf8'
)

DISPATCHER_UID = '54591353'
DISPATCHER_UID_PROVIDER = 'yandex'
DISPATCHER_CREATOR = {
    'uid': DISPATCHER_UID,
    'uid_provider': DISPATCHER_UID_PROVIDER,
}
DISPATCHER_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-User-Ticket': DISPATCHER_USER_TICKET,
    'X-Ya-User-Ticket-Provider': DISPATCHER_UID_PROVIDER,
    'X-Yandex-UID': DISPATCHER_UID,
}

SUPPORT_UID = '1120000000083978'
SUPPORT_UID_PROVIDER = 'yandex_team'
SUPPORT_CREATOR = {'uid': SUPPORT_UID, 'uid_provider': SUPPORT_UID_PROVIDER}
SUPPORT_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-User-Ticket': SUPPORT_USER_TICKET,
    'X-Ya-User-Ticket-Provider': SUPPORT_UID_PROVIDER,
    'X-Yandex-UID': SUPPORT_UID,
}

ADMIN_UID = '1120000000012345'
ADMIN_UID_PROVIDER = 'yandex_team'
ADMIN_CREATOR = {'uid': ADMIN_UID, 'uid_provider': ADMIN_UID_PROVIDER}
ADMIN_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': ADMIN_UID,
}

INTERNAL_HEADERS = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
