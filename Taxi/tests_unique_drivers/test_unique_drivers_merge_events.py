import datetime
import typing as tp

import bson
import pytest

from tests_unique_drivers import utils

JOB_NAME = 'unique-drivers-events-worker'

UNIQUE_DRIVER = {
    '_id': bson.ObjectId('000000000000000000000002'),
    'created': datetime.datetime(2021, 5, 1),
    'updated': datetime.datetime(2021, 5, 23, 16, 0, 12),
    'licenses': [
        {'license': 'LICENSE_001'},
        {'license': 'LICENSE_002'},
        {'license': 'LICENSE_003'},
        {'license': 'LICENSE_004'},
    ],
    'profiles': [
        {'driver_id': 'clid1_driver1'},
        {'driver_id': 'clid2_driver2'},
        {'driver_id': 'clid3_driver3'},
        {'driver_id': 'clid4_driver4'},
    ],
    'license_ids': [
        {'id': 'LICENSE_001_ID'},
        {'id': 'LICENSE_002_ID'},
        {'id': 'LICENSE_003_ID'},
        {'id': 'LICENSE_004_ID'},
    ],
    'exam_score': 5,
    'exam_created': datetime.datetime(2021, 5, 2),
    'new_score': {'unified': {'total': 0.5}},
    'mqc_passed': datetime.datetime(2021, 5, 3),
    'fraud': True,
    'pe': {'econom': 4, 'business': -4, 'vip': 2},
    'pl': {'econom': 4, 'business': 2, 'vip': 4},
    'gl': {'econom': 'moscow', 'business': 'ekb', 'vip': 'perm'},
    'ma': {'d': datetime.datetime(2021, 5, 3)},
    'first_order_complete': {
        'completed': datetime.datetime(2021, 5, 4),
        'id': 'test_order_id1',
    },
    'blocking_by_activity': {
        'is_blocked': False,
        'blocked_until': None,
        'counter': 3,
        'timestamp': None,
    },
    'unioned_with': [
        bson.ObjectId('000000000000000000000001'),
        bson.ObjectId('200000000000000000000002'),
    ],
}
PAYLOAD = {
    'process_license_pd_ids': [
        {'id': 'LICENSE_001_ID'},
        {'id': 'LICENSE_002_ID'},
        {'id': 'LICENSE_003_ID'},
        {'id': 'LICENSE_004_ID'},
    ],
    'unique_driver': {
        'id': bson.ObjectId('000000000000000000000002'),
        'licenses': [{'license': 'LICENSE_003'}, {'license': 'LICENSE_004'}],
        'license_pd_ids': [{'id': 'LICENSE_003_ID'}, {'id': 'LICENSE_004_ID'}],
        'park_driver_profile_ids': [
            {'id': 'park3_driver3'},
            {'id': 'park4_driver4'},
        ],
        'clid_driver_profile_ids': [
            {'id': 'clid3_driver3'},
            {'id': 'clid4_driver4'},
        ],
    },
    'merged_unique_driver': {
        'id': bson.ObjectId('000000000000000000000001'),
        'licenses': [{'license': 'LICENSE_001'}, {'license': 'LICENSE_002'}],
        'license_pd_ids': [{'id': 'LICENSE_001_ID'}, {'id': 'LICENSE_002_ID'}],
        'park_driver_profile_ids': [
            {'id': 'park1_driver1'},
            {'id': 'park2_driver2'},
        ],
        'clid_driver_profile_ids': [
            {'id': 'clid1_driver1'},
            {'id': 'clid2_driver2'},
        ],
    },
}
UNIQUE_DRIVER_EMPTY = {
    '_id': bson.ObjectId('000000000000000000000004'),
    'created': datetime.datetime(2021, 5, 3),
    'updated': datetime.datetime(2021, 5, 23, 16, 0, 12),
    'licenses': [{'license': 'LICENSE_005'}, {'license': 'LICENSE_006'}],
    'profiles': [
        {'driver_id': 'clid5_driver5'},
        {'driver_id': 'clid6_driver6'},
    ],
    'license_ids': [{'id': 'LICENSE_005_ID'}, {'id': 'LICENSE_006_ID'}],
    'unioned_with': [bson.ObjectId('000000000000000000000003')],
}
PAYLOAD_EMPTY = {
    'process_license_pd_ids': [
        {'id': 'LICENSE_005_ID'},
        {'id': 'LICENSE_006_ID'},
    ],
    'unique_driver': {
        'id': bson.ObjectId('000000000000000000000004'),
        'licenses': [{'license': 'LICENSE_006'}],
        'license_pd_ids': [{'id': 'LICENSE_006_ID'}],
        'park_driver_profile_ids': [{'id': 'park6_driver6'}],
        'clid_driver_profile_ids': [{'id': 'clid6_driver6'}],
    },
    'merged_unique_driver': {
        'id': bson.ObjectId('000000000000000000000003'),
        'licenses': [{'license': 'LICENSE_005'}],
        'license_pd_ids': [{'id': 'LICENSE_005_ID'}],
        'park_driver_profile_ids': [{'id': 'park5_driver5'}],
        'clid_driver_profile_ids': [{'id': 'clid5_driver5'}],
    },
}


