import pytest

PARK_ID = 'park_id_1'
DRIVER_ID = 'driver_id_1'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}

ENDPOINT = '/driver/v1/order-misc/v1/action/statistics'


@pytest.mark.experiments3(
    name='scenario_events_experiment',
    consumers=['driver_order_misc/activity-statistics'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['driver_id_1'],
                    'arg_name': 'driver_id',
                    'set_elem_type': 'string',
                },
            },
            'title': 'For everyone',
            'value': {
                'free_roam': {
                    'id': 'dbid_uuid',
                    'tag_ttl_hours': 3,
                    'events': {
                        'started': {
                            'tag': 'tag_for_priority',
                            'action': 'add',
                        },
                        'stopped': {
                            'tag': 'tag_for_priority',
                            'action': 'remove',
                        },
                    },
                },
                'fun_times': {
                    'id': 'udid',
                    'tag_ttl_hours': 2,
                    'events': {
                        'started': {'tag': 'tag_for_fun', 'action': 'add'},
                        'stopped': {'tag': 'tag_for_fun', 'action': 'remove'},
                    },
                },
            },
        },
    ],
)
@pytest.mark.parametrize(
    'scenario, event, code, kwargs',
    [
        (
            'free_roam',
            'started',
            200,
            {
                'tag': 'tag_for_priority',
                'entity_type': 4,
                'record_match_id': 'park_id_1_driver_id_1',
                'tag_ttl_hours': 3,
                'enable': True,
            },
        ),
        (
            'fun_times',
            'started',
            200,
            {
                'tag': 'tag_for_fun',
                'entity_type': 2,
                'record_match_id': 'unique_driver_id_1',
                'tag_ttl_hours': 2,
                'enable': True,
            },
        ),
        ('fun_timez', 'started', 400, {}),
    ],
)
async def test_post_action_statistics(
        scenario,
        event,
        code,
        kwargs,
        taxi_driver_order_misc,
        driver_trackstory,
        stq,
):
    response = await taxi_driver_order_misc.post(
        ENDPOINT,
        headers=AUTHORIZED_HEADERS,
        json={'scenario': scenario, 'event': event},
    )
    assert response.status_code == code
    if code == 200:
        assert stq.driver_set_remove_tag.times_called == 1
        response_kwargs = stq.driver_set_remove_tag.next_call()['kwargs']
        response_kwargs.pop('log_extra')
        assert response_kwargs == kwargs


@pytest.mark.parametrize(
    'kwargs',
    [
        (
            {
                'tag': 'tag_for_priority',
                'entity_type': 4,
                'record_match_id': 'park_id_1_driver_id_1',
                'tag_ttl_hours': 3,
                'enable': True,
            }
        ),
        (
            {
                'tag': 'tag_for_fun',
                'entity_type': 2,
                'record_match_id': 'unique_driver_id_1',
                'tag_ttl_hours': 2,
                'enable': True,
            }
        ),
    ],
)
async def test_stq_worker(stq_runner, tags, kwargs):
    tags.udid = kwargs['entity_type'] == 2
    await stq_runner.driver_set_remove_tag.call(
        task_id='sample_task', kwargs=kwargs,
    )
