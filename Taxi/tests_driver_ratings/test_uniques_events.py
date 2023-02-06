import copy

import pytest


DIVIDE_LB_MSG = {
    'unique_driver': {
        'id': '000000000000000000000001',
        'park_driver_profile_ids': [{'id': 'park1_driver1'}],
    },
    'decoupled_unique_driver': {
        'id': '000000000000000000000002',
        'park_driver_profile_ids': [{'id': 'park2_driver2'}],
    },
}
DIVIDE_LB_FAILED_MSG = {
    'unique_driver': {
        'id': '000000000000000000000001',
        'park_driver_profile_ids': [{'id': 'park1_driver1'}],
    },
}
DIVIDE_LB_MSGS = [DIVIDE_LB_MSG, DIVIDE_LB_FAILED_MSG]

MERGE_LB_MSG = {
    'unique_driver': {
        'id': '000000000000000000000001',
        'park_driver_profile_ids': [{'id': 'park1_driver1'}],
    },
    'merged_unique_driver': {
        'id': '000000000000000000000002',
        'park_driver_profile_ids': [{'id': 'park2_driver2'}],
    },
}
MERGE_LB_FAILED_MSG = {
    'unique_driver': {
        'id': '000000000000000000000001',
        'park_driver_profile_ids': [{'id': 'park1_driver1'}],
    },
}
MERGE_LB_MSGS = [MERGE_LB_MSG, MERGE_LB_FAILED_MSG]


@pytest.mark.parametrize(
    'consumer, storage_mock, messages',
    [
        ('uniques-divide-events', [DIVIDE_LB_MSG], DIVIDE_LB_MSGS),
        ('uniques-merge-events', [MERGE_LB_MSG], MERGE_LB_MSGS),
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
        'driver-ratings': {
            '__default__': {
                'logs-enabled': True,
                'is-enabled': True,
                'sleep-ms': 10,
            },
        },
    },
)
async def test_uniques_events(
        taxi_driver_ratings,
        taxi_driver_ratings_monitor,
        driver_ratings_storage,
        logbroker_helper,
        testpoint,
        consumer,
        storage_mock,
        messages,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    driver_ratings_storage.set_events(storage_mock)

    lb_helper = logbroker_helper(taxi_driver_ratings)
    for message in messages:
        lb_message = copy.deepcopy(message)
        lb_message['producer'] = {'source': 'admin', 'login': 'login'}

        await lb_helper.send_json(
            consumer,
            lb_message,
            topic='/taxi/unique-drivers/testing/' + consumer,
            cookie='cookie',
        )

    async with taxi_driver_ratings.spawn_task('driver-ratings-' + consumer):
        for _ in messages:
            await commit.wait_call()

        stats = await taxi_driver_ratings_monitor.get_metrics(consumer)
        stats[consumer]['driver-ratings'].pop('events_timings')

        assert stats[consumer] == {
            'driver-ratings': {'parsing_errors': 1, 'processed': 2},
        }
