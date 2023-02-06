import json

import psycopg2
import pytest

from tests_eats_catalog_storage.helpers import helpers


def get_dump_lines(dump_data: bytearray):
    return [
        line for line in dump_data.decode('utf-8').strip().split('\n') if line
    ]


DEFAULT_CONFIG = pytest.mark.config(
    EATS_CATALOG_STORAGE_S3_DUMPER={
        'enabled': True,
        'backup_prefix': 'backup',
        'destination': 'catalog-dump.json',
        'period_seconds': 60,
        'timeout_seconds': 40,
        'upload_retries': 1,
        'backup_period_seconds': 1800,
    },
)

WITHOUT_PICKUP = pytest.mark.config(
    EATS_CATALOG_STORAGE_S3_DUMPER={
        'enabled': True,
        'backup_prefix': 'backup',
        'destination': 'catalog-dump.json',
        'period_seconds': 60,
        'timeout_seconds': 40,
        'upload_retries': 1,
        'backup_period_seconds': 1800,
        'disable_pickup': True,
    },
)

WITHOUT_DISABLED = pytest.mark.config(
    EATS_CATALOG_STORAGE_S3_DUMPER={
        'enabled': True,
        'backup_prefix': 'backup',
        'destination': 'catalog-dump.json',
        'period_seconds': 60,
        'timeout_seconds': 40,
        'upload_retries': 1,
        'backup_period_seconds': 1800,
        'skip_disabled_places': True,
    },
)


@DEFAULT_CONFIG
async def test_s3_dump(
        mds_s3_storage,
        taxi_eats_catalog_storage,
        load_json,
        taxi_config,
        testpoint,
        taxi_eats_catalog_storage_monitor,
):
    @testpoint('eats_catalog_storage_s3_dump_backup_created')
    def task_finished(data):
        return data

    await taxi_eats_catalog_storage.enable_testpoints()

    data = load_json('place_request.json')
    place_id = 3
    await helpers.place_upsert(taxi_eats_catalog_storage, place_id, data, 200)

    data = load_json('delivery_zone_request.json')
    zone_external_id = 'id-2'
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, data, 200,
    )

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)
    lines = get_dump_lines(dumped_data)
    assert len(lines) == 1

    response = await task_finished.wait_call()

    backup_path = response['data']['path']
    backup = mds_s3_storage.get_object(backup_path)
    assert dumped_data == backup

    metrics = await taxi_eats_catalog_storage_monitor.get_metric('s3-dumper')
    assert metrics['dump_error'] == 0
    assert metrics['dump_success'] == 1
    assert metrics['backup_error'] == 0
    assert metrics['backup_success'] == 1


@DEFAULT_CONFIG
@pytest.mark.pgsql(
    'eats_catalog_storage',
    files=['insert_new_backup_timestamp.sql', 'insert_places_and_zones.sql'],
)
async def test_s3_dump_backup_period_cancel(
        pgsql, taxi_eats_catalog_storage, testpoint,
):
    @testpoint('eats_catalog_storage_s3_dump_backup_cancelled')
    def task_finished(data):
        return data

    await taxi_eats_catalog_storage.enable_testpoints()

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    await task_finished.wait_call()


@DEFAULT_CONFIG
@pytest.mark.pgsql(
    'eats_catalog_storage',
    files=['insert_old_backup_timestamp.sql', 'insert_places_and_zones.sql'],
)
async def test_s3_dump_backup_period_update(
        pgsql, taxi_eats_catalog_storage, testpoint,
):
    @testpoint('eats_catalog_storage_s3_dump_backup_timestamp_updated')
    def task_finished(data):
        return data

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute("""SELECT id, updated_at FROM storage.s3_metadata""")
    old_record = cursor.fetchone()['updated_at']

    await taxi_eats_catalog_storage.enable_testpoints()

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    await task_finished.wait_call()

    cursor.execute("""SELECT id, updated_at FROM storage.s3_metadata""")
    new_record = cursor.fetchone()

    assert old_record is not None
    assert new_record is not None
    assert new_record != old_record


