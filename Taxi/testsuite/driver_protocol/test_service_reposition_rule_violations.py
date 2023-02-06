import json

import pytest


@pytest.fixture
def client_notify(mockserver):
    class Handlers:
        @mockserver.json_handler('/client_notify/v2/push')
        def mock_client_notify(request):
            request.get_data()
            return {'notification_id': '123123'}

    return Handlers()


@pytest.mark.parametrize(
    'urgency,disable_count,flags,warning',
    [
        (
            'last_warning',
            0,
            None,
            (
                'Нарушение правил перемешения',
                'Нарушение режима перемещения ДОМОЙ! '
                'Начните движение иначе режим ДОМОЙ будет выключен!',
            ),
        ),
        (
            'final_warning',
            1,
            ['refresh_state'],
            (
                'Нарушение правил перемешения',
                'Нарушение режима перемещения! Режим будет выключен!',
            ),
        ),
    ],
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_messages_mode(
        taxi_driver_protocol,
        client_notify,
        redis_store,
        urgency,
        disable_count,
        warning,
        flags,
):
    assert (
        taxi_driver_protocol.post(
            '/service/reposition/rule-violations',
            json={
                'violations': [
                    {
                        'park_db_id': '1488',
                        'driver_uuid': 'driverSS1',
                        'urgency': urgency,
                        'type': 'no_movement',
                        'mode': 'home',
                    },
                ],
            },
        ).status_code
        == 200
    )
    assert redis_store.exists('Chat:Messages:PRIVATE:1488:driverSS1')
    assert (
        json.loads(
            redis_store.lrange('Chat:Messages:PRIVATE:1488:driverSS1', 0, -1)[
                0
            ],
        )['expiration_date']
        == '2018-01-22T01:00:00.000000Z'
    )

    request = client_notify.mock_client_notify.wait_call()['request'].json

    data = request['data']
    notification = request['notification']

    assert (notification['title'], notification['text']) == warning
    assert ('flags' in data) != (flags is None)
    assert (flags is None) or data['flags'] == flags


@pytest.mark.config(REPOSITION_ENABLED=False)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_reposition_disabled(taxi_driver_protocol):
    request_params = {
        'violations': [
            {
                'park_db_id': '1488',
                'driver_uuid': 'driverSS1',
                'urgency': 'last_warning',
                'type': 'no_movement',
                'mode': 'home',
            },
        ],
    }
    response = taxi_driver_protocol.post(
        '/service/reposition/rule-violations', json=request_params,
    )
    assert response.status_code == 503


def test_disable_reposition(taxi_driver_protocol, client_notify):
    request_params = {
        'violations': [
            {
                'park_db_id': '777',
                'driver_uuid': '888',
                'urgency': 'final_warning',
                'type': 'arrival',
                'mode': 'home',
            },
            {
                'park_db_id': '12341777',
                'driver_uuid': '888',
                'urgency': 'final_warning',
                'type': 'no_movement',
                'mode': 'home',
            },
        ],
    }
    response = taxi_driver_protocol.post(
        '/service/reposition/rule-violations', json=request_params,
    )
    assert response.status_code == 200
    client_notify.mock_client_notify.wait_call()
