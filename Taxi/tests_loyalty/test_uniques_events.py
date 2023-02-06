import copy
import datetime

import pytest

from . import utils


MERGE_LB_MSG = {
    'producer': {'source': 'admin', 'login': 'login'},
    'unique_driver': {
        'id': '000000000000000000000001',
        'park_driver_profile_ids': [{'id': 'park1_driver1'}],
    },
    'merged_unique_driver': {
        'id': '000000000000000000000002',
        'park_driver_profile_ids': [{'id': 'park2_driver2'}],
    },
}


@pytest.mark.config(
    UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS={
        '__default__': {
            '__default__': {
                'logs-enabled': False,
                'is-enabled': False,
                'sleep-ms': 5000,
            },
        },
        'loyalty': {
            '__default__': {
                'logs-enabled': True,
                'is-enabled': True,
                'sleep-ms': 10,
            },
        },
    },
)
@pytest.mark.parametrize(
    'udid, merged_udid, expected_status, expected_account, expected_logs',
    [
        (
            '000000000000000000000001',
            '000000000000000000000003',
            None,
            [
                (
                    '000000000000000000000001',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'silver',
                    '{}',
                    False,
                ),
            ],
            [],
        ),
        (
            '000000000000000000000003',
            '000000000000000000000001',
            'silver',
            [
                (
                    '000000000000000000000003',
                    datetime.datetime(2021, 12, 31, 21, 0),
                    'silver',
                    '{}',
                    True,
                ),
            ],
            [
                (
                    'silver',
                    '000000000000000000000003',
                    (
                        'merge unique 000000000000000000000001 '
                        '(source: admin, login: login)'
                    ),
                    0,
                ),
            ],
        ),
        (
            '000000000000000000000001',
            '100000000000000000000005',
            'gold',
            [
                (
                    '000000000000000000000001',
                    datetime.datetime(2021, 12, 31, 21, 0),
                    'gold',
                    '{}',
                    True,
                ),
            ],
            [
                (
                    'gold',
                    '000000000000000000000001',
                    (
                        'merge unique 100000000000000000000005 '
                        '(source: admin, login: login)'
                    ),
                    0,
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql('loyalty', files=['loyalty_accounts.sql'])
@pytest.mark.now('2021-12-01T06:35:00+0500')
async def test_uniques_events(
        taxi_loyalty,
        taxi_loyalty_monitor,
        logbroker_helper,
        testpoint,
        tags,
        pgsql,
        udid,
        merged_udid,
        expected_status,
        expected_account,
        expected_logs,
):
    tags.set_append_tag(expected_status)

    @testpoint('loyalty-uniques-merge-events::ProcessMessage')
    def processed(data):
        # pylint: disable=unused-variable
        pass

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_loyalty)

    lb_message = copy.deepcopy(MERGE_LB_MSG)
    lb_message['unique_driver']['id'] = udid
    lb_message['merged_unique_driver']['id'] = merged_udid

    await lb_helper.send_json(
        'uniques-merge-events',
        lb_message,
        topic='/taxi/unique-drivers/testing/uniques-merge-events',
        cookie='cookie',
    )

    async with taxi_loyalty.spawn_task('loyalty-uniques-merge-events'):
        await commit.wait_call()

        account = utils.select_account(pgsql, udid)
        assert account == expected_account
        log = utils.select_log(pgsql, udid)
        assert log == expected_logs
