import pytest


@pytest.mark.config(DISPATCH_AIRPORT_RFID_LABLES_TAGGER={'enabled': True})
@pytest.mark.now('2021-10-14T13:00:00.000000+0300')
@pytest.mark.tags_v2_index(
    tags_list=[('park_car_id', 'dbid_car_id_tagged', 'has_rfid_label')],
    topic_relations=[('airport_queue', 'has_rfid_label')],
)
async def test_rfid_labels_tagger(taxi_dispatch_airport, mockserver):
    # ХЕ35376 - not active more than 45 days
    # ХЕ35377 - already tagged
    # ХЕ35378, ХЕ35379, ХЕ35380- should be tagged

    set_tags = []

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append']
        assert len(append) == 1
        append_by_car_number = append[0]
        assert append_by_car_number['entity_type'] == 'park_car_id'

        nonlocal set_tags
        set_tags += append_by_car_number['tags']
        return {}

    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/retrieve_by_number_with_normalization',
    )
    def _fleet_vehicles(request):
        assert request.json['projection'] == ['park_id_car_id']

        if request.json['numbers_in_set'] == ['ХЕ35377']:
            return {
                'vehicles': [
                    {'park_id_car_id': 'dbid_car_id_tagged', 'data': {}},
                ],
            }
        if request.json['numbers_in_set'] == ['ХЕ35378']:
            return {
                'vehicles': [
                    {'park_id_car_id': 'dbid_car_id0', 'data': {}},
                    {'park_id_car_id': 'dbid_car_id1', 'data': {}},
                ],
            }
        if request.json['numbers_in_set'] == ['ХЕ35379']:
            return {
                'vehicles': [{'park_id_car_id': 'dbid_car_id2', 'data': {}}],
            }
        if request.json['numbers_in_set'] == ['ХЕ35380']:
            return {
                'vehicles': [{'park_id_car_id': 'dbid_car_id3', 'data': {}}],
            }
        assert False, request.json['numbers_in_set']
        return {}

    await taxi_dispatch_airport.run_periodic_task('rfid_labels_tagger_task')

    set_tags = sorted(set_tags, key=lambda x: x['entity'])

    assert set_tags == [
        {
            'entity': 'dbid_car_id0',
            'name': 'has_rfid_label',
            'ttl': 24 * 3600 * 35,
        },
        {
            'entity': 'dbid_car_id1',
            'name': 'has_rfid_label',
            'ttl': 24 * 3600 * 35,
        },
        {
            'entity': 'dbid_car_id2',
            'name': 'has_rfid_label',
            'ttl': 24 * 3600 * 34,
        },
        {
            'entity': 'dbid_car_id3',
            'name': 'has_rfid_label',
            'ttl': 24 * 3600 * 3,
        },
    ]
