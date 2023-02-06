import copy
import datetime
import json
import operator

import pytz


def _revision_pack(revision: str):
    parts = revision.split('_')
    timestamp = int(parts[0])
    increment = int(parts[1])
    return timestamp << 32 | increment


def _mongo_revision_pack(mongo_revision: str):
    parts = mongo_revision.split('_', maxsplit=1)
    assert parts[0] == '0'
    return _revision_pack(parts[1])


def _mock_api_over_db_cache_updates(request, items, item_name):
    last_known_revision = request.json.get('last_known_revision')
    revision_from = _mongo_revision_pack(last_known_revision)
    revision = items[-1]['revision']
    if revision_from >= _mongo_revision_pack(items[-1]['revision']):
        items = []
        revision = last_known_revision

    response_json = {
        'last_modified': timestamp_to_datetime(revision),
        'last_revision': revision,
        item_name: items,
    }
    return response_json


async def test_personal_cache_full_update(
        taxi_personal_caches, mockserver, mock_personal, testpoint,
):
    @testpoint('personal-cache-finish')
    def personal_cache_testpoint(data):
        data.sort(key=operator.itemgetter('id'))
        assert data == [
            {'id': 'driver_license_pd_id_1', 'value': 'LICENSE1'},
            {'id': 'driver_license_pd_id_11', 'value': 'LICENSE11'},
            {'id': 'driver_license_pd_id_123', 'value': 'LICENSE123'},
            {'id': 'driver_license_pd_id_2', 'value': 'LICENSE2'},
            {'id': 'phone_pd_id_1', 'value': '+79998887766'},
            {'id': 'phone_pd_id_11', 'value': '+79998887777'},
            {'id': 'phone_pd_id_123', 'value': '+79998887766'},
            {'id': 'phone_pd_id_2', 'value': '+70001112233'},
        ]

    await taxi_personal_caches.enable_testpoints()
    assert personal_cache_testpoint.times_called == 1


async def test_suffixes_cache_full_update(
        taxi_personal_caches, mockserver, mock_personal, testpoint,
):
    drivers_suffixes_count = 94
    cars_suffixes_count = 40

    @testpoint('suffixes-cache-finish')
    def suffixes_cache_testpoint(data):
        suffixes_count = 0
        for cache_items in data['cache_data']:
            cache_data = copy.deepcopy(cache_items['data'])
            cache_data.sort(key=operator.itemgetter('suffix'))
            suffixes_count += len(cache_data)
            assert cache_items['data'] == cache_data

        if data['cache_name'] == 'drivers-suffixes-cache':
            assert suffixes_count == drivers_suffixes_count
        else:
            assert suffixes_count == cars_suffixes_count

    await taxi_personal_caches.enable_testpoints()
    assert suffixes_cache_testpoint.times_called == 2


def timestamp_to_datetime(timestamp):
    splitted = timestamp.split('_')
    dt_by_timestamp = datetime.datetime.fromtimestamp(
        int(splitted[0]), pytz.utc,
    )
    return dt_by_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')


async def test_suffixes_cache_remove(
        taxi_personal_caches,
        mockserver,
        mock_personal,
        mocked_time,
        testpoint,
):
    drivers_suffixes_count = 94
    cars_suffixes_count = 40

    @testpoint('suffixes-cache-finish')
    def suffixes_cache_testpoint(data):
        suffixes_count = 0
        for cache_items in data['cache_data']:
            cache_data = copy.deepcopy(cache_items['data'])
            cache_data.sort(key=operator.itemgetter('suffix'))
            suffixes_count += len(cache_data)
            assert cache_items['data'] == cache_data

        if data['cache_name'] == 'drivers-suffixes-cache':
            assert suffixes_count == drivers_suffixes_count
        else:
            assert suffixes_count == cars_suffixes_count

    await taxi_personal_caches.enable_testpoints()
    assert suffixes_cache_testpoint.times_called == 2

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/updates')
    def _driver_profiles_updates(request):
        items = [
            {
                'data': {
                    'car_id': 'no_car',
                    'full_name': {
                        'first_name': 'NeoNeo',
                        'last_name': 'Matrix',
                    },
                    'license': {'pd_id': 'driver_license_pd_id_2'},
                    'park_id': 'park2',
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_2'}],
                    'uuid': 'driver2',
                },
                'park_driver_profile_id': 'park2_driver2',
                'revision': '0_1646300750_6',
            },
        ]
        return mockserver.make_response(
            json.dumps(
                _mock_api_over_db_cache_updates(request, items, 'profiles'),
            ),
            200,
            headers={'X-Polling-Delay-Ms': '0'},
        )

    drivers_suffixes_count = 95
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-cache'],
    )
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-suffixes-cache'],
    )
    assert suffixes_cache_testpoint.times_called == 3


