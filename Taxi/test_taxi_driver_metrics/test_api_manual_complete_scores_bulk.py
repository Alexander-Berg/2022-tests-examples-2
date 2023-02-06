import pytest

HANDLER_PATH = 'v1/service/driver/complete_scores_value/correct_bulk'
CHECK_HANDLER_PATH = (
    'v1/service/driver/complete_scores_value/correct_bulk/check'
)
UDID_1 = '5b05621ee6c22ea2654849c9'
UDID_2 = '5b05621ee6c22ea2654849c2'
UDID_3 = '5b05621ee6c22ea2654849c0'
UDID_NOT_VALID = 'not_valid'

EVENT_NEW_URL = '/driver-metrics-storage/v1/event/new/bulk'


@pytest.mark.config(
    DRIVER_METRICS_MAX_COUNT_UDIDS_FOR_BULK_API=10,
    DRIVER_METRICS_COMPLETE_SCORES_SETTINGS={
        '__default__': {
            'initial_value': 0,
            'blocking_threshold': -3,
            'amnesty_value': 5,
            'blocking_durations': [10_000],
        },
    },
)
@pytest.mark.parametrize(
    'tst_request, status, event_call',
    (
        (
            {
                'corrections': [
                    {'unique_driver_id': UDID_1, 'value': 1},
                    {'unique_driver_id': UDID_2, 'value': 5},
                ],
                'reason': 'yep',
                'mode': 'additive',
                'idempotency_token': 'token',
            },
            200,
            [
                {
                    'descriptor': {'type': 'set_complete_scores_value'},
                    'extra_data': {
                        'mode': 'additive',
                        'operation': 'set_complete_scores_value',
                        'reason': 'yep',
                        'value': 1,
                    },
                    'idempotency_token': '5b05621ee6c22ea2654849c9/token',
                    'type': 'dm_service_manual',
                    'unique_driver_id': '5b05621ee6c22ea2654849c9',
                },
                {
                    'descriptor': {'type': 'set_complete_scores_value'},
                    'extra_data': {
                        'mode': 'additive',
                        'operation': 'set_complete_scores_value',
                        'reason': 'yep',
                        'value': 5,
                    },
                    'idempotency_token': '5b05621ee6c22ea2654849c2/token',
                    'type': 'dm_service_manual',
                    'unique_driver_id': '5b05621ee6c22ea2654849c2',
                },
            ],
        ),
        (
            {
                'corrections': [
                    {'unique_driver_id': UDID_1, 'value': -1},
                    {'unique_driver_id': UDID_2, 'value': 3},
                ],
                'reason': 'yep',
                'mode': 'absolute',
                'idempotency_token': 'token',
            },
            200,
            [
                {
                    'descriptor': {'type': 'set_complete_scores_value'},
                    'extra_data': {
                        'mode': 'absolute',
                        'operation': 'set_complete_scores_value',
                        'reason': 'yep',
                        'value': -1,
                    },
                    'idempotency_token': '5b05621ee6c22ea2654849c9/token',
                    'type': 'dm_service_manual',
                    'unique_driver_id': '5b05621ee6c22ea2654849c9',
                },
                {
                    'descriptor': {'type': 'set_complete_scores_value'},
                    'extra_data': {
                        'mode': 'absolute',
                        'operation': 'set_complete_scores_value',
                        'reason': 'yep',
                        'value': 3,
                    },
                    'idempotency_token': '5b05621ee6c22ea2654849c2/token',
                    'type': 'dm_service_manual',
                    'unique_driver_id': '5b05621ee6c22ea2654849c2',
                },
            ],
        ),
        (
            {
                'corrections': [
                    {'unique_driver_id': UDID_NOT_VALID, 'value': -1},
                ],
                'reason': 'yep',
                'mode': 'absolute',
                'idempotency_token': 'token',
            },
            400,
            None,
        ),
    ),
)
async def test_different_values_for_each_udid(
        web_app_client, dms_mockserver, tst_request, status, event_call,
):
    headers = {'X-Idempotency-Token': tst_request.pop('idempotency_token')}
    response = await web_app_client.post(
        CHECK_HANDLER_PATH, json=tst_request, headers=headers,
    )

    assert response.status == status

    if status > 200:
        return

    await web_app_client.post(HANDLER_PATH, json=tst_request, headers=headers)

    assert dms_mockserver.event_new_bulk.times_called == 1

    call_1 = dms_mockserver.event_new_bulk.next_call()['request'].json
    for event in call_1['events']:
        assert event.pop('created')

    assert call_1 == {'events': event_call}
