HANDLER_PATH = 'v1/service/correct_loyalty_value/'
UDID_1 = '5b05621ee6c22ea2654849c9'


async def test_base(taxi_driver_metrics, mockserver):
    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _patch_event_new(*args, **kwargs):
        return {}

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'udid': UDID_1,
            'reason': 'because',
            'value': 3,
            'idempotency_token': 'token',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={'udid': UDID_1, 'value': 3, 'idempotency_token': 'token'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    response = await taxi_driver_metrics.post(
        HANDLER_PATH, json={'udid': UDID_1, 'idempotency_token': 'tokeni'},
    )
    assert response.status == 400
    content = await response.text()
    assert 'required property' in content

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={'udid': '4v94994994', 'value': 3, 'idempotency_token': 'token'},
    )
    assert response.status == 400
    content = await response.text()
    assert 'Mongo' in content
