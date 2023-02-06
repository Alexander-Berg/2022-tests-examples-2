import json

import aiohttp.web
import pytest


# request.param - list of disabled services
@pytest.fixture(name='cc_driver_card_mocks')
def _cc_driver_card_mocks(mockserver, load_json, request):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal(http_request):
        if 'personal' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())
        response = load_json('personal_phones_find_response.json')
        for item in response['items']:
            if item['value'] == request_json['value']:
                return mockserver.make_response(json=item)
        return aiohttp.web.Response(
            status=404,
            body=json.dumps({'code': 'not_found', 'message': 'Not found'}),
        )

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _driver_profiles(http_request):
        if 'driver-profiles' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())
        if not request_json['driver_phone_in_set']:
            return aiohttp.web.Response(status=400)

        response = load_json('driver_profiles_retrieve_by_phone_response.json')
        profiles = [
            profile
            for profile in response['profiles_by_phone']
            if profile['driver_phone'] in request_json['driver_phone_in_set']
        ]
        return mockserver.make_response(json={'profiles_by_phone': profiles})

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status(http_request):
        if 'driver-status' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())

        response = load_json('driver_status_statuses_response.json')
        statuses = [
            status
            for status in response['statuses']
            if {'driver_id': status['driver_id'], 'park_id': status['park_id']}
            in request_json['driver_ids']
        ]
        return mockserver.make_response(json={'statuses': statuses})

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _driver_tags(http_request):
        if 'driver-tags' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())

        response = load_json(
            'driver_tags_drivers_match_profiles_response.json',
        )
        drivers = [
            driver
            for driver in response['drivers']
            if {'uuid': driver['uuid'], 'dbid': driver['dbid']}
            in request_json['drivers']
        ]
        return mockserver.make_response(json={'drivers': drivers})

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks(http_request):
        if 'fleet-parks' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())
        assert len(request_json['query']['park']['ids']) == len(
            set(request_json['query']['park']['ids']),
        )

        response = load_json('fleet_parks_list_response.json')
        parks = [
            park
            for park in response['parks']
            if park['id'] in request_json['query']['park']['ids']
        ]
        return mockserver.make_response(json={'parks': parks})

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles(http_request):
        if 'fleet-vehicles' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())
        if not request_json['id_in_set']:
            return aiohttp.web.Response(status=400)

        response = load_json('fleet_vehicles_retrieve_response.json')
        vehicles = [
            vehicle
            for vehicle in response['vehicles']
            if vehicle['park_id_car_id'] in request_json['id_in_set']
        ]
        return mockserver.make_response(json={'vehicles': vehicles})

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_drivers(http_request):
        if 'unique-drivers' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())
        if not request_json['profile_id_in_set']:
            return aiohttp.web.Response(status=400)

        response = load_json(
            'unique_drivers_retrieve_by_profiles_response.json',
        )
        uniques = [
            unique
            for unique in response['uniques']
            if unique['park_driver_profile_id']
            in request_json['profile_id_in_set']
        ]
        return mockserver.make_response(json={'uniques': uniques})

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _driver_profiles_retrieve_by_uniques(http_request):
        if (
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques'
                in request.param
        ):
            return aiohttp.web.Response(status=500)
        assert http_request.json == {'id_in_set': ['5b055d74e6c22ea2654346b3']}
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'unique_driver_id': unique_driver_id,
                        'data': [
                            {
                                'park_id': 'some_park_id',
                                'driver_profile_id': 'some_driver_profile_id',
                                'park_driver_profile_id': (
                                    'some_park_driver_profile_id'
                                ),
                            },
                        ],
                    }
                    for unique_driver_id in http_request.json['id_in_set']
                ],
            },
        )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(http_request):
        if '/driver-profiles/v1/driver/profiles/retrieve' in request.param:
            return aiohttp.web.Response(status=500)

        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': (
                            'some_park_driver_profile_id'
                        ),
                        'data': {
                            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
                            'uuid': 'some_uuid',
                            'car_id': 'some_car_id',
                            'full_name': {
                                'first_name': 'some_first_name',
                                'middle_name': 'some_middle_name',
                                'last_name': 'some_last_name',
                            },
                            'work_status': 'some_work_status',
                            'license': {'pd_id': 'some_license_pd_id'},
                        },
                    },
                ],
            },
        )

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _driver_metrics_storage(http_request):
        if 'driver-metrics-storage' in request.param:
            return aiohttp.web.Response(status=500)

        request_json = json.loads(http_request.get_data())

        response = load_json(
            'driver_metrics_storage_activity_values_list_response.json',
        )
        activities = [
            activity
            for activity in response['items']
            if activity['unique_driver_id']
            in request_json['unique_driver_ids']
        ]
        return mockserver.make_response(json={'items': activities})