ITERATIONS: tp.Dict[str, bool] = {}


async def wait_iteration(taxi_unique_drivers, testpoint):
    @testpoint(JOB_NAME + '-merge-fields')
    # pylint: disable=unused-variable
    def merge_fields_failed(data):
        return {'merge-fields': ITERATIONS.get('merge-fields', False)}

    @testpoint(JOB_NAME + '-remove-log')
    # pylint: disable=unused-variable
    def remove_log_failed(data):
        return {'remove-log': ITERATIONS.get('remove-log', False)}

    @testpoint(JOB_NAME + '-remove-unique')
    # pylint: disable=unused-variable
    def remove_unique_failed(data):
        return {'remove-unique': ITERATIONS.get('remove-unique', False)}

    @testpoint(JOB_NAME + '-merge-uniques')
    # pylint: disable=unused-variable
    def merge_uniques_failed(data):
        return {'merge-uniques': ITERATIONS.get('merge-uniques', False)}

    @testpoint(JOB_NAME + '-remove-imports')
    # pylint: disable=unused-variable
    def remove_imports_failed(data):
        return {'remove-imports': ITERATIONS.get('remove-imports', False)}

    @testpoint(JOB_NAME + '-exc-merge-uniques')
    # pylint: disable=unused-variable
    def exc_merge_uniques_failed(data):
        return {
            'exc_merge-uniques': ITERATIONS.get('exc-merge-uniques', False),
        }

    @testpoint(JOB_NAME + '-finished')
    def finished(data):
        return data

    await taxi_unique_drivers.run_task(JOB_NAME)

    return (await finished.wait_call())['data']['stats']


@pytest.mark.config(
    UNIQUE_DRIVERS_EVENTS_WORKER_SETTINGS={
        'mode': 'enabled',
        'work-interval-ms': 5000,
        'chunk-size': 100,
        'log-skipped': False,
        'events': {'merge': True, 'divide': False},
    },
)
@pytest.mark.now('2021-07-01T00:00:00')
async def test_merge_events_worker(taxi_unique_drivers, testpoint, mongodb):
    await taxi_unique_drivers.invalidate_caches()

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/merge',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={
            'license': {'license': 'LICENSE_003'},
            'merge_license': {'license': 'LICENSE_001'},
        },
    )
    assert response.status_code == 200

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/merge',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={
            'license': {'license': 'LICENSE_003'},
            'merge_license': {'license': 'LICENSE_001'},
        },
    )
    assert response.status_code == 409

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/merge',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={
            'license': {'license': 'LICENSE_006'},
            'merge_license': {'license': 'LICENSE_005'},
        },
    )
    assert response.status_code == 200

    payloads = []
    for event in mongodb.unique_drivers_events.find():
        assert event['source'] == 'admin'
        assert event['login'] == 'user'
        payloads.append(event['payload'])

    assert utils.ordered(payloads) == utils.ordered([PAYLOAD, PAYLOAD_EMPTY])

    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 2
    assert stats['failed'] == 0

    assert mongodb.unique_drivers_events.find().count() == 0

    unique_driver = utils.get_unique_driver(
        'LICENSE_003', 'licenses.license', mongodb, fields=None,
    )
    expected_unique_driver = UNIQUE_DRIVER.copy()
    for field in ['updated', 'updated_ts', 'created_ts']:
        expected_unique_driver[field] = unique_driver[field]
    assert utils.ordered(unique_driver) == utils.ordered(
        expected_unique_driver,
    )

    unique_driver = utils.get_unique_driver(
        'LICENSE_006', 'licenses.license', mongodb, fields=None,
    )
    expected_unique_driver = UNIQUE_DRIVER_EMPTY.copy()
    for field in ['updated', 'updated_ts', 'created_ts']:
        expected_unique_driver[field] = unique_driver[field]
    assert utils.ordered(unique_driver) == utils.ordered(
        expected_unique_driver,
    )

    assert mongodb.unique_drivers.find().count() == 2
    assert mongodb.unique_drivers_deletions.find().count() == 2


