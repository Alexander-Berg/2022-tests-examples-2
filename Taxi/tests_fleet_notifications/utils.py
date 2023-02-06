FEEDS_CREATE_ENDPOINT = '/feeds/v1/create'
FEEDS_FETCH_ENDPOINT = '/feeds/v1/fetch'
FEEDS_LOG_STATUS_ENDPOINT = '/feeds/v1/log_status'
FEEDS_SUMMARY_ENDPOINT = '/feeds/v1/summary'

# tvmknife unittest service -s 111 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:'
    'G4hKvC1tY887M0UUAjj13gJEnzikFS9z9so'
    'b0laeFmJ4JVL0XDyNZtWBu4ZjKf9O_juLZg'
    'hRptbnyiQRqoiBsX1eXLdABRLpdJpAxLY4d'
    'fVOD0o8GEQ7q94GH0uLQOV_POubrySzzMgN'
    'gRFhn_CwXjrfZRziFuk-RV0I-zzTsE4'
)

HEADERS = {
    'X-Yandex-UID': '100',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-User-Ticket': 'ticket_valid',
}

SERVICE_NAME = 'fleet-notifications'


def build_params(park_id='park_valid'):
    return {'park_id': park_id}
