FEEDS_CREATE_ENDPOINT = '/feeds/v1/create'
FEEDS_FETCH_ENDPOINT = '/feeds/v1/fetch'
FEEDS_FETCH_BY_ID_ENDPOINT = '/feeds/v1/fetch_by_id'
FEEDS_REMOVE_ENDPOINT = '/feeds/v1/remove'
FEEDS_LOG_STATUS_ENDPOINT = '/feeds/v1/log_status'

# tvmknife unittest service -s 111 -d 2018676
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxD0mns:DrgESvD'
    '-6-THZo_Z5Tx88sciWWggWj56j5EWCFeVjfeCLE1vJ'
    'FacG4bzIcIDHvrbrsWHt6j5vLxh5AXy1JRrVIeu1Gs'
    'NsaBWb_o2ETMzJz41ba2weqib6c95orB4sU9wdV0y9'
    'aKE3di8VgfPTTGyCvhbZ1wlZN7L-NX7P9xF8pM'
)
# tvmknife unittest user -d 100 -e test --scopes read,write
USER_TICKET = (
    '3:user:CA0Q__________9_GhsKAghkEGQaBHJlYWQa'
    'BXdyaXRlINKF2MwEKAE:NUa9-lQjXTADvKlL8saH1Xs'
    'C-17g0jlGuJW9eC2PIJ85mi5TkXevq4-z033xgf8D6O'
    'EvAhi8F2Wm1qBQTkf8ooVnARVJa_leLxlLyN49PeeHP'
    'lOHbQ31LCyinygUdgN0FhwG87PZ2D-OtplvLOmSvmO1'
    'iXA1dbI2D8bdnYRzSE8'
)
HEADERS = {
    'X-Yandex-UID': '100',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-User-Ticket': USER_TICKET,
}

HEADERS_YATEAM = {
    'X-Yandex-UID': '100',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Ya-User-Ticket': USER_TICKET,
}

TUTORIAL_PAYLOAD = {
    'body': 'text',
    'buttons': [
        {
            'title': 'button',
            'action': {'type': 'next'},
            'body': 'body',
            'params': {'color': '#122faa'},
        },
    ],
    'title': 'title',
}

TUTORIALS_EMPTY_CONFIG: dict = {}

TUTORIALS_BASE_CONFIG = {
    'tutorial_1': {
        'payloads': [TUTORIAL_PAYLOAD],
        'params': {
            'enabled': True,
            'need_confirm': False,
            'priority': 0,
            'is_repeatable': False,
        },
        'destination': {
            'locations': {
                'include': [{'category': 'country', 'id': 'Russia'}],
            },
        },
    },
}

TUTORIALS_EXTENDED_CONFIG = {
    **TUTORIALS_BASE_CONFIG,
    'tutorial_2': {
        'payloads': [TUTORIAL_PAYLOAD],
        'params': {
            'enabled': True,
            'need_confirm': False,
            'priority': 1,
            'is_repeatable': False,
        },
        'destination': {
            'locations': {'include': [{'category': 'city', 'id': 'Moscow'}]},
        },
    },
}

TUTORIALS_HIDDEN_CONFIG = {
    **TUTORIALS_BASE_CONFIG,
    'tutorial_2': {
        'payloads': [TUTORIAL_PAYLOAD],
        'params': {
            'enabled': True,
            'need_confirm': False,
            'priority': 1,
            'is_repeatable': False,
        },
        'destination': {
            'locations': {'include': [{'category': 'city', 'id': 'Moscow'}]},
            'page_ids': {'include': []},
        },
    },
}

FEEDS_BASE_RESPONSE = {
    'polling_delay': 300,
    'etag': 'new-etag',
    'has_more': False,
    'feed': [
        {
            'feed_id': 'unique_feed_id',
            'created': '2019-01-04T23:59:59+0000',
            'request_id': 'request_id',
            'payload': {
                'tutorial_id': 'tutorial_1',
                'payloads': [TUTORIAL_PAYLOAD],
            },
        },
    ],
}

FEEDS_EMPTY_RESPONSE: list = []