@pytest.mark.config(
    UNIQUE_DRIVERS_EVENTS_WORKER_SETTINGS={
        'mode': 'enabled',
        'work-interval-ms': 5000,
        'chunk-size': 100,
        'log-skipped': False,
        'events': {'merge': True, 'divide': False},
        'lb-events': {'merge': True, 'divide': False},
    },
)
@pytest.mark.now('2021-07-01T00:00:00')
async def test_merge_events_worker_testpoints(
        taxi_unique_drivers, logbroker, testpoint, mongodb,
):
    await taxi_unique_drivers.invalidate_caches()

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/merge',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={
            'license': {'license': 'LICENSE_003'},
            'merge_license': {'license': 'LICENSE_001'},
        },
    )
    assert response.status_code == 200

    # failed before merging fields
    ITERATIONS['merge-fields'] = True
    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 0
    assert stats['failed'] == 1

    assert mongodb.unique_drivers.find().count() == 4
    assert mongodb.unique_drivers_deletions.find().count() == 0

    # failed to add removing log
    ITERATIONS['merge-fields'] = False
    ITERATIONS['remove-log'] = True
    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 0
    assert stats['failed'] == 1

    assert mongodb.unique_drivers.find().count() == 4
    assert mongodb.unique_drivers_deletions.find().count() == 0

    # failed to remove unique
    ITERATIONS['remove-log'] = False
    ITERATIONS['remove-unique'] = True
    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 0
    assert stats['failed'] == 1

    unique_driver = utils.get_unique_driver(
        'LICENSE_003', 'licenses.license', mongodb, fields=None,
    )
    expected_unique_driver = UNIQUE_DRIVER.copy()
    for field in [
            'licenses',
            'license_ids',
            'profiles',
            'updated',
            'updated_ts',
            'created_ts',
    ]:
        expected_unique_driver[field] = unique_driver[field]
    assert utils.ordered(unique_driver) == utils.ordered(
        expected_unique_driver,
    )

    assert mongodb.unique_drivers.find().count() == 4
    assert mongodb.unique_drivers_deletions.find().count() == 1

    # failed to merge uniques
    ITERATIONS['remove-unique'] = False
    ITERATIONS['merge-uniques'] = True
    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 0
    assert stats['failed'] == 1

    assert mongodb.unique_drivers.find().count() == 3
    assert mongodb.unique_drivers_deletions.find().count() == 1

    # duplicate during inserting unique and fail during removing new imports
    ITERATIONS['merge-uniques'] = False
    ITERATIONS['remove-imports'] = True
    mongodb.unique_drivers.update(
        {'_id': bson.ObjectId('000000000000000000000004')},
        {
            '$set': {
                'licenses': [
                    {'license': 'LICENSE_001'},
                    {'license': 'LICENSE_006'},
                ],
                'license_ids': [
                    {'id': 'LICENSE_001_ID'},
                    {'id': 'LICENSE_006_ID'},
                ],
            },
        },
    )

    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 0
    assert stats['failed'] == 1

    assert mongodb.unique_drivers.find().count() == 3
    assert mongodb.unique_drivers_deletions.find().count() == 1

    # failed to merge uniques after removing new imports
    ITERATIONS['remove-imports'] = False
    ITERATIONS['exc-merge-uniques'] = True
    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 0
    assert stats['failed'] == 1

    assert mongodb.unique_drivers.find().count() == 2
    assert mongodb.unique_drivers_deletions.find().count() == 2

    # ok
    ITERATIONS['exc-merge-uniques'] = False
    stats = await wait_iteration(taxi_unique_drivers, testpoint)
    assert stats['merged'] == 1
    assert stats['failed'] == 0

    unique_driver = utils.get_unique_driver(
        'LICENSE_003', 'licenses.license', mongodb, fields=None,
    )
    expected_unique_driver = UNIQUE_DRIVER.copy()
    for field in ['updated', 'updated_ts', 'created_ts']:
        expected_unique_driver[field] = unique_driver[field]
    assert utils.ordered(unique_driver) == utils.ordered(
        expected_unique_driver,
    )

    assert mongodb.unique_drivers.find().count() == 2
    assert mongodb.unique_drivers_deletions.find().count() == 2
    assert mongodb.unique_drivers_events.find().count() == 0

    assert await logbroker.wait_publish(timeout=5)
    assert len(logbroker.data) == 1

    assert utils.ordered(logbroker.data) == utils.ordered(
        [
            {
                'name': 'uniques-merge-events',
                'data': {
                    'producer': {'source': 'admin', 'login': 'user'},
                    'unique_driver': {
                        'id': '000000000000000000000002',
                        'park_driver_profile_ids': [
                            {'id': 'park3_driver3'},
                            {'id': 'park4_driver4'},
                        ],
                    },
                    'merged_unique_driver': {
                        'id': '000000000000000000000001',
                        'park_driver_profile_ids': [
                            {'id': 'park1_driver1'},
                            {'id': 'park2_driver2'},
                        ],
                    },
                },
            },
        ],
    )
