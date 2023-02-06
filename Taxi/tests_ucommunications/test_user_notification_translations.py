import json

import pytest


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
@pytest.mark.parametrize(
    'text,payload',
    [
        ('Строка!', 'Строка!'),
        (
            {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}},
            '100 руб.',
        ),
    ],
)
async def test_send_ok(taxi_ucommunications, mockserver, text, payload):
    @mockserver.json_handler('/xiva/v2/send')
    def _mock_xiva(request):
        body = json.loads(request.get_data())
        assert body['payload']['msg'] == payload
        assert body['payload']['title'] == 'Title'
        return mockserver.make_response('{}', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user',
            'locale': 'ru',
            'data': {'payload': {'msg': text, 'title': 'Title'}},
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_send_bad(taxi_ucommunications):
    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user',
            'data': {
                'payload': {
                    'msg': {'key': 'key1', 'keyset': 'notify'},
                    'title': 'Title',
                },
            },
        },
    )
    assert response.status_code == 400
