import pytest

# Testpoints
PREFIX = 'eats_place_rating::sync-ratings-to-catalog-storage-'
TESTPOINT_PROCESS_DEPRECATED = PREFIX + 'process-deprecated'
TESTPOINT_PROCESS_DEPRECATED_LOOP = PREFIX + 'process-deprecated-loop'
TESTPOINT_PROCESS = PREFIX + 'process'
TESTPOINT_PROCESS_LOOP = PREFIX + 'process-loop'

CONFIG = {
    'enabled': True,
    'retry_timeout': 10,
    'retry_exponential_base': 2,
    'always_show': [4],
    'never_show': [3],
    'use_active_places_table': True,
}

CONFIG_OLD = {
    'enabled': True,
    'retry_timeout': 10,
    'retry_exponential_base': 2,
    'always_show': [4],
    'never_show': [3],
    'use_active_places_table': False,
}

CONFIG_RETAIL = {
    'default_rating': 4.9,
    'ratings': {
        'brand1': {'rating': 4.8, 'show': True},
        'brand3': {'rating': 4.7, 'show': False},
    },
}

DEFAULT_PLACES = {
    # was already synced
    1: {'need_to_sync': False, 'data': None, 'synced_revision': 2},
    2: {
        'need_to_sync': True,
        'data': {'rating': 4.6, 'show': True, 'count': 1},
        'synced_revision': 4,
    },
    3: {
        'need_to_sync': True,
        'data': {'rating': 4.5, 'show': False, 'count': 9},
        'synced_revision': 5,
    },
    4: {
        'need_to_sync': False,
        'data': {'rating': 4.5, 'show': False},
        'synced_revision': 7,
    },
    # value wasn't changed
    5: {'need_to_sync': False, 'data': None, 'synced_revision': 10},
    6: {
        'need_to_sync': True,
        'data': {'rating': 4.5, 'show': False, 'count': 1},
        'synced_revision': 11,
    },
    7: {
        'need_to_sync': True,
        'data': {'rating': 4.5, 'show': False, 'count': 3},
        'synced_revision': 12,
    },
    8: {
        'need_to_sync': True,
        'data': {'rating': 4.5, 'show': False, 'count': 1},
        'synced_revision': 13,
    },
}


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
@pytest.mark.parametrize(
    ['new_process'],
    (
        pytest.param(
            False,
            id='process_deprecated',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process_deprecated.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE=CONFIG_OLD,
                ),
            ],
        ),
        pytest.param(
            True,
            id='process',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE=CONFIG,
                ),
            ],
        ),
    ),
)
async def test_sync_to_catalog_storage(
        new_process, taxi_eats_place_rating, pgsql, mockserver, testpoint,
):
    places = DEFAULT_PLACES

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/place/rating',
    )
    def _catalog_storage(request):
        place_id = request.json['place_id']
        assert place_id in places
        if place_id in CONFIG['always_show']:
            assert (
                places[place_id]['data']['rating']
                == request.json['rating']['rating']
            )
            assert request.json['rating']['show']
        else:
            assert places[place_id]['need_to_sync']
            assert places[place_id]['data'] == request.json['rating']
        return {}

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    def _catalog_storage_places(request):
        assert request.json['place_ids'] == [6, 7, 8]
        return {'places': [], 'not_found_place_ids': []}

    @testpoint(TESTPOINT_PROCESS)
    def point_process(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_DEPRECATED)
    def point_process_deprecated(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-ratings-to-catalog-storage-periodic',
    )
    assert _catalog_storage.times_called == 6

    cursor = pgsql['eats_place_rating'].cursor()
    for place_id, data in places.items():
        cursor.execute(
            'SELECT synced_revision '
            'FROM eats_place_rating.catalog_storage_sync '
            f'WHERE place_id={place_id};',
        )
        sync_info = cursor.fetchone()
        print('place_id is: ', place_id, sync_info)
        assert sync_info
        assert sync_info[0] == data['synced_revision']

    if new_process:
        assert point_process.times_called == 1
        assert point_process_deprecated.times_called == 0
    else:
        assert point_process.times_called == 0
        assert point_process_deprecated.times_called == 1


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
@pytest.mark.parametrize(
    ['new_process'],
    (
        pytest.param(
            False,
            id='process_deprecated',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process_deprecated.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE={
                        'enabled': True,
                        'retry_timeout': 10,
                        'retry_exponential_base': 2,
                        'check_value_changed': False,
                        'use_active_places_table': False,
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            id='process',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE={
                        'enabled': True,
                        'retry_timeout': 10,
                        'retry_exponential_base': 2,
                        'check_value_changed': False,
                        'use_active_places_table': True,
                    },
                ),
            ],
        ),
    ),
)
async def test_sync_to_catalog_storage_same_value(
        new_process, taxi_eats_place_rating, pgsql, mockserver, testpoint,
):
    places = {
        # was already synced
        1: {'need_to_sync': False, 'data': None, 'synced_revision': 2},
        2: {
            'need_to_sync': True,
            'data': {'rating': 4.6, 'show': True, 'count': 1},
            'synced_revision': 4,
        },
        3: {
            'need_to_sync': True,
            'data': {'rating': 4.5, 'show': True, 'count': 9},
            'synced_revision': 5,
        },
        4: {
            'need_to_sync': True,
            'data': {'rating': 4.5, 'show': True, 'count': 1},
            'synced_revision': 7,
        },
        # value wasn't changed
        5: {
            'need_to_sync': True,
            'data': {'rating': 4.5, 'show': True, 'count': 1},
            'synced_revision': 10,
        },
        6: {
            'need_to_sync': True,
            'data': {'rating': 4.5, 'show': False, 'count': 1},
            'synced_revision': 11,
        },
        7: {
            'need_to_sync': True,
            'data': {'rating': 4.5, 'show': False, 'count': 3},
            'synced_revision': 12,
        },
        8: {
            'need_to_sync': True,
            'data': {'rating': 4.5, 'show': False, 'count': 1},
            'synced_revision': 13,
        },
    }

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/place/rating',
    )
    def _catalog_storage(request):
        place_id = request.json['place_id']
        assert place_id in places
        assert places[place_id]['need_to_sync']
        assert places[place_id]['data'] == request.json['rating']
        return {}

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    def _catalog_storage_places(request):
        assert request.json['place_ids'] == [6, 7, 8]
        return {'places': [], 'not_found_place_ids': []}

    @testpoint(TESTPOINT_PROCESS)
    def point_process(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_DEPRECATED)
    def point_process_deprecated(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-ratings-to-catalog-storage-periodic',
    )
    assert _catalog_storage.times_called == 7

    cursor = pgsql['eats_place_rating'].cursor()
    for place_id, data in places.items():
        cursor.execute(
            'SELECT synced_revision '
            'FROM eats_place_rating.catalog_storage_sync '
            f'WHERE place_id={place_id};',
        )
        sync_info = cursor.fetchone()
        print('place_id is: ', place_id)
        assert sync_info
        assert sync_info[0] == data['synced_revision']

    if new_process:
        assert point_process.times_called == 1
        assert point_process_deprecated.times_called == 0
    else:
        assert point_process.times_called == 0
        assert point_process_deprecated.times_called == 1