async def test_suffixes_cache_incremental_update_with_local_pd_cache(
        taxi_personal_caches, mockserver, mock_personal, testpoint,
):
    drivers_suffixes_count = 94
    cars_suffixes_count = 40

    @testpoint('suffixes-cache-finish')
    def suffixes_cache_testpoint(data):
        suffixes_count = 0
        for cache_items in data['cache_data']:
            cache_data = copy.deepcopy(cache_items['data'])
            cache_data.sort(key=operator.itemgetter('suffix'))
            suffixes_count += len(cache_data)
            assert cache_items['data'] == cache_data

        if data['cache_name'] == 'drivers-suffixes-cache':
            assert suffixes_count == drivers_suffixes_count
        else:
            assert suffixes_count == cars_suffixes_count

    await taxi_personal_caches.enable_testpoints()
    assert suffixes_cache_testpoint.times_called == 2

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/updates')
    def _driver_profiles_updates(request):
        items = [
            {
                'data': {
                    'car_id': 'no_car',
                    'full_name': {
                        'first_name': 'NeoNeo',
                        'last_name': 'Matrix',
                    },
                    'license': {'pd_id': 'new_licence1'},
                    'park_id': 'park2',
                    'phone_pd_ids': [
                        {'pd_id': 'new_phone1'},
                        {'pd_id': 'new_phone2'},
                    ],
                    'uuid': 'driver2',
                },
                'park_driver_profile_id': 'park2_driver2',
                'revision': '0_1646300750_6',
            },
        ]
        return mockserver.make_response(
            json.dumps(
                _mock_api_over_db_cache_updates(request, items, 'profiles'),
            ),
            200,
            headers={'X-Polling-Delay-Ms': '0'},
        )

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _personal_phone_retrieve(request):
        request_json = request.json
        request_json['items'].sort(key=operator.itemgetter('id'))
        assert request_json['items'] == [
            {'id': 'new_phone1'},
            {'id': 'new_phone2'},
        ]
        return {
            'items': [
                {'id': 'new_phone1', 'value': '+70001111834'},
                {'id': 'new_phone2', 'value': '+70001111835'},
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _personal_driver_license_retrieve(request):
        request_json = request.json
        request_json['items'].sort(key=operator.itemgetter('id'))
        assert request_json['items'] == [{'id': 'new_licence1'}]
        return {'items': [{'id': 'new_licence1', 'value': 'NEW_LICENSE'}]}

    drivers_suffixes_count = 107
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-cache'],
    )
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-suffixes-cache'],
    )
    assert suffixes_cache_testpoint.times_called == 3


async def test_suffixes_cache_incremental_update_same_doc(
        taxi_personal_caches, mockserver, mock_personal, testpoint,
):
    drivers_suffixes_count = 94
    cars_suffixes_count = 40

    @testpoint('suffixes-cache-finish')
    def suffixes_cache_testpoint(data):
        suffixes_count = 0
        for cache_items in data['cache_data']:
            cache_data = copy.deepcopy(cache_items['data'])
            cache_data.sort(key=operator.itemgetter('suffix'))
            suffixes_count += len(cache_data)
            assert cache_items['data'] == cache_data

        if data['cache_name'] == 'drivers-suffixes-cache':
            assert suffixes_count == drivers_suffixes_count
        else:
            assert suffixes_count == cars_suffixes_count

    await taxi_personal_caches.enable_testpoints()
    assert suffixes_cache_testpoint.times_called == 2

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/updates')
    def _driver_profiles_updates(request):
        items = [
            {
                'data': {
                    'car_id': 'car2',
                    'full_name': {
                        'first_name': 'Геннадий',
                        'last_name': 'Д',
                        'middle_name': 'Е',
                    },
                    'license': {'pd_id': 'driver_license_pd_id_2'},
                    'park_id': 'park2',
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_2'}],
                    'uuid': 'driver2',
                },
                'park_driver_profile_id': 'park2_driver2',
                'revision': '0_1546300750_6',
            },
        ]
        return mockserver.make_response(
            json.dumps(
                _mock_api_over_db_cache_updates(request, items, 'profiles'),
            ),
            200,
            headers={'X-Polling-Delay-Ms': '0'},
        )

    drivers_suffixes_count = 94
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-cache'],
    )
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-suffixes-cache'],
    )
    assert suffixes_cache_testpoint.times_called == 3


