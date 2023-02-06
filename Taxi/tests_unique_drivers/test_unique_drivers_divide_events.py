import bson
import pytest

from tests_unique_drivers import utils

JOB_NAME = 'unique-drivers-events-worker'


async def wait_iteration(taxi_unique_drivers, update, create, drop, testpoint):
    @testpoint(JOB_NAME + '-update')
    # pylint: disable=unused-variable
    def update_unique_failed(data):
        return {'update': update}

    @testpoint(JOB_NAME + '-create')
    # pylint: disable=unused-variable
    def create_unique_failed(data):
        return {'create': create}

    @testpoint(JOB_NAME + '-drop')
    # pylint: disable=unused-variable
    def drop_failed(data):
        return {'drop': drop}

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
        'events': {'merge': False, 'divide': True},
    },
)
@pytest.mark.now('2021-03-01T00:00:00')
async def test_divide_events_worker(taxi_unique_drivers, testpoint, mongodb):
    await taxi_unique_drivers.invalidate_caches()

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/divide',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={'licenses': [{'license': 'LICENSE_001'}]},
    )
    assert response.status_code == 200

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/divide',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={'licenses': [{'license': 'LICENSE_001'}]},
    )
    assert response.status_code == 409

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/divide',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={'licenses': [{'license': 'LICENSE_005'}]},
    )
    assert response.status_code == 200

    payloads = []
    for event in mongodb.unique_drivers_events.find():
        assert event['source'] == 'admin'
        assert event['login'] == 'user'
        event['payload']['decoupled_unique_driver'].pop('id')
        payloads.append(event['payload'])

    expected_payloads = [
        {
            'process_license_pd_ids': [
                {'id': 'LICENSE_001_ID'},
                {'id': 'LICENSE_002_ID'},
                {'id': 'LICENSE_003_ID'},
                {'id': 'LICENSE_004_ID'},
            ],
            'unique_driver': {
                'id': bson.ObjectId('000000000000000000000001'),
                'licenses': [
                    {'license': 'LICENSE_002'},
                    {'license': 'LICENSE_003'},
                    {'license': 'LICENSE_004'},
                ],
                'license_pd_ids': [
                    {'id': 'LICENSE_002_ID'},
                    {'id': 'LICENSE_003_ID'},
                    {'id': 'LICENSE_004_ID'},
                ],
                'park_driver_profile_ids': [
                    {'id': 'park3_driver3'},
                    {'id': 'park4_driver4'},
                    {'id': 'park5_driver5'},
                    {'id': 'park6_driver6'},
                ],
                'clid_driver_profile_ids': [
                    {'id': 'clid3_driver3'},
                    {'id': 'clid4_driver4'},
                    {'id': 'clid5_driver5'},
                    {'id': 'clid6_driver6'},
                ],
            },
            'decoupled_unique_driver': {
                'licenses': [{'license': 'LICENSE_001'}],
                'license_pd_ids': [{'id': 'LICENSE_001_ID'}],
                'park_driver_profile_ids': [
                    {'id': 'park1_driver1'},
                    {'id': 'park2_driver2'},
                ],
                'clid_driver_profile_ids': [
                    {'id': 'clid1_driver1'},
                    {'id': 'clid2_driver2'},
                ],
            },
        },
        {
            'process_license_pd_ids': [
                {'id': 'LICENSE_005_ID'},
                {'id': 'LICENSE_006_ID'},
            ],
            'unique_driver': {
                'id': bson.ObjectId('000000000000000000000002'),
                'licenses': [{'license': 'LICENSE_006'}],
                'license_pd_ids': [{'id': 'LICENSE_006_ID'}],
                'park_driver_profile_ids': [{'id': 'park8_driver8'}],
                'clid_driver_profile_ids': [{'id': 'clid8_driver8'}],
            },
            'decoupled_unique_driver': {
                'licenses': [{'license': 'LICENSE_005'}],
                'license_pd_ids': [{'id': 'LICENSE_005_ID'}],
                'park_driver_profile_ids': [{'id': 'park7_driver7'}],
                'clid_driver_profile_ids': [{'id': 'clid7_driver7'}],
            },
        },
    ]

    assert utils.ordered(payloads) == utils.ordered(expected_payloads)

    stats = await wait_iteration(
        taxi_unique_drivers, False, False, False, testpoint,
    )
    assert stats['divided'] == 2
    assert stats['failed'] == 0

    assert mongodb.unique_drivers_events.find().count() == 0

    old_unique_driver = utils.get_unique_driver(
        'LICENSE_002', 'licenses.license', mongodb,
    )
    old_unique_driver.pop('_id')
    assert old_unique_driver == {
        'exam_score': 2,
        'license_ids': [
            {'id': 'LICENSE_002_ID'},
            {'id': 'LICENSE_003_ID'},
            {'id': 'LICENSE_004_ID'},
        ],
        'licenses': [
            {'license': 'LICENSE_002'},
            {'license': 'LICENSE_003'},
            {'license': 'LICENSE_004'},
        ],
        'profiles': [
            {'driver_id': 'clid3_driver3'},
            {'driver_id': 'clid4_driver4'},
            {'driver_id': 'clid5_driver5'},
            {'driver_id': 'clid6_driver6'},
        ],
    }

    new_unique_driver = utils.get_unique_driver(
        'LICENSE_001', 'licenses.license', mongodb,
    )
    new_unique_driver.pop('_id')
    assert utils.ordered(new_unique_driver) == utils.ordered(
        {
            'decoupled_from': bson.ObjectId('000000000000000000000001'),
            'license_ids': [{'id': 'LICENSE_001_ID'}],
            'licenses': [{'license': 'LICENSE_001'}],
            'profiles': [
                {'driver_id': 'clid1_driver1'},
                {'driver_id': 'clid2_driver2'},
            ],
        },
    )