@DEFAULT_CONFIG
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_s3_dump_backup_period_empty_update(
        pgsql, taxi_eats_catalog_storage, testpoint,
):
    @testpoint('eats_catalog_storage_s3_dump_backup_timestamp_updated')
    def task_finished(data):
        return data

    await taxi_eats_catalog_storage.enable_testpoints()

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    await task_finished.wait_call()

    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute("""SELECT id, updated_at FROM storage.s3_metadata""")
    new_record = cursor.fetchone()

    assert new_record is not None


@DEFAULT_CONFIG
async def test_dumps_enabled_and_disabled_places(
        mds_s3_storage, taxi_eats_catalog_storage, load_json, taxi_config,
):
    place_data = load_json('place_request.json')

    place_data['enabled'] = True
    enabled_place_id = 3
    await helpers.place_upsert(
        taxi_eats_catalog_storage, enabled_place_id, place_data, 200,
    )

    place_data['enabled'] = False
    disabled_place_id = 4
    await helpers.place_upsert(
        taxi_eats_catalog_storage, disabled_place_id, place_data, 200,
    )

    zone_data = load_json('delivery_zone_request.json')

    zone_data['place_id'] = enabled_place_id
    zone_external_id = 'id-2'
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_data, 200,
    )
    zone_data['place_id'] = disabled_place_id
    zone_external_id = 'id-3'
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, zone_data, 200,
    )

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)
    lines = get_dump_lines(dumped_data)
    assert len(lines) == 2

    place_ids = set(json.loads(line)['place_id'] for line in lines)
    assert place_ids == set([enabled_place_id, disabled_place_id])


@DEFAULT_CONFIG
async def test_single_disabled_zone(
        mds_s3_storage, taxi_eats_catalog_storage, load_json, taxi_config,
):
    data = load_json('place_request.json')
    place_id = 3
    await helpers.place_upsert(taxi_eats_catalog_storage, place_id, data, 200)

    zone_data = load_json('delivery_zone_request.json')

    zone_data['place_id'] = place_id
    zone_data['enabled'] = False
    for zone_external_id in range(2, 5):
        zone_external_id = f'id-{zone_external_id}'
        await helpers.delivery_zone_upsert(
            taxi_eats_catalog_storage, zone_external_id, zone_data, 200,
        )

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)
    lines = get_dump_lines(dumped_data)
    assert len(lines) == 1


@DEFAULT_CONFIG
async def test_no_disabled_zones_if_there_is_enabled_one(
        mds_s3_storage, taxi_eats_catalog_storage, load_json, taxi_config,
):
    data = load_json('place_request.json')
    place_id = 3
    await helpers.place_upsert(taxi_eats_catalog_storage, place_id, data, 200)

    zone_data = load_json('delivery_zone_request.json')
    zone_data['place_id'] = place_id

    zone_data['enabled'] = True
    enabled_zone_external_id = 'id-1'
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, enabled_zone_external_id, zone_data, 200,
    )

    zone_data['enabled'] = False
    for zone_external_id in range(2, 5):
        zone_external_id = f'id-{zone_external_id}'
        await helpers.delivery_zone_upsert(
            taxi_eats_catalog_storage, zone_external_id, zone_data, 200,
        )

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)
    lines = get_dump_lines(dumped_data)
    assert len(lines) == 1

    assert (
        json.loads(lines[0])['delivery_zone_source_info']['external_id']
        == enabled_zone_external_id
    )


@DEFAULT_CONFIG
async def test_place_without_zones(
        mds_s3_storage, taxi_eats_catalog_storage, load_json, taxi_config,
):
    data = load_json('place_request.json')
    place_id = 3
    await helpers.place_upsert(taxi_eats_catalog_storage, place_id, data, 200)

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)
    lines = get_dump_lines(dumped_data)
    assert len(lines) == 1

    assert not json.loads(lines[0])['enabled']


