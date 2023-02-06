import json
import random
import string

import pytest


MOCK_DATA_EXPECTED = {
    'condition': (
        '\'moscow.online\' in topics || '
        '\'russia.online\' in topics || \'debug\' in topics || '
        '\'topic1\' in topics || \'topic2\' in topics'
    ),
    'to': '/topics/topic3',
}
MOCK_DATA_REQUESTED: list = []


@pytest.fixture(name='fcm_service_topics')
def _fcm_service_topics(mockserver, fcm_service):
    @mockserver.json_handler('/fcm/send')
    def _fcm_send(request):
        return fcm_service.on_send(request, MOCK_DATA_REQUESTED)


async def test_send_topics(taxi_device_notify, fcm_service_topics):
    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {
        'priority': 10,
        'ttl': 30,
        'event': 'test_send_topics',
        'service': k_service_name1,
    }
    data = {
        'topics': [
            'moscow.online',
            'russia.online',
            'debug',
            'topic1',
            'topic2',
            'topic3',
        ],
        'payload': {
            'priority': 'high',
            'notification': {
                'title': 'sample title',
                'body': 'sample notification',
            },
        },
    }

    # Normal send to topic
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
    assert len(MOCK_DATA_REQUESTED) == len(MOCK_DATA_EXPECTED)
    found_keys = set()
    for req in MOCK_DATA_REQUESTED:
        if 'condition' in req and 'condition' not in found_keys:
            found_keys.add('condition')
            assert req['condition'] == MOCK_DATA_EXPECTED['condition']
        elif 'to' in req and 'to' not in found_keys:
            found_keys.add('to')
            assert req['to'] == MOCK_DATA_EXPECTED['to']
        else:
            assert False

    # Long payload but fit in limits
    # MOCK_DATA_EXPECTED = []  # it has no sense
    params['event'] = 'test_send_topics_long'
    data['payload']['notification']['body'] = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(3000)
    )
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
