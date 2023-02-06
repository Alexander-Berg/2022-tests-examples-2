# tvmknife unittest service -s 111 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:'
    'G4hKvC1tY887M0UUAjj13gJEnzikFS9z9so'
    'b0laeFmJ4JVL0XDyNZtWBu4ZjKf9O_juLZg'
    'hRptbnyiQRqoiBsX1eXLdABRLpdJpAxLY4d'
    'fVOD0o8GEQ7q94GH0uLQOV_POubrySzzMgN'
    'gRFhn_CwXjrfZRziFuk-RV0I-zzTsE4'
)

USER_TICKET = 'ticket_valid'
UID = '100'
EMAIL = 'user@yandex.ru'


def build_headers(
        uid=UID,
        provider='yandex',
        user_ticket=USER_TICKET,
        park_id=None,
        accept_language=None,
):
    headers = {
        'X-Yandex-UID': uid,
        'X-Ya-User-Ticket-Provider': provider,
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': user_ticket,
    }
    if park_id is not None:
        headers['X-Park-Id'] = park_id
    if accept_language is not None:
        headers['Accept-Language'] = accept_language
    return headers