@pytest.mark.parametrize(
    ['phone', 'cc_driver_card_mocks', 'expected_code', 'expected_response'],
    [
        pytest.param(
            '+79001110101',
            ['/unique-drivers/v1/driver/profiles/retrieve_by_uniques'],
            200,
            'callcenter_support_contractors_response_1.json',
            id='callcenter_support_contractors_response_1.json',
        ),
        pytest.param(
            '+79002220202',
            ['/unique-drivers/v1/driver/profiles/retrieve_by_uniques'],
            200,
            'callcenter_support_contractors_response_2.json',
            id='callcenter_support_contractors_response_2.json',
        ),
        pytest.param(
            '+79003330303',
            ['/unique-drivers/v1/driver/profiles/retrieve_by_uniques'],
            200,
            'callcenter_support_contractors_empty_response.json',
            id='callcenter_support_contractors_empty_response.json',
        ),
        pytest.param(
            '+79000000000',
            ['/unique-drivers/v1/driver/profiles/retrieve_by_uniques'],
            200,
            'callcenter_support_contractors_empty_response.json',
            id='callcenter_support_contractors_empty_response.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'driver-tags',
            ],
            200,
            'callcenter_support_contractors_response_3.json',
            id='callcenter_support_contractors_response_3.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'driver-status',
            ],
            200,
            'callcenter_support_contractors_response_4.json',
            id='callcenter_support_contractors_response_4.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'fleet-parks',
            ],
            200,
            'callcenter_support_contractors_response_5.json',
            id='callcenter_support_contractors_response_5.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'fleet-vehicles',
            ],
            200,
            'callcenter_support_contractors_response_6.json',
            id='callcenter_support_contractors_response_6.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'unique-drivers',
            ],
            200,
            'callcenter_support_contractors_response_7.json',
            id='callcenter_support_contractors_response_7.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'driver-metrics-storage',
            ],
            200,
            'callcenter_support_contractors_response_7.json',
            id='callcenter_support_contractors_response_7_1.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'personal',
            ],
            200,
            'callcenter_support_contractors_empty_response.json',
            id='callcenter_support_contractors_empty_response_3.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'driver-profiles',
            ],
            200,
            'callcenter_support_contractors_empty_response.json',
            id='callcenter_support_contractors_empty_response_2.json',
        ),
        pytest.param(
            '+79001110101',
            [
                '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
                'driver-tags',
                'driver-status',
                'fleet-parks',
                'fleet-vehicles',
                'unique-drivers',
                'driver-metrics-storage',
                'driver-profiles',
            ],
            200,
            'callcenter_support_contractors_empty_response.json',
            id='callcenter_support_contractors_empty_response_1.json',
        ),
        pytest.param(
            '+79000000222',
            ['/unique-drivers/v1/driver/profiles/retrieve_by_uniques'],
            200,
            'callcenter_support_contractors_response_8.json',
            id='callcenter_support_contractors_response_8.json',
        ),
        pytest.param(
            '+79001110101',
            [],
            200,
            'response_more_profiles_by_unique_driver_id_1.json',
            id='more_profiles_by_unique_driver_id_1',
        ),
    ],
    indirect=['cc_driver_card_mocks'],
)
async def test_cc_v2_driver_card(
        taxi_callcenter_support_contractors,
        cc_driver_card_mocks,
        load_json,
        phone,
        expected_code,
        expected_response,
):
    response = await taxi_callcenter_support_contractors.post(
        '/cc/v1/callcenter-support-contractors/v2/driver_card',
        json={'phone': phone},
    )
    assert response.status_code == expected_code
    if expected_response:
        response_json = response.json()
        assert response_json == load_json(expected_response)


