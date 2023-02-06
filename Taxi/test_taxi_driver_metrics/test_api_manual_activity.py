HANDLER_PATH = 'v1/service/activity_value/'
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
            'mode': 'absolute',
            'idempotency_token': 'token',
        },
    )
    assert response.status == 200
    json = await response.json()
    assert not json['text']

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'udid': UDID_1,
            'reason': 'because',
            'value': 3,
            'mode': 'additive',
            'idempotency_token': 'token',
        },
    )
    assert response.status == 200
    json = await response.json()
    assert not json['text']

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'udid': UDID_1,
            'reason': 'because',
            'value': 3,
            'mode': 'additive',
            'idempotency_token': 'token_//-DRIVER_METRICS/1234',
        },
    )
    assert response.status == 200

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'udid': UDID_1,
            'reason': 'because',
            'value': 3,
            'mode': 'additive',
            'idempotency_token': 'abc ',
        },
    )
    assert response.status == 400
    json = await response.json()
    assert 'does not conform to pattern:' in json['text']
