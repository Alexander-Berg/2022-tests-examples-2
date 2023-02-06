import pytest


ENDPOINT_URL = '/v2/clients/list'

CLIENT_OPTEUM = {
    'consumer_id': 'fleet-api-internal',
    'client_id': 'opteum',
    'name': 'Оптеум',
    'comment': '',
    'creator': {'uid': '54591353', 'uid_provider': 'yandex'},
    'created_at': '2018-02-25T16:04:13+00:00',
    'updated_at': '2018-02-25T16:04:13+00:00',
}
CLIENT_YANDEX_GAS = {
    'consumer_id': 'fleet-api-internal',
    'client_id': 'yandex_gas',
    'name': 'Яндекс.Заправки',
    'comment': '',
    'creator': {'uid': '1120000000083978', 'uid_provider': 'yandex_team'},
    'created_at': '2018-02-25T17:04:13+00:00',
    'updated_at': '2018-02-25T17:04:13+00:00',
}
CLIENT_VASYA = {
    'consumer_id': 'fleet-api',
    'client_id': 'vasya',
    'name': 'Вася',
    'comment': '',
    'creator': {'uid': '54591353', 'uid_provider': 'yandex'},
    'created_at': '2018-02-26T11:55:13+00:00',
    'updated_at': '2018-02-26T11:55:13+00:00',
}
CLIENT_PETYA = {
    'consumer_id': 'fleet-api',
    'client_id': 'petya',
    'name': 'Петя',
    'comment': '',
    'creator': {'uid': '54591353', 'uid_provider': 'yandex_team'},
    'created_at': '2018-02-26T11:56:13+00:00',
    'updated_at': '2018-02-26T11:56:13+00:00',
}
CLIENT_KOLYA = {
    'consumer_id': 'fleet-api',
    'client_id': 'kolya',
    'name': 'Коля',
    'comment': '',
    'creator': {'uid': '1120000000083978', 'uid_provider': 'yandex_team'},
    'created_at': '2018-02-26T11:57:13+00:00',
    'updated_at': '2018-02-26T11:57:13+00:00',
}
CLIENT_OPTEUM_EXTERNAL = {
    'consumer_id': 'fleet-api',
    'client_id': 'opteum',
    'name': 'Оптеум внешний',
    'comment': '',
    'creator': {'uid': '555', 'uid_provider': 'yandex'},
    'created_at': '2018-02-26T12:12:13+00:00',
    'updated_at': '2018-02-26T12:12:13+00:00',
}

OK_PARAMS = [
    (
        {},
        {
            'limit': 100,
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
                CLIENT_YANDEX_GAS,
                CLIENT_OPTEUM,
            ],
        },
    ),
    # query.consumer_id
    (
        {'query': {'consumer_id': 'fleet-api-internal'}},
        {'limit': 100, 'clients': [CLIENT_YANDEX_GAS, CLIENT_OPTEUM]},
    ),
    (
        {'query': {'consumer_id': 'fleet-api'}},
        {
            'limit': 100,
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
            ],
        },
    ),
    # query.client_id
    (
        {'query': {'client_id': 'yandex_gas'}},
        {'limit': 100, 'clients': [CLIENT_YANDEX_GAS]},
    ),
    (
        {'query': {'client_id': 'vasya'}},
        {'limit': 100, 'clients': [CLIENT_VASYA]},
    ),
    (
        {'query': {'client_id': 'petya'}},
        {'limit': 100, 'clients': [CLIENT_PETYA]},
    ),
    (
        {'query': {'client_id': 'kolya'}},
        {'limit': 100, 'clients': [CLIENT_KOLYA]},
    ),
    (
        {'query': {'client_id': 'opteum'}},
        {'limit': 100, 'clients': [CLIENT_OPTEUM_EXTERNAL, CLIENT_OPTEUM]},
    ),
    # query.consumer_id + query.client_id
    (
        {'query': {'consumer_id': 'fleet-api', 'client_id': 'opteum'}},
        {'limit': 100, 'clients': [CLIENT_OPTEUM_EXTERNAL]},
    ),
    # query.text
    ({'query': {'text': 'someone'}}, {'limit': 100, 'clients': []}),
    (
        {'query': {'text': 'yandex_gas kolya opteum vasya petya'}},
        {
            'limit': 100,
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
                CLIENT_YANDEX_GAS,
                CLIENT_OPTEUM,
            ],
        },
    ),
    (
        {'query': {'text': 'Яндекс.ЗАправки кОля опте петя ВАСЯ'}},
        {
            'limit': 100,
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
                CLIENT_YANDEX_GAS,
                CLIENT_OPTEUM,
            ],
        },
    ),
    (
        {'query': {'text': 'yandex_gas кОля pet ВАСЯ'}},
        {
            'limit': 100,
            'clients': [
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
                CLIENT_YANDEX_GAS,
            ],
        },
    ),
    (
        {
            'query': {
                'client': {
                    'client_id': [
                        'opteum',
                        'yandex_gas',
                        'vasya',
                        'petya',
                        'kolya',
                    ],
                },
                'text': 'теум',
            },
        },
        {'limit': 100, 'clients': [CLIENT_OPTEUM_EXTERNAL, CLIENT_OPTEUM]},
    ),
    # limit
    (
        {'limit': 6},
        {
            'limit': 6,
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
                CLIENT_YANDEX_GAS,
                CLIENT_OPTEUM,
            ],
        },
    ),
    (
        {'limit': 4},
        {
            'limit': 4,
            'cursor': '2',
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
            ],
        },
    ),
    # cursor
    (
        {'cursor': '547'},
        {
            'limit': 100,
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
                CLIENT_YANDEX_GAS,
                CLIENT_OPTEUM,
            ],
        },
    ),
    (
        {'cursor': '6'},
        {
            'limit': 100,
            'clients': [
                CLIENT_OPTEUM_EXTERNAL,
                CLIENT_KOLYA,
                CLIENT_PETYA,
                CLIENT_VASYA,
                CLIENT_YANDEX_GAS,
                CLIENT_OPTEUM,
            ],
        },
    ),
    (
        {'cursor': '3'},
        {
            'limit': 100,
            'clients': [CLIENT_VASYA, CLIENT_YANDEX_GAS, CLIENT_OPTEUM],
        },
    ),
    ({'cursor': '1'}, {'limit': 100, 'clients': [CLIENT_OPTEUM]}),
    # limit + cursor
    (
        {'limit': 2, 'cursor': '5'},
        {'limit': 2, 'cursor': '3', 'clients': [CLIENT_KOLYA, CLIENT_PETYA]},
    ),
    # query.text + limit
    (
        {'query': {'text': 'kolya'}, 'limit': 2},
        {'limit': 2, 'clients': [CLIENT_KOLYA]},
    ),
    (
        {'query': {'text': 'kolya'}, 'limit': 1},
        {'limit': 1, 'clients': [CLIENT_KOLYA]},
    ),
]


@pytest.mark.parametrize('request_json, response_json', OK_PARAMS)
async def test_ok(taxi_uapi_keys, request_json, response_json):
    response = await taxi_uapi_keys.post(ENDPOINT_URL, json=request_json)

    assert response.status_code == 200
    assert response.json() == response_json