async def test_not_retrieve_profiles_with_null_driver_license(
        taxi_callcenter_support_contractors, mockserver, load_json,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal(http_request):
        assert http_request.json == {
            'primary_replica': False,
            'value': '+79672763662',
        }
        return mockserver.make_response(
            json={
                'id': '808d85827a454f12b856e75c60b05723',
                'value': '+79672763662',
            },
        )

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _driver_profiles(http_request):
        assert http_request.json == {
            'driver_phone_in_set': ['808d85827a454f12b856e75c60b05723'],
            'projection': [
                'park_driver_profile_id',
                'data.uuid',
                'data.park_id',
                'data.full_name',
                'data.license.pd_id',
                'data.work_status',
                'data.car_id',
            ],
        }

        return mockserver.make_response(
            json={
                'profiles_by_phone': [
                    {
                        'driver_phone': '92f78e99f7addaf79a4787c987e9f933',
                        'profiles': [
                            {
                                'full_name': {
                                    'first_name': 'Андрей',
                                    'last_name': 'Андреев',
                                    'middle_name': 'Адрианович',
                                },
                                'data': {
                                    'park_id': (
                                        '7ad36bc7560449998acbe2c57a75c293'
                                    ),
                                    'uuid': '1b5b0aed564348a7a668df5055b78376',
                                    'license': {'pd_id': 'some_license_pd_id'},
                                    'car_id': 'some_car_id',
                                },
                                'park_driver_profile_id': (
                                    '7ad36bc7560449998acbe2c57a75c293'
                                    '_1b5b0aed564348a7a668df5055b78376'
                                ),
                                'work_status': 'working',
                            },
                        ],
                    },
                ],
            },
        )

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status(http_request):
        assert http_request.json == {
            'driver_ids': [
                {
                    'driver_id': '1b5b0aed564348a7a668df5055b78376',
                    'park_id': '7ad36bc7560449998acbe2c57a75c293',
                },
            ],
        }
        return mockserver.make_response(
            json={
                'statuses': [
                    {
                        'driver_id': '49a09730a3ae4419b387c7c157aa0847',
                        'park_id': '7ad36bc7560449998acbe2c57a75c293',
                        'status': 'online',
                        'updated_ts': 1611162393314,
                    },
                ],
            },
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _driver_tags(http_request):
        assert http_request.json == {
            'drivers': [
                {
                    'dbid': '7ad36bc7560449998acbe2c57a75c293',
                    'uuid': '1b5b0aed564348a7a668df5055b78376',
                },
            ],
        }
        return mockserver.make_response(
            json={
                'drivers': [
                    {
                        'dbid': '7ad36bc7560449998acbe2c57a75c293',
                        'tags': [
                            '2orders',
                            'bronze',
                            'activity_85',
                            'high_activity',
                            'davos_support',
                        ],
                        'uuid': '1b5b0aed564348a7a668df5055b78376',
                    },
                ],
            },
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks(http_request):
        assert http_request.json == {
            'query': {'park': {'ids': ['7ad36bc7560449998acbe2c57a75c293']}},
        }

        return mockserver.make_response(
            json={
                'parks': [
                    {
                        'city_id': 'Москва',
                        'country_id': 'rus',
                        'demo_mode': False,
                        'driver_partner_source': 'self_assign',
                        'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                        'id': '7ad36bc7560449998acbe2c57a75c293',
                        'is_active': True,
                        'is_billing_enabled': True,
                        'is_franchising_enabled': False,
                        'locale': 'ru',
                        'login': 'cc08e4622d3545c7b8eb2318e56c6a46',
                        'name': 'Чирик',
                        'provider_config': {
                            'clid': '643753730232',
                            'type': 'production',
                        },
                    },
                ],
            },
        )

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _fleet_vehicles(http_request):
        assert http_request.json == {
            'id_in_set': ['7ad36bc7560449998acbe2c57a75c293_some_car_id'],
            'projection': [
                'park_id_car_id',
                'data.number_normalized',
                'data.model',
                'data.brand',
            ],
        }
        return mockserver.make_response(
            json={
                'vehicles': [
                    {
                        'data': {
                            'brand': 'Subaru',
                            'model': 'Legacy',
                            'number_normalized': 'A795YC777',
                        },
                        'park_id_car_id': (
                            '7ad36bc7560449998acbe2c57a75c293'
                            '_ae2c0854af7f49c1b6c656a341fdc83f'
                        ),
                    },
                ],
            },
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_drivers(http_request):
        assert http_request.json == {
            'profile_id_in_set': [
                '7ad36bc7560449998acbe2c57a75c293'
                '_1b5b0aed564348a7a668df5055b78376',
            ],
        }

        return mockserver.make_response(
            json={
                'uniques': [
                    {
                        'data': {
                            'unique_driver_id': '5b056296e6c22ea26548c8ed',
                        },
                        'park_driver_profile_id': (
                            '7ad36bc7560449998acbe2c57a75c293'
                            '_1b5b0aed564348a7a668df5055b78376'
                        ),
                    },
                ],
            },
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _driver_profiles_retrieve_by_uniques(http_request):
        assert http_request.json == {'id_in_set': ['5b056296e6c22ea26548c8ed']}
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'unique_driver_id': '5b055d74e6c22ea2654346b3',
                        'data': [
                            {
                                'park_id': '7ad36bc7560449998acbe2c57a75c293',
                                'driver_profile_id': (
                                    '1b5b0aed564348a7a668df5055b78376'
                                ),
                                'park_driver_profile_id': (
                                    '7ad36bc7560449998acbe2c57a75c293'
                                    '_1b5b0aed564348a7a668df5055b78376'
                                ),
                            },
                        ],
                    },
                ],
            },
        )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(http_request):
        assert http_request.json == {
            'id_in_set': [
                '7ad36bc7560449998acbe2c57a75c293'
                '_1b5b0aed564348a7a668df5055b78376',
            ],
            'projection': [
                'park_driver_profile_id',
                'data.uuid',
                'data.park_id',
                'data.full_name',
                'data.license.pd_id',
                'data.work_status',
                'data.car_id',
            ],
        }
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': (
                            '7ad36bc7560449998acbe2c57a75c293'
                            '_1b5b0aed564348a7a668df5055b78376'
                        ),
                        'data': {
                            'park_id': '7ad36bc7560449998acbe2c57a75c293',
                            'uuid': '1b5b0aed564348a7a668df5055b78376',
                            'car_id': 'some_car_id',
                            'full_name': {
                                'first_name': 'some_first_name',
                                'middle_name': 'some_middle_name',
                                'last_name': 'some_last_name',
                            },
                            'work_status': 'some_work_status',
                            'license': {'pd_id': 'some_license_pd_id'},
                        },
                    },
                    {
                        'park_driver_profile_id': (
                            'park_driver_profile_id_for_null_license_pd_id'
                        ),
                        'data': {
                            'park_id': 'park_id_for_null_license_pd_id',
                            'uuid': 'uuid_for_null_license_pd_id',
                            'car_id': 'some_car_id',
                            'full_name': {
                                'first_name': 'some_first_name',
                                'middle_name': 'some_middle_name',
                                'last_name': 'some_last_name',
                            },
                            'work_status': 'some_work_status',
                            'license': {
                                'pd_id': 'ee58c814298640b69a2dd2d305ca9a74',
                            },  # null license
                        },
                    },
                ],
            },
        )

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _driver_metrics_storage(http_request):
        assert http_request.json == {
            'unique_driver_ids': ['5b056296e6c22ea26548c8ed'],
        }
        return mockserver.make_response(
            json={
                'items': [
                    {
                        'unique_driver_id': '5b055d74e6c22ea2654346b3',
                        'value': 94,
                    },
                ],
            },
        )

    response = await taxi_callcenter_support_contractors.post(
        '/cc/v1/callcenter-support-contractors/v2/driver_card',
        json={'phone': '+79672763662'},
    )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json == {
        'driver_profile_groups': [
            {
                'driver_names': [],
                'drivers': [
                    {
                        'clid': '643753730232',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'is_davos': True,
                        'is_individual_entrepreneur': True,
                        'park_driver_profile_id': (
                            '7ad36bc7560449998acbe2c57a75c293'
                            '_1b5b0aed564348a7a668df5055b78376'
                        ),
                        'park_name': 'Чирик',
                        'personal_license_id': 'some_license_pd_id',
                        'tags': [
                            '2orders',
                            'bronze',
                            'activity_85',
                            'high_activity',
                            'davos_support',
                        ],
                        'uuid': '1b5b0aed564348a7a668df5055b78376',
                    },
                ],
                'is_online': False,
                'personal_license_ids': ['some_license_pd_id'],
                'unique_driver_id': 'unique_driver_id not found',
            },
        ],
    }
