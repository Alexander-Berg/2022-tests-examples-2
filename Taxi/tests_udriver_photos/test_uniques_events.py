import pytest


def get_photos(pgsql, udid):
    cursor = pgsql['driver_photos'].cursor()
    cursor.execute(
        f'SELECT COUNT(*) FROM driver_photos WHERE driver_id = \'{udid}\'',
    )
    return next(cursor)[0]


@pytest.mark.parametrize(
    'consumer, message, udid1, photos1, udid2, photos2',
    [
        (
            'uniques-divide-events',
            {
                'producer': {'source': 'admin', 'login': 'login'},
                'unique_driver': {
                    'id': '000000000000000000000001',
                    'park_driver_profile_ids': [
                        {'id': 'park1_driver1'},
                        {'id': 'park2_driver2'},
                    ],
                },
                'decoupled_unique_driver': {
                    'id': '000000000000000000000003',
                    'park_driver_profile_ids': [
                        {'id': 'park3_driver3'},
                        {'id': 'park4_driver4'},
                    ],
                },
            },
            '000000000000000000000001',
            2,
            '000000000000000000000003',
            2,
        ),
        (
            'uniques-divide-events',
            {
                'producer': {'source': 'admin', 'login': 'login'},
                'unique_driver': {
                    'id': '000000000000000000000005',
                    'park_driver_profile_ids': [
                        {'id': 'park0_driver1'},
                        {'id': 'park0_driver2'},
                    ],
                },
                'decoupled_unique_driver': {
                    'id': '000000000000000000000006',
                    'park_driver_profile_ids': [
                        {'id': 'park0_driver3'},
                        {'id': 'park0_driver4'},
                    ],
                },
            },
            '000000000000000000000005',
            0,
            '000000000000000000000006',
            0,
        ),
        (
            'uniques-merge-events',
            {
                'producer': {'source': 'admin', 'login': 'login'},
                'unique_driver': {
                    'id': '000000000000000000000001',
                    'park_driver_profile_ids': [
                        {'id': 'park1_driver1'},
                        {'id': 'park2_driver2'},
                        {'id': 'park3_driver3'},
                        {'id': 'park4_driver4'},
                    ],
                },
                'merged_unique_driver': {
                    'id': '000000000000000000000002',
                    'park_driver_profile_ids': [{'id': 'park5_driver5'}],
                },
            },
            '000000000000000000000001',
            5,
            '000000000000000000000002',
            0,
        ),
        (
            'uniques-merge-events',
            {
                'producer': {'source': 'admin', 'login': 'login'},
                'unique_driver': {
                    'id': '000000000000000000000005',
                    'park_driver_profile_ids': [{'id': 'park0_driver1'}],
                },
                'merged_unique_driver': {
                    'id': '000000000000000000000002',
                    'park_driver_profile_ids': [{'id': 'park5_driver5'}],
                },
            },
            '000000000000000000000005',
            1,
            '000000000000000000000002',
            0,
        ),
    ],
)
@pytest.mark.config(
    UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS={
        '__default__': {
            '__default__': {
                'logs-enabled': False,
                'is-enabled': False,
                'sleep-ms': 5000,
            },
        },
        'udriver-photos': {
            '__default__': {
                'logs-enabled': True,
                'is-enabled': True,
                'sleep-ms': 10,
            },
        },
    },
)
async def test_uniques_events(
        taxi_udriver_photos,
        pgsql,
        logbroker_helper,
        testpoint,
        consumer,
        message,
        udid1,
        photos1,
        udid2,
        photos2,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_udriver_photos)
    await lb_helper.send_json(
        consumer,
        message,
        topic='/taxi/unique-drivers/testing/' + consumer,
        cookie='cookie',
    )

    async with taxi_udriver_photos.spawn_task('udriver-photos-' + consumer):
        await commit.wait_call()

        assert get_photos(pgsql, udid1) == photos1
        assert get_photos(pgsql, udid2) == photos2
