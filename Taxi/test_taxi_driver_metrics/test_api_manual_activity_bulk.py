import pytest

HANDLER_PATH = 'v1/service/driver/correct_activity_value_bulk/'
CHECK_HANDLER_PATH = 'v1/service/driver/correct_activity_value_bulk/check'
UDID_1 = '5b05621ee6c22ea2654849c9'
UDID_2 = '5b05621ee6c22ea2654849c2'
UDID_3 = '5b05621ee6c22ea2654849c0'
UDID_NOT_VALID = 'not_valid'

EVENT_NEW_URL = '/driver-metrics-storage/v1/event/new/bulk'


@pytest.mark.config(DRIVER_METRICS_MAX_COUNT_UDIDS_FOR_BULK_API=2)
async def test_base(taxi_driver_metrics, mockserver):
    @mockserver.json_handler(EVENT_NEW_URL)
    def _patch_event_new(request, *args, **kwargs):
        data = request.json
        for event in data['events']:
            assert event['type'] == 'dm_service_manual'
        return {'events': []}

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'unique_driver_ids': [UDID_1, UDID_2],
            'reason': 'because',
            'mode': 'absolute',
            'value': 3,
            'idempotency_token': 'token',
        },
    )
    assert response.status == 200

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'unique_driver_ids': [UDID_1, ''],
            'reason': 'because',
            'mode': 'absolute',
            'value': 3,
            'idempotency_token': 'token',
        },
    )
    assert response.status == 200

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'reason': 'because',
            'mode': 'absolute',
            'value': 3,
            'idempotency_token': 'token',
        },
    )
    assert response.status == 400

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={'unique_driver_ids': [UDID_1, UDID_2], 'reason': 'because'},
    )
    assert response.status == 400

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'drivers_values': [{'unique_driver_id': UDID_1, 'value': 5}],
            'idempotency_token': 'token',
            'mode': 'absolute',
        },
    )
    assert response.status == 200

    response = await taxi_driver_metrics.post(
        HANDLER_PATH,
        json={
            'udid': [UDID_1, UDID_NOT_VALID],
            'reason': 'because',
            'value': 3,
            'mode': 'additive',
            'idempotency_token': 'abc ',
        },
    )
    assert response.status == 400

    response = await taxi_driver_metrics.post(
        f'{HANDLER_PATH}check',
        json={
            'unique_driver_ids': [UDID_1, UDID_2, UDID_3],
            'reason': 'because',
            'mode': 'absolute',
            'value': 3,
            'idempotency_token': 'token',
        },
    )
    content = await response.json()
    assert content['code'] == 'limit_exceeded'
    assert response.status == 400


@pytest.mark.config(DRIVER_METRICS_MAX_COUNT_UDIDS_FOR_BULK_API=3)
async def test_manual_activity_bulk_check(web_app_client):
    udids = [UDID_1, UDID_2, UDID_3]

    response = await web_app_client.post(
        CHECK_HANDLER_PATH,
        json={
            'unique_driver_ids': udids,
            'idempotency_token': 'token',
            'mode': 'absolute',
            'value': 5,
        },
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json['data']['idempotency_token'] == 'token'
    assert response_json['data']['mode'] == 'absolute'
    assert response_json['data']['value'] == 5
    assert sorted(response_json['data']['unique_driver_ids']) == [
        '5b05621ee6c22ea2654849c0',
        '5b05621ee6c22ea2654849c2',
        '5b05621ee6c22ea2654849c9',
    ]

    udids = [UDID_1, 'god please no']

    response = await web_app_client.post(
        CHECK_HANDLER_PATH,
        json={
            'unique_driver_ids': udids,
            'idempotency_token': 'token',
            'mode': 'absolute',
        },
    )
    assert response.status == 400

    udids = [UDID_1] * 5

    response = await web_app_client.post(
        CHECK_HANDLER_PATH,
        json={'unique_driver_ids': udids, 'idempotency_token': 'token'},
    )
    assert response.status == 400

    udids = [UDID_1, UDID_2, UDID_3]

    response = await web_app_client.post(
        CHECK_HANDLER_PATH,
        json={'unique_driver_ids': udids, 'idempotency_token': '133+-..sadp'},
    )

    assert response.status == 400


async def test_insertion_partial_fail(web_app_client, mockserver):
    @mockserver.json_handler(EVENT_NEW_URL)
    def _patch_event_new(request, *args, **kwargs):
        return {
            'events': [
                {
                    'idempotency_token': 'some',
                    'error': {
                        'message': 'Insertion failed for udid: 123',
                        'code': 'error',
                    },
                },
            ],
        }

    response = await web_app_client.post(
        HANDLER_PATH,
        json={
            'unique_driver_ids': [UDID_1, UDID_2, UDID_3],
            'drivers_values': [
                {'unique_driver_id': UDID_1, 'value': 4},
                {'unique_driver_id': UDID_2, 'value': 5},
            ],
            'reason': 'yep',
            'mode': 'absolute',
            'value': 7,
            'idempotency_token': 'token',
        },
    )
    assert response.status == 200
    data = await response.json()

    assert data == {
        'status': 'partially_completed',
        'errors': [
            {
                'error': {
                    'code': 'error',
                    'message': 'Insertion failed for udid: 123',
                },
                'idempotency_token': 'some',
            },
        ],
    }


@pytest.mark.config(DRIVER_METRICS_MAX_COUNT_UDIDS_FOR_BULK_API=10)
async def test_different_values_for_each_udid(web_app_client, dms_mockserver):
    response = await web_app_client.post(
        HANDLER_PATH,
        json={
            'unique_driver_ids': [UDID_1, UDID_2, UDID_3],
            'drivers_values': [
                {'unique_driver_id': UDID_1, 'value': 4},
                {'unique_driver_id': UDID_2, 'value': 5},
            ],
            'reason': 'yep',
            'mode': 'absolute',
            'value': 7,
            'idempotency_token': 'token',
        },
    )
    assert response.status == 200

    assert dms_mockserver.event_new_bulk.times_called == 1

    call_1 = dms_mockserver.event_new_bulk.next_call()['request'].json
    for event in call_1['events']:
        assert event.pop('created')

    assert call_1 == {
        'events': [
            {
                'type': 'dm_service_manual',
                'unique_driver_id': '5b05621ee6c22ea2654849c9',
                'idempotency_token': '5b05621ee6c22ea2654849c9/token',
                'descriptor': {'type': 'set_activity_value'},
                'extra_data': {
                    'operation': 'set_activity_value',
                    'mode': 'absolute',
                    'value': 4,
                    'reason': 'yep',
                },
            },
            {
                'type': 'dm_service_manual',
                'unique_driver_id': '5b05621ee6c22ea2654849c2',
                'idempotency_token': '5b05621ee6c22ea2654849c2/token',
                'descriptor': {'type': 'set_activity_value'},
                'extra_data': {
                    'operation': 'set_activity_value',
                    'mode': 'absolute',
                    'value': 5,
                    'reason': 'yep',
                },
            },
        ],
    }