@pytest.mark.config(
    UNIQUE_DRIVERS_EVENTS_WORKER_SETTINGS={
        'mode': 'enabled',
        'work-interval-ms': 5000,
        'chunk-size': 100,
        'log-skipped': False,
        'events': {'merge': False, 'divide': True},
        'lb-events': {'merge': False, 'divide': True},
    },
)
@pytest.mark.now('2021-03-01T00:00:00')
async def test_divide_events_worker_testpoints(
        taxi_unique_drivers, logbroker, testpoint, mongodb,
):
    await taxi_unique_drivers.invalidate_caches()

    processed_unique_driver = utils.get_unique_driver(
        'LICENSE_001', 'licenses.license', mongodb,
    )
    expected_old_unique_driver = {
        'license_ids': [
            {'id': 'LICENSE_002_ID'},
            {'id': 'LICENSE_003_ID'},
            {'id': 'LICENSE_004_ID'},
        ],
        'licenses': [
            {'license': 'LICENSE_002'},
            {'license': 'LICENSE_003'},
            {'license': 'LICENSE_004'},
        ],
        'profiles': [
            {'driver_id': 'clid3_driver3'},
            {'driver_id': 'clid4_driver4'},
            {'driver_id': 'clid5_driver5'},
            {'driver_id': 'clid6_driver6'},
        ],
    }
    expected_new_unique_driver = {
        'license_ids': [{'id': 'LICENSE_001_ID'}],
        'licenses': [{'license': 'LICENSE_001'}],
        'profiles': [
            {'driver_id': 'clid1_driver1'},
            {'driver_id': 'clid2_driver2'},
        ],
        'decoupled_from': bson.ObjectId('000000000000000000000001'),
    }

    response = await taxi_unique_drivers.post(
        '/admin/unique-drivers/v1/divide',
        headers={'X-Yandex-Login': 'user'},
        params={'consumer': 'admin'},
        json={'licenses': [{'license': 'LICENSE_001'}]},
    )
    assert response.status_code == 200

    # fail during decoupling licenses
    stats = await wait_iteration(
        taxi_unique_drivers, True, True, True, testpoint,
    )
    assert stats['divided'] == 0
    assert stats['failed'] == 1

    assert mongodb.unique_drivers.find().count() == 2
    assert mongodb.unique_drivers_events.find().count() == 1

    assert processed_unique_driver == utils.get_unique_driver(
        'LICENSE_001', 'licenses.license', mongodb,
    )

    # can't create decoupled unique
    stats = await wait_iteration(
        taxi_unique_drivers, False, True, True, testpoint,
    )
    assert stats['divided'] == 0
    assert stats['failed'] == 1

    assert mongodb.unique_drivers.find().count() == 2
    assert mongodb.unique_drivers_events.find().count() == 1

    old_unique_driver = utils.get_unique_driver(
        'LICENSE_002', 'licenses.license', mongodb,
    )
    old_unique_driver.pop('_id')
    assert old_unique_driver == expected_old_unique_driver

    assert not utils.get_unique_driver(
        'LICENSE_001', 'licenses.license', mongodb,
    )

    # can't drop events
    stats = await wait_iteration(
        taxi_unique_drivers, False, False, True, testpoint,
    )
    assert stats['divided'] == 1
    assert stats['failed'] == 0

    assert mongodb.unique_drivers.find().count() == 3
    assert mongodb.unique_drivers_events.find().count() == 1

    old_unique_driver = utils.get_unique_driver(
        'LICENSE_002', 'licenses.license', mongodb,
    )
    old_unique_driver.pop('_id')
    old_unique_driver.pop('exam_score')
    assert utils.ordered(old_unique_driver) == utils.ordered(
        expected_old_unique_driver,
    )

    new_unique_driver = utils.get_unique_driver(
        'LICENSE_001', 'licenses.license', mongodb,
    )
    new_unique_driver.pop('_id')
    assert utils.ordered(new_unique_driver) == utils.ordered(
        expected_new_unique_driver,
    )

    assert await logbroker.wait_publish(timeout=5)
    assert len(logbroker.data) == 1

    logbroker.data[0]['data']['decoupled_unique_driver'].pop('id')
    assert utils.ordered(logbroker.data) == utils.ordered(
        [
            {
                'name': 'uniques-divide-events',
                'data': {
                    'producer': {'source': 'admin', 'login': 'user'},
                    'unique_driver': {
                        'id': '000000000000000000000001',
                        'park_driver_profile_ids': [
                            {'id': 'park3_driver3'},
                            {'id': 'park4_driver4'},
                            {'id': 'park5_driver5'},
                            {'id': 'park6_driver6'},
                        ],
                    },
                    'decoupled_unique_driver': {
                        'park_driver_profile_ids': [
                            {'id': 'park1_driver1'},
                            {'id': 'park2_driver2'},
                        ],
                    },
                },
            },
        ],
    )

    # ok
    stats = await wait_iteration(
        taxi_unique_drivers, False, False, False, testpoint,
    )
    assert stats['divided'] == 0
    assert stats['failed'] == 0

    assert mongodb.unique_drivers.find().count() == 3
    assert mongodb.unique_drivers_events.find().count() == 0

    old_unique_driver = utils.get_unique_driver(
        'LICENSE_002', 'licenses.license', mongodb,
    )
    old_unique_driver.pop('_id')
    old_unique_driver.pop('exam_score')
    assert utils.ordered(old_unique_driver) == utils.ordered(
        expected_old_unique_driver,
    )

    new_unique_driver = utils.get_unique_driver(
        'LICENSE_001', 'licenses.license', mongodb,
    )
    new_unique_driver.pop('_id')
    assert utils.ordered(new_unique_driver) == utils.ordered(
        expected_new_unique_driver,
    )
