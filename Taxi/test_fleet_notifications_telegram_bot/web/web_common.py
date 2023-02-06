PARTNER_PASSPORT_UID_1 = '54591353'


# `tvmknife unittest service --src 111 --dst 2016267`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCLiHs:NnLj18bjvNK1BNWUBc'
    'HKTNjeXkLh7xHowhQUxF7XjcFEibaG5NLaTCtH-eKcfY3PcTWMNue'
    'reDTyW2pm9N5-rCd_p-RZ_cyFqqH8rq0w7Sj_jnE1sKs3XuzK3IPm'
    'C83XNKspEYsr4u_KgWGQcV_gIXmpPcTunHD1l72MzqYk7yg'
)
MOCK_USER_TICKET = 'valid_user_ticket'
PARTNER_HEADERS_1 = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': PARTNER_PASSPORT_UID_1,
}


def make_headers(yandexuid=None):
    if yandexuid:
        PARTNER_HEADERS_1['X-Yandex-UID'] = yandexuid
    return PARTNER_HEADERS_1
