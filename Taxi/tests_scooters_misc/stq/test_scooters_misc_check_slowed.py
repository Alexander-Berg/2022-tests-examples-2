import pytest


@pytest.mark.config(
    SCOOTERS_MISC_CHECK_SLOWED_SETTINGS={
        'process_settings': [
            {
                'tags_filter': 'slowdown_was_set_car_tag*-old_state_riding',
                'area_tag': '',
                'area_tags': ['slowdown_area_tag'],
                'remove_tag': 'slowdown_was_set_car_tag',
                'add_tag': 'slowdown_remove_deferred_command_tag',
                'enable_slowdown_removal': True,
            },
            {
                'tags_filter': (
                    'slowdown_low_was_set_car_tag*-old_state_riding'
                ),
                'area_tag': '',
                'area_tags': ['slowdown_low_area_tag'],
                'remove_tag': 'slowdown_low_was_set_car_tag',
                'add_tag': 'slowdown_remove_deferred_command_tag',
                'enable_slowdown_removal': True,
            },
            {
                'tags_filter': (
                    '-old_state_riding*'
                    '-slowdown_low_was_set_car_tag*-slowdown_was_set_car_tag'
                ),
                'area_tag': '',
                'area_tags': ['slowdown_area_tag', 'slowdown_low_area_tag'],
                'remove_tag': '',
                'add_tag': 'slowdown_remove_deferred_command_tag',
                'enable_slowdown_removal': True,
                'sensor_filter': {'sensor': 'speed_can', 'less_than': 20},
            },
        ],
    },
)
async def test_simple(stq_runner, mockserver, load_json):
    details_responses = {
        '-old_state_riding*'
        '-slowdown_low_was_set_car_tag*-slowdown_was_set_car_tag': (
            'details.json'
        ),
        'slowdown_was_set_car_tag*-old_state_riding': 'details_slowdown.json',
        'slowdown_low_was_set_car_tag*-old_state_riding': (
            'details_slowdown_low.json'
        ),
    }
    tag_removes = {
        'slowdown_was_set_car_tag': ['s_id2', 's_id3', 's_id5'],
        'slowdown_low_was_set_car_tag': ['s_id1_in_vko', 's_id6'],
    }
    speed_can_map = {'s_id7': 6, 's_id8': 6, 's_id9': 12, 's_id10': 12}
    tag_added_for = set()

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def car_details(request):
        if 'tags_filter' in request.query.keys():
            tags_filter = request.query['tags_filter']
            assert tags_filter in details_responses
            return load_json(filename=details_responses[tags_filter])
        else:
            return {'cars': [], 'timestamp': 1655447659}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    async def car_telematics(request):
        speed_can = speed_can_map[request.query['car_id']]
        response = load_json(filename='telematics_state.json')
        for sensor in response['sensors']:
            if sensor['name'] == 'speed_can':
                sensor['value'] = speed_can
        return response

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    async def car_tag_remove(request):
        tags = request.json['tag_names']
        assert len(tags) == 1
        tag = tags[0]
        assert tag in tag_removes
        assert sorted(request.json['object_ids']) == sorted(tag_removes[tag])
        return {}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    async def car_tag_add(request):
        assert (
            request.json['tag_name'] == 'slowdown_'
            'remove_deferred_command_tag'
        )
        for obj in request.json['object_ids']:
            tag_added_for.add(obj)
        return {'tagged_objects': []}

    await stq_runner.scooters_misc_check_slowed.call(task_id='task_id')

    assert car_details.times_called == 4
    assert car_telematics.times_called > 0
    assert car_tag_remove.times_called == 2
    assert car_tag_add.times_called == 3

    assert tag_added_for == {
        's_id1_in_vko',
        's_id2',
        's_id3',
        's_id5',
        's_id6',
        's_id7',  # by sensors
        's_id10',  # by sensors
    }
