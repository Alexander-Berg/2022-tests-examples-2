import pytest

from testsuite.utils import matching


@pytest.mark.parametrize(
    'input_data, status, config_updated, old_config_data, new_config_data',
    [
        pytest.param(
            {'subsystems_info': {}},
            'success',
            False,
            None,
            None,
            id='missing service_info',
        ),
        pytest.param(
            {
                'subsystems_info': {
                    'service_info': {
                        'duty_group_id': {'new': 'some', 'old': None},
                    },
                },
            },
            'success',
            False,
            None,
            None,
            id='just removing plain old duty_group_id',
        ),
        pytest.param(
            {
                'subsystems_info': {
                    'service_info': {
                        'duty_group_id': {'new': None, 'old': 'some'},
                    },
                },
            },
            'success',
            False,
            None,
            None,
            id='just adding plain old duty_group_id',
        ),
        pytest.param(
            {
                'subsystems_info': {
                    'service_info': {
                        'duty_group_id': {'new': None, 'old': 'some'},
                        'duty': {
                            'old': None,
                            'new': {
                                'abc_slug': 'abc_slug',
                                'primary_schedule': 'primary_schedule',
                            },
                        },
                    },
                },
            },
            'success',
            True,
            [{'id': 'some', 'param1': 'value1', 'param2': 'value2'}],
            [
                {'id': 'some', 'param1': 'value1', 'param2': 'value2'},
                {
                    'id': 'abc_slug:primary_schedule',
                    'param1': 'value1',
                    'param2': 'value2',
                },
            ],
            id='change duty type and extend config',
        ),
        pytest.param(
            {
                'subsystems_info': {
                    'service_info': {
                        'duty_group_id': {'new': None, 'old': 'some'},
                        'duty': {
                            'old': None,
                            'new': {
                                'abc_slug': 'abc_slug',
                                'primary_schedule': 'primary_schedule',
                            },
                        },
                    },
                },
            },
            'success',
            False,
            [{'id': 'more', 'param1': 'value1', 'param2': 'value2'}],
            None,
            id='change duty and do not extend config (old duty not found)',
        ),
        pytest.param(
            {
                'subsystems_info': {
                    'service_info': {
                        'duty_group_id': {'new': None, 'old': 'some'},
                        'duty': {
                            'old': None,
                            'new': {
                                'abc_slug': 'abc_slug',
                                'primary_schedule': 'primary_schedule',
                            },
                        },
                    },
                },
            },
            'success',
            False,
            [
                {'id': 'some', 'param1': 'value1', 'param2': 'value2'},
                {
                    'id': 'abc_slug:primary_schedule',
                    'param1': 'value1',
                    'param2': 'value2',
                },
            ],
            None,
            id='new duty settings already in config',
        ),
    ],
)
async def test_ensure_new_duty_group_in_config(
        mockserver,
        web_app_client,
        input_data,
        status,
        config_updated,
        old_config_data,
        new_config_data,
):
    @mockserver.json_handler('/abk-configs/CLOWNY_ALERT_MANAGER_DUTY_GROUPS/')
    def _config_handler(request):
        if request.method == 'GET':
            return {'value': old_config_data}
        return {}

    response = await web_app_client.post(
        '/task-processor/v1/cubes/ABKConfigsEnsureNewDutyGroupInConfig/',
        json={
            'input_data': input_data,
            'job_id': 1,
            'retries': 0,
            'status': 'in_progress',
            'task_id': 1,
        },
    )
    data = await response.json()
    assert data['status'] == status

    update_call = None
    while _config_handler.has_calls:
        call = _config_handler.next_call()
        if call['request'].method == 'POST':
            update_call = call
            break
    if not config_updated:
        assert update_call is None
        return

    assert update_call['request'].json == {
        'new_value': new_config_data,
        'old_value': old_config_data,
        'reason': matching.any_string,
    }
