import json

import pytest


@pytest.fixture
def taxi_rider_metrics_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_rider_metrics_mocks')
async def test_ping(taxi_rider_metrics_web):
    response = await taxi_rider_metrics_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


CORRECT_EVENTS_HISTORY = {
    'events': [
        {
            'event_id': '123',
            'type': 'asd',
            'order_id': '321',
            'tariff_zone': 'msk',
            'descriptor': '{\"name\":\"name\", \"tags\":[]}',
            'extra_data': '{\"super_field\":\"super_value\"}',
            'created': '2019-01-01T11:40:31.043000Z',
        },
    ],
}


@pytest.mark.parametrize(
    'request_body, bad_request',
    [
        ({'user_id': '321'}, True),
        ({'older_than': '2019-01-01T11:40:31.043000Z'}, True),
        ({'user_phone_id': '123'}, False),
    ],
)
@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_rider_metrics_mocks')
async def test_rider_history(
        taxi_rider_metrics_web, mockserver, request_body, bad_request,
):
    @mockserver.json_handler('/rider-metrics-storage/v1/events/processed')
    async def _mock_processed_events(*_args, **_kwargs):
        return CORRECT_EVENTS_HISTORY

    response = await taxi_rider_metrics_web.get(
        '/v1/service/rider/history', params=request_body,
    )
    if not bad_request:
        assert response.status == 200
        res = await response.text()
        deserialized = json.loads(res)

        assert deserialized['user_phone_id'] == '123'
        assert deserialized['count'] == 1
        event = deserialized['items'][0]['event']
        assert event['event_id'] == '123'
        assert event['additional_properties']['super_field'] == 'super_value'
    else:
        assert response.status == 400