async def test_suffixes_cache_cars_cache_incremental_update(
        taxi_personal_caches, mockserver, testpoint,
):
    drivers_suffixes_count = 94
    cars_suffixes_count = 40

    @testpoint('suffixes-cache-finish')
    def suffixes_cache_testpoint(data):
        suffixes_count = 0
        for cache_items in data['cache_data']:
            cache_data = copy.deepcopy(cache_items['data'])
            cache_data.sort(key=operator.itemgetter('suffix'))
            suffixes_count += len(cache_data)
            assert cache_items['data'] == cache_data

        if data['cache_name'] == 'drivers-suffixes-cache':
            assert suffixes_count == drivers_suffixes_count
        else:
            assert suffixes_count == cars_suffixes_count

    await taxi_personal_caches.enable_testpoints()
    assert suffixes_cache_testpoint.times_called == 2

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/updates')
    def _cars_profiles_updates(request):
        items = [
            {
                'data': {
                    'brand': 'Mercedes',
                    'callsign': 'merin_callsign',
                    'car_id': 'car1',
                    'model': 'X6',
                    'number_normalized': 'ABC123DEF',
                    'park_id': 'park1',
                    'year': 2018,
                },
                'park_id_car_id': 'park1_car1',
                'revision': '0_1546300750_3',
            },
        ]
        return mockserver.make_response(
            json.dumps(
                _mock_api_over_db_cache_updates(request, items, 'vehicles'),
            ),
            200,
            headers={'X-Polling-Delay-Ms': '0'},
        )

    cars_suffixes_count = 48
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['cars-cache'],
    )
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['cars-suffixes-cache'],
    )
    assert suffixes_cache_testpoint.times_called == 3


async def test_suffixes_cache_incremental_update_item_with_new_park(
        taxi_personal_caches, mockserver, mock_personal, testpoint,
):
    drivers_suffixes_count = 94
    cars_suffixes_count = 40

    @testpoint('suffixes-cache-finish')
    def suffixes_cache_testpoint(data):
        suffixes_count = 0
        for cache_items in data['cache_data']:
            cache_data = copy.deepcopy(cache_items['data'])
            cache_data.sort(key=operator.itemgetter('suffix'))
            suffixes_count += len(cache_data)
            assert cache_items['data'] == cache_data

        if data['cache_name'] == 'drivers-suffixes-cache':
            assert suffixes_count == drivers_suffixes_count
        else:
            assert suffixes_count == cars_suffixes_count

    await taxi_personal_caches.enable_testpoints()
    assert suffixes_cache_testpoint.times_called == 2

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/updates')
    def _driver_profiles_updates(request):
        items = [
            {
                'data': {
                    'car_id': 'no_car',
                    'full_name': {
                        'first_name': 'NeoNeo',
                        'last_name': 'Matrix',
                    },
                    'license': {'pd_id': 'driver_license_pd_id_2'},
                    'park_id': 'NewPark',
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_2'}],
                    'uuid': 'driver2',
                },
                'park_driver_profile_id': 'NewPark_driver2',
                'revision': '0_1646300750_6',
            },
        ]
        return mockserver.make_response(
            json.dumps(
                _mock_api_over_db_cache_updates(request, items, 'profiles'),
            ),
            200,
            headers={'X-Polling-Delay-Ms': '0'},
        )

    drivers_suffixes_count = 113
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-cache'],
    )
    await taxi_personal_caches.invalidate_caches(
        clean_update=False, cache_names=['drivers-suffixes-cache'],
    )
    assert suffixes_cache_testpoint.times_called == 3
