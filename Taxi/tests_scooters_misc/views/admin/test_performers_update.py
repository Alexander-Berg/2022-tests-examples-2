import pytest


@pytest.mark.config(
    SCOOTERS_OPS_PERFORMERS_SETTINGS={'park_ids': ['parkid2']},
    SCOOTERS_MISC_ALLOWED_CAPACITIES={'energizer_on_car': [45]},
)
@pytest.mark.parametrize(
    'performer,expected_response,calls',
    [
        pytest.param(
            {
                'phone': '+79077632229',
                'type': 'energizer_on_car',
                'capacity': 45,
            },
            {
                'phone': '+79077632229',
                'tags_added': [
                    'scooters_batteries_capacity_45',
                    'scooters_ops_on_car_contractor',
                ],
                'tags_removed': ['scooters_batteries_capacity_10'],
                'dbid_uuid': 'parkid2_uuid2',
            },
            {
                'phones_find': 1,
                'retrieve_by_phone': 1,
                'match_profiles': 1,
                'tags_upload': 1,
            },
            id='update by phone',
        ),
        pytest.param(
            {
                'dbid_uuid': 'parkid2_uuid2',
                'type': 'energizer_on_car',
                'capacity': 45,
            },
            {
                'tags_added': [
                    'scooters_batteries_capacity_45',
                    'scooters_ops_on_car_contractor',
                ],
                'tags_removed': ['scooters_batteries_capacity_10'],
                'dbid_uuid': 'parkid2_uuid2',
            },
            {
                'phones_find': 0,
                'retrieve_by_phone': 0,
                'match_profiles': 1,
                'tags_upload': 1,
            },
            id='update by dbid_uuid',
        ),
    ],
)
async def test_handler(
        mockserver, taxi_scooters_misc, performer, expected_response, calls,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_find')
    def mock_phones_find(request):
        assert request.json['items'] == [{'value': '+79077632229'}]
        return {
            'items': [{'id': 'personal_phone_id', 'value': '+79077632229'}],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def mock_retrieve_by_phone(request):
        assert request.json == {
            'projection': ['park_driver_profile_id', 'data.park_id'],
            'driver_phone_in_set': ['personal_phone_id'],
        }
        assert request.args == {'consumer': 'scooters-misc'}
        return {
            'profiles_by_phone': [
                {
                    'driver_phone': 'personal_phone_id',
                    'profiles': [
                        {
                            'data': {'park_id': 'parkid1'},
                            'park_driver_profile_id': 'parkid1_uuid1',
                        },
                        {
                            'data': {'park_id': 'parkid2'},
                            'park_driver_profile_id': 'parkid2_uuid2',
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def mock_match_profiles(request):
        assert request.json == {
            'drivers': [{'dbid': 'parkid2', 'uuid': 'uuid2'}],
            'topics': ['candidates', 'scooters_ops'],
        }
        return {
            'drivers': [
                {
                    'dbid': 'parkid2',
                    'tags': [
                        'scooters_energizer',
                        'scooters_batteries_capacity_10',
                        'medical_card_off',
                        'medical_card',
                    ],
                    'uuid': 'uuid2',
                },
            ],
        }

    @mockserver.json_handler('/tags/v2/upload')
    def mock_tags_upload(request):
        assert request.json == {
            'provider_id': 'scooters-misc',
            'append': [
                {
                    'entity_type': 'dbid_uuid',
                    'tags': [
                        {
                            'name': 'scooters_batteries_capacity_45',
                            'entity': 'parkid2_uuid2',
                        },
                        {
                            'name': 'scooters_ops_on_car_contractor',
                            'entity': 'parkid2_uuid2',
                        },
                    ],
                },
            ],
            'remove': [
                {
                    'entity_type': 'dbid_uuid',
                    'tags': [
                        {
                            'name': 'scooters_batteries_capacity_10',
                            'entity': 'parkid2_uuid2',
                        },
                    ],
                },
            ],
        }
        return {'status': 'ok'}

    resp = await taxi_scooters_misc.post(
        '/scooters-misc/v1/admin/performers/update',
        json={'performers': [performer]},
    )

    assert resp.status_code == 200
    assert resp.json() == {'performers': [expected_response]}

    assert mock_phones_find.times_called == calls.get('phones_find', 0)
    assert mock_retrieve_by_phone.times_called == calls.get(
        'retrieve_by_phone', 0,
    )
    assert mock_match_profiles.times_called == calls.get('match_profiles', 0)
    assert mock_tags_upload.times_called == calls.get('tags_upload', 0)


async def test_capacities_config(taxi_scooters_misc):
    resp = await taxi_scooters_misc.post(
        '/scooters-misc/v1/admin/performers/update',
        json={
            'performers': [
                {
                    'phone': '+79077632229',
                    'type': 'energizer_on_car',
                    'capacity': 45,
                },
            ],
        },
    )

    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'bad-capacity',
        'message': (
            'Capacity: 45 no allowed. '
            'Allowed capacities for type energizer_on_car: []'
        ),
    }
