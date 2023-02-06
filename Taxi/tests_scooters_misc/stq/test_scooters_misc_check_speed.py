import time

import pytest


@pytest.mark.parametrize(
    'check_speed_settings_config, car_tag_add_times_called_exp',
    [
        pytest.param(
            {'batch_size_for_tag_add': 3, 'heartbeat_valid_lag_seconds': 60},
            4,
        ),
        pytest.param(
            {'batch_size_for_tag_add': 2, 'heartbeat_valid_lag_seconds': 60},
            5,
        ),
        pytest.param(
            {'batch_size_for_tag_add': 1, 'heartbeat_valid_lag_seconds': 60},
            7,
        ),
    ],
)
@pytest.mark.config(
    SCOOTERS_MISC_REGIONS_SPEED_LIMIT_SETTINGS={
        'scooter': 25,
        'scooter_spb': 20,
        '__default__': 25,
    },
)
async def test_simple(
        stq_runner,
        mockserver,
        taxi_config,
        load_json,
        check_speed_settings_config,
        car_tag_add_times_called_exp,
):
    taxi_config.set_values(
        dict(SCOOTERS_MISC_CHECK_SPEED_SETTINGS=check_speed_settings_config),
    )

    scooter_to_added_tag_map = {}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def car_details(request):
        response = load_json(filename='details.json')
        for car in response['cars']:
            heartbeat_lag = int(time.time())
            # emulate scooter with old heartbeat
            if car['number'] == '0011':
                heartbeat_lag = heartbeat_lag - 61
            # emulate scooter without heartbeat
            if car['number'] == '0012':
                continue

            if car['number'] == '0010':
                heartbeat_lag = heartbeat_lag - 59

            car['lag'] = {'heartbeat': heartbeat_lag}
        return response

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    async def car_tag_add(request):
        tag_added_for = set()

        for obj in request.json['object_ids']:
            tag_added_for.add(obj)

        if not request.json['tag_name'] in scooter_to_added_tag_map.keys():
            scooter_to_added_tag_map[request.json['tag_name']] = tag_added_for
        else:
            scooter_to_added_tag_map[request.json['tag_name']] = (
                scooter_to_added_tag_map[request.json['tag_name']]
                | tag_added_for
            )

        return {'tagged_objects': []}

    await stq_runner.scooters_misc_check_speed.call(task_id='task_id')

    assert car_details.times_called == 1
    assert car_tag_add.times_called == car_tag_add_times_called_exp

    assert scooter_to_added_tag_map == {
        'slowdown_low_deffered_command_tag': {'s_id7'},
        'slowdown_deffered_command_tag': {'s_id6'},
        'slowdown_remove_to_20_deferred_command_tag': {'s_id4', 's_id5'},
        'slowdown_remove_deferred_command_tag': {'s_id3', 's_id9', 's_id10'},
    }