@pytest.mark.config(EATS_PLACE_RATING_RETAIL_RATING=CONFIG_RETAIL)
@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
@pytest.mark.parametrize(
    ['new_process'],
    (
        pytest.param(
            False,
            id='process_deprecated',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process_deprecated.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE=CONFIG_OLD,
                ),
            ],
        ),
        pytest.param(
            True,
            id='process',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE=CONFIG,
                ),
            ],
        ),
    ),
)
async def test_sync_to_catalog_storage_retail(
        new_process, taxi_eats_place_rating, pgsql, mockserver, testpoint,
):
    places = {
        # was already synced
        1: {'need_to_sync': False, 'data': None, 'synced_revision': 2},
        2: {
            'need_to_sync': True,
            'data': {'rating': 4.6, 'show': True, 'count': 1},
            'synced_revision': 4,
        },
        3: {
            'need_to_sync': True,
            'data': {'rating': 4.5, 'show': False, 'count': 9},
            'synced_revision': 5,
        },
        4: {
            'need_to_sync': False,
            'data': {'rating': 4.5, 'show': False, 'count': 1},
            'synced_revision': 7,
        },
        # value wasn't changed
        5: {'need_to_sync': False, 'data': None, 'synced_revision': 10},
        6: {
            'need_to_sync': True,
            'data': {'rating': 4.8, 'show': True, 'count': 1},
            'synced_revision': 11,
        },
        7: {
            'need_to_sync': True,
            'data': {'rating': 4.9, 'show': False, 'count': 3},
            'synced_revision': 12,
        },
        8: {
            'need_to_sync': True,
            'data': {'rating': 4.7, 'show': False, 'count': 1},
            'synced_revision': 13,
        },
    }

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/place/rating',
    )
    def _catalog_storage(request):
        place_id = request.json['place_id']
        assert place_id in places
        if place_id in CONFIG['always_show']:
            assert (
                places[place_id]['data']['rating']
                == request.json['rating']['rating']
            )
            assert request.json['rating']['show']
        else:
            assert places[place_id]['need_to_sync']
            assert places[place_id]['data'] == request.json['rating']
        return {}

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    def _catalog_storage_places(request):
        assert request.json['place_ids'] == [6, 7, 8]
        return {
            'places': [
                {
                    'id': 6,
                    'business': 'shop',
                    'brand': {
                        'id': 1,
                        'slug': 'brand1',
                        'name': 'name1',
                        'picture_scale_type': 'aspect_fit',
                    },
                    'revision_id': 20,
                    'updated_at': '2021-08-01T00:00:0Z',
                },
                {
                    'id': 7,
                    'business': 'shop',
                    'brand': {
                        'id': 2,
                        'slug': 'brand2',
                        'name': 'name2',
                        'picture_scale_type': 'aspect_fit',
                    },
                    'revision_id': 21,
                    'updated_at': '2021-08-01T00:00:0Z',
                },
                {
                    'id': 8,
                    'business': 'shop',
                    'brand': {
                        'id': 2,
                        'slug': 'brand3',
                        'name': 'name3',
                        'picture_scale_type': 'aspect_fit',
                    },
                    'revision_id': 22,
                    'updated_at': '2021-08-01T00:00:0Z',
                },
            ],
            'not_found_place_ids': [],
        }

    @testpoint(TESTPOINT_PROCESS)
    def point_process(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_DEPRECATED)
    def point_process_deprecated(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-ratings-to-catalog-storage-periodic',
    )
    assert _catalog_storage.times_called == 6

    cursor = pgsql['eats_place_rating'].cursor()
    for place_id, data in places.items():
        cursor.execute(
            'SELECT synced_revision '
            'FROM eats_place_rating.catalog_storage_sync '
            f'WHERE place_id={place_id};',
        )
        sync_info = cursor.fetchone()
        print('place_id is: ', place_id, sync_info)
        assert sync_info
        assert sync_info[0] == data['synced_revision']

    if new_process:
        assert point_process.times_called == 1
        assert point_process_deprecated.times_called == 0
    else:
        assert point_process.times_called == 0
        assert point_process_deprecated.times_called == 1


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
@pytest.mark.parametrize(
    ['new_process'],
    (
        pytest.param(
            False,
            id='process_deprecated',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process_deprecated.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE={
                        'enabled': True,
                        'retry_timeout': 10,
                        'retry_exponential_base': 2,
                        'always_show': [4],
                        'never_show': [3],
                        'batch_size': 1,
                        'use_active_places_table': False,
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            id='process',
            marks=[
                pytest.mark.pgsql(
                    'eats_place_rating',
                    files=('pg_eats_place_rating_process.sql',),
                ),
                pytest.mark.config(
                    EATS_PLACE_RATING_SYNC_TO_CATALOG_STORAGE={
                        'enabled': True,
                        'retry_timeout': 10,
                        'retry_exponential_base': 2,
                        'always_show': [4],
                        'never_show': [3],
                        'batch_size': 1,
                        'use_active_places_table': True,
                    },
                ),
            ],
        ),
    ),
)
async def test_sync_to_catalog_storage_with_batch_size(
        new_process, taxi_eats_place_rating, pgsql, mockserver, testpoint,
):
    places = DEFAULT_PLACES

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/place/rating',
    )
    def _catalog_storage(request):
        place_id = request.json['place_id']
        assert place_id in places
        if place_id in CONFIG['always_show']:
            assert (
                places[place_id]['data']['rating']
                == request.json['rating']['rating']
            )
            assert request.json['rating']['show']
        else:
            assert places[place_id]['need_to_sync']
            assert places[place_id]['data'] == request.json['rating']
        return {}

    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    def _catalog_storage_places(request):
        return {'places': [], 'not_found_place_ids': []}

    @testpoint(TESTPOINT_PROCESS)
    def point_process(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_LOOP)
    def point_process_loop(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_DEPRECATED)
    def point_process_deprecated(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_DEPRECATED_LOOP)
    def point_process_deprecated_loop(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-ratings-to-catalog-storage-periodic',
    )

    assert _catalog_storage.times_called == 6

    cursor = pgsql['eats_place_rating'].cursor()
    for place_id, data in places.items():
        cursor.execute(
            'SELECT synced_revision '
            'FROM eats_place_rating.catalog_storage_sync '
            f'WHERE place_id={place_id};',
        )
        sync_info = cursor.fetchone()
        print('place_id is: ', place_id, sync_info)
        assert sync_info
        assert sync_info[0] == data['synced_revision']

    if new_process:
        assert point_process.times_called == 1
        assert point_process_loop.times_called == 8
        assert point_process_deprecated.times_called == 0
    else:
        assert point_process.times_called == 0
        assert point_process_deprecated.times_called == 1
        assert point_process_deprecated_loop.times_called == 8
