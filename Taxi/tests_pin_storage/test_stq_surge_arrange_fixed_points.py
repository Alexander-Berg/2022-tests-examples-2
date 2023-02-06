import copy

import pytest

TIME_NOW = '2019-03-08T00:00:00Z'
TIMESTAMP_NOW = '1552003200'


def round_result(data):
    result = copy.deepcopy(data)
    for fixed_point in result['result']['fixed_points']:
        fixed_point['location'] = [
            round(fixed_point['location'][0], 4),
            round(fixed_point['location'][1], 4),
        ]
    return result


@pytest.mark.now(TIME_NOW)
@pytest.mark.config(PIN_STORAGE_CREATE_PIN_REQUESTS=True)
@pytest.mark.yt(static_table_data=['yt_pins_data.yaml'])
async def test_arrange_points(
        stq_runner, taxi_pin_storage, mockserver, testpoint, yt_apply,
):
    admin_surger_requests = []

    @mockserver.json_handler('/taxi-admin-surger/v1/points/save-arranged')
    def _save_arranged(request):
        admin_surger_requests.append(request.json)
        return {}

    @testpoint('admin_surger_save_arranged')
    def admin_surger_save_arranged(data):
        pass

    await taxi_pin_storage.enable_testpoints()

    stq_params = {
        'request_id': '123456789012345678901234',
        'pins_yt_table_name': '//home/taxi/arrange_points_pins',
        'settings_override': dict({'tags': ['hello1', 'hello2']}),
    }
    await stq_runner.surge_arrange_fixed_points.call(
        task_id='task_id', kwargs=stq_params,
    )

    await admin_surger_save_arranged.wait_call()
    assert len(admin_surger_requests) == 1
    assert round_result(admin_surger_requests[0]) == {
        'result': {
            'fixed_points': [
                {
                    'location': [37.5899, 55.7261],
                    'mode': 'apply',
                    'name': 'auto_123456789012345678901234_0',
                    'surge_zone_name': 'MSK',
                    'tags': ['hello1', 'hello2'],
                },
                {
                    'location': [37.575, 55.7215],
                    'mode': 'apply',
                    'name': 'auto_123456789012345678901234_1',
                    'surge_zone_name': 'MSK',
                    'tags': ['hello1', 'hello2'],
                },
                {
                    'location': [37.6006, 55.7369],
                    'mode': 'apply',
                    'name': 'auto_123456789012345678901234_2',
                    'surge_zone_name': 'MSK',
                    'tags': ['hello1', 'hello2'],
                },
            ],
        },
        'status': 'done',
    }
