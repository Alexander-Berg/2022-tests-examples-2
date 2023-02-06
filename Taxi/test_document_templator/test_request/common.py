TARIFF = 'Tariff'
SURGE = 'Surge'
NOT_IN_DB = 'Not in db'


REQUEST_ID_BY_NAME = {
    TARIFF: '5ff4901c583745e089e55bd1',
    SURGE: '5ff4901c583745e089e55bd3',
}
DOCUMENT_TEMPLATOR_REQUESTS = {
    TARIFF: {
        'method': 'POST',
        'url_pattern': '$mockserver/tariff/{zone}/{tariff}/',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    SURGE: {
        'method': 'GET',
        'url_pattern': '$mockserver/get_surge/',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    NOT_IN_DB: {
        'method': 'GET',
        'url_pattern': '$mockserver/not_in_db/{db}',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
}
CONFIG = {'DOCUMENT_TEMPLATOR_REQUESTS': DOCUMENT_TEMPLATOR_REQUESTS}