@DEFAULT_CONFIG
async def test_double_dump_of_same_data(
        taxi_eats_catalog_storage,
        load_json,
        mocked_time,
        taxi_eats_catalog_storage_monitor,
):
    data = load_json('place_request.json')
    place_id = 3
    await helpers.place_upsert(taxi_eats_catalog_storage, place_id, data, 200)

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    metrics = await taxi_eats_catalog_storage_monitor.get_metric('s3-dumper')
    successful_dumps = metrics['dump_success']

    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )
    metrics = await taxi_eats_catalog_storage_monitor.get_metric('s3-dumper')
    assert metrics['dump_success'] == successful_dumps + 1

    mocked_time.sleep(1000)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    metrics = await taxi_eats_catalog_storage_monitor.get_metric('s3-dumper')
    assert metrics['dump_success'] == successful_dumps + 1


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
@pytest.mark.parametrize(
    'expected_lines, expected_zones, expected_places',
    [
        pytest.param(
            4,
            {100, 101, 102, 103},
            {11, 20},
            marks=DEFAULT_CONFIG,
            id='default',
        ),
        pytest.param(
            3,
            {100, 101, 102},
            {11, 20},
            marks=WITHOUT_PICKUP,
            id='without pickup',
        ),
        pytest.param(
            3,
            {101, 102, 103},
            {20},
            marks=WITHOUT_DISABLED,
            id='without disabled',
        ),
    ],
)
async def test_archived_places_zones(
        mds_s3_storage,
        taxi_eats_catalog_storage,
        taxi_config,
        expected_lines,
        expected_zones,
        expected_places,
):
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)
    lines = get_dump_lines(dumped_data)

    # check dump has archived places and zones as well
    place_ids = []
    zone_ids = []
    for line in lines:
        place_ids.append(json.loads(line)['place_id'])
        zone_ids.append(json.loads(line)['delivery_zone_id'])

    for place_id in expected_places:
        assert place_id in place_ids

    assert set(zone_ids) == expected_zones
    assert len(lines) == expected_lines


TEST_DISABLED_CONFIG = {
    'enabled': False,
    'backup_prefix': 'backup',
    'destination': 'catalog-dump.json',
    'period_seconds': 60,
    'timeout_seconds': 40,
    'upload_retries': 1,
    'backup_period_seconds': 1800,
}


@pytest.mark.config(EATS_CATALOG_STORAGE_S3_DUMPER=TEST_DISABLED_CONFIG)
async def test_s3_dump_disabled(
        mds_s3_storage, taxi_eats_catalog_storage, load_json, taxi_config,
):
    data = load_json('place_request.json')
    place_id = 3
    await helpers.place_upsert(taxi_eats_catalog_storage, place_id, data, 200)

    data = load_json('delivery_zone_request.json')
    zone_external_id = 'id-2'
    await helpers.delivery_zone_upsert(
        taxi_eats_catalog_storage, zone_external_id, data, 200,
    )

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)

    assert dumped_data is None


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
@DEFAULT_CONFIG
async def test_s3_dump_new_rating(
        mds_s3_storage, taxi_eats_catalog_storage, taxi_config, testpoint,
):
    @testpoint('eats_catalog_storage_s3_dump_backup_created')
    def _task_finished(data):
        return data

    await taxi_eats_catalog_storage.enable_testpoints()

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats-catalog-storage-s3-dump-periodic',
    )

    path = taxi_config.get('EATS_CATALOG_STORAGE_S3_DUMPER')['destination']
    dumped_data = mds_s3_storage.get_object(path)

    dumped_data = json.loads(dumped_data.decode())
    assert dumped_data['new_rating'] == {
        'rating': 5.0,
        'show': True,
        'count': 0,
    }
