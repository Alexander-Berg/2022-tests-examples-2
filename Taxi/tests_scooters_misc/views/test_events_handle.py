# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error

import time

from metrics_aggregations import helpers as metrics_helpers
import pytest

MOSCOW_LOCATION = {'lon': 37.4, 'lat': 55.7}


@pytest.mark.experiments3(
    filename='exp3_scooters_events_handler_settings.json',
)
@pytest.mark.config(SCOOTERS_MISC_CITY_TAGS=['scooter_moscow'])
@pytest.mark.parametrize(
    'event_type',
    [
        'last_payment_succeeded',
        'last_payment_failed',
        'scooter_in_forbidden_zone',
        'scooter_out_of_forbidden_zone',
        'low_battery_level',
        'sufficient_battery_level',
    ],
)
@pytest.mark.parametrize('acceleration_enabled', [True, False])
@pytest.mark.parametrize('battery_level', [5, 40])
@pytest.mark.parametrize('task_status', ['ok', 'no_funds'])
@pytest.mark.parametrize('zone_tag', ['moscow_zone', 'area_for_bad'])
@pytest.mark.parametrize('usage', ['busy', 'free'])
async def test_common(
        taxi_scooters_misc,
        mockserver,
        generate_uuid,
        load_json,
        event_type,
        acceleration_enabled,
        battery_level,
        task_status,
        zone_tag,
        usage,
        taxi_scooters_misc_monitor,
        get_single_metric_by_label_values,
):
    await taxi_scooters_misc.tests_control(reset_metrics=True)

    session_id = generate_uuid
    user_id = generate_uuid
    scooter_id = generate_uuid

    config = load_json('exp3_scooters_events_handler_settings.json')[
        'configs'
    ][0]['default_value']

    last_payment_failed = task_status in config['failed_payment_statuses']
    scooter_in_forbidden_zone = zone_tag in config['forbidden_zone_tags']
    scooter_is_busy = usage == 'busy'

    action_conditions = {
        'disable_acceleration': acceleration_enabled and any(
            [
                scooter_is_busy and last_payment_failed,
                scooter_in_forbidden_zone,
                battery_level <= 10,
            ],
        ),
        'enable_acceleration': all(
            [
                not acceleration_enabled,
                not last_payment_failed or not scooter_is_busy,
                not scooter_in_forbidden_zone,
                battery_level >= 15,
            ],
        ),
    }

    action_candidate = config['events'][event_type]['action']
    action = action_candidate if action_conditions[action_candidate] else None

    @mockserver.json_handler('/scooter-backend/api/taxi/car/info')
    def car_info_mock(request):
        assert request.query['car_id'] == scooter_id
        return {
            'number': '0001',
            'id': scooter_id,
            'usage': usage,
            'location': {**MOSCOW_LOCATION, 'tags': [zone_tag]},
            'telematics': {
                'accelerator_pedal': int(acceleration_enabled),
                'fuel_level': battery_level,
            },
            'tags': [{'tag_id': generate_uuid, 'tag': 'scooter_moscow'}],
            'session_info': {
                'session': {
                    'specials': {
                        'current_offer': {
                            'constructor_id': 'minutes',
                            'type': 'standart_offer',
                        },
                        'current_offer_state': {},
                    },
                },
                'meta': {
                    'session_id': session_id,
                    'user_id': user_id,
                    'object_id': scooter_id,
                    'instance_id': generate_uuid,
                },
            },
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/billing/payment/info')
    def payment_info_mock(request):
        assert request.query['session_id'] == session_id
        return {
            'current': [
                {
                    'task_status': task_status,
                    'last_status_update': int(time.time()) - 60,
                },
            ],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    def car_tag_add_mock(request):
        assert action is not None
        assert request.query['unique_policy'] == 'skip_if_exists'
        assert request.json == {
            'object_ids': [scooter_id],
            'tag_name': config['events'][event_type]['car_tag'],
        }
        return {'tagged_objects': []}

    @mockserver.json_handler('/scooter-backend/api/taxi/user/tag_add')
    def user_tag_add_mock(request):
        assert action is not None
        assert request.query['unique_policy'] == 'skip_if_exists'
        assert request.json == {
            'object_ids': [user_id],
            'tag_name': config['events'][event_type]['user_tag'],
        }
        return {'tagged_objects': []}

    response = await taxi_scooters_misc.post(
        '/scooters-misc/v1/events-handle',
        json={'events': [{'type': event_type, 'scooter_id': scooter_id}]},
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert car_info_mock.times_called == 1
    assert payment_info_mock.times_called == int(scooter_is_busy)

    assert car_tag_add_mock.times_called == int(action is not None)
    assert user_tag_add_mock.times_called == int(
        action is not None and scooter_is_busy,
    )

    sensor = 'scooters_misc_events_handler_metrics'
    metric = await get_single_metric_by_label_values(
        taxi_scooters_misc_monitor, sensor=sensor, labels={'sensor': sensor},
    )
    assert metric == metrics_helpers.Metric(
        labels={
            'sensor': sensor,
            'type': event_type,
            'city_tag': 'scooter_moscow',
            'action': action_candidate,
            'action_is_performed': str(int(action is not None)),
        },
        value=1,
    )
