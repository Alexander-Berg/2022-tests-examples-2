# tvmknife unittest service -s 111 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:'
    'G4hKvC1tY887M0UUAjj13gJEnzikFS9z9so'
    'b0laeFmJ4JVL0XDyNZtWBu4ZjKf9O_juLZg'
    'hRptbnyiQRqoiBsX1eXLdABRLpdJpAxLY4d'
    'fVOD0o8GEQ7q94GH0uLQOV_POubrySzzMgN'
    'gRFhn_CwXjrfZRziFuk-RV0I-zzTsE4'
)

SERVICE_HEADERS = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}

FILE_DATA = bytes('file_string_data', encoding='utf-8')


def build_fleet_headers(
        park_id,
        accept_language='ru',
        idempotency_token=None,
        content_type=None,
):
    headers = {
        **SERVICE_HEADERS,
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
        'Accept-Language': accept_language,
    }
    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token
    if content_type is not None:
        headers['Content-Type'] = content_type
    return headers


def build_taximeter_headers(park_id, driver_id):
    return {
        'User-Agent': 'Taximeter 8.90 (228)',
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '8.90',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
    }
