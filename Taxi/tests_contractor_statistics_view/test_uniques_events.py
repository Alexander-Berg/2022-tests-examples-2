import datetime

import pytest

from tests_contractor_statistics_view import pg_helpers as pgh

TIME = '2020-03-08T03:00:00.00Z'

CONFIG = {
    '__default__': {
        '__default__': {
            'logs-enabled': False,
            'is-enabled': False,
            'sleep-ms': 5000,
        },
    },
    'contractor-statistics-view': {
        '__default__': {
            'logs-enabled': True,
            'is-enabled': True,
            'sleep-ms': 10,
        },
    },
}


@pytest.mark.config(UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'udid, merged_udid, expected_number_of_udids, expected_triggers',
    [
        (
            'udid1',
            'udid5',
            1,
            [
                ('trigger02', 1, 'active', True),
                ('trigger03', 2, 'waiting', True),
            ],
        ),
        (
            'udid6',
            'udid2',
            2,
            [
                ('trigger05', 4, 'active', False),
                ('trigger06', 5, 'waiting', False),
            ],
        ),
        (
            'udid3',
            'udid4',
            3,
            [
                ('trigger07', 1, 'active', True),
                ('trigger08', 3, 'active', True),
                ('trigger09', 5, 'active', False),
                ('trigger10', 5, 'waiting', False),
                ('trigger11', 5, 'active', False),
            ],
        ),
        ('udid7', 'udid8', 0, []),
    ],
    ids=[
        'no_contractors_with_merged_udid',
        'only_contractors_with_merged_udid',
        'there_are_contractors_with_both_udids',
        'no_contractors_with_udids',
    ],
)
@pytest.mark.pgsql(
    'contractor_statistics_view',
    files=['insert_in_triggers_and_contractors.sql'],
)
async def test_uniques_merge_events(
        taxi_contractor_statistics_view,
        logbroker_helper,
        testpoint,
        pgsql,
        udid,
        merged_udid,
        expected_number_of_udids,
        expected_triggers,
):
    @testpoint(
        'contractor-statistics-view-uniques-merge-events::ProcessMessage',
    )
    def processed(data):
        # pylint: disable=unused-variable
        pass

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_contractor_statistics_view)

    lb_message = {
        'producer': {'source': 'admin', 'login': 'login'},
        'unique_driver': {
            'id': udid,
            'park_driver_profile_ids': [{'id': 'park_driver'}],
        },
        'merged_unique_driver': {
            'id': merged_udid,
            'park_driver_profile_ids': [{'id': 'park_driver'}],
        },
    }

    await lb_helper.send_json(
        'uniques-merge-events',
        lb_message,
        topic='/taxi/unique-drivers/testing/uniques-merge-events',
        cookie='cookie',
    )

    async with taxi_contractor_statistics_view.spawn_task(
            'contractor-statistics-view-uniques-merge-events',
    ):
        await commit.wait_call()

    def get_contractor_query(udid):
        return f"""
                SELECT COUNT(*)
                FROM contractor_statistics_view.contractors
                WHERE unique_driver_id = '{udid}';
                """

    cursor = pgsql['contractor_statistics_view'].cursor()

    cursor.execute(get_contractor_query(merged_udid))
    rows = cursor.fetchall()
    assert rows[0][0] == 0

    cursor.execute(get_contractor_query(udid))
    rows = cursor.fetchall()
    assert rows[0][0] == expected_number_of_udids

    def get_triggers_query(udid):
        return f"""
                SELECT trigger_name, counter, trigger_status, updated_at
                FROM contractor_statistics_view.triggers
                WHERE unique_driver_id = '{udid}'
                ORDER BY trigger_name;
                """

    cursor = pgsql['contractor_statistics_view'].cursor()

    cursor.execute(get_triggers_query(merged_udid))
    rows = cursor.fetchall()
    assert rows == []

    cursor.execute(get_triggers_query(udid))
    rows = cursor.fetchall()

    time_now = pgh.datetime_from_timestamp(
        str(datetime.datetime.now()), fmt='%Y-%m-%d %H:%M:%S.%f',
    )

    assert len(rows) == len(expected_triggers)
    for [trigger, expected_trigger] in zip(rows, expected_triggers):
        assert trigger[:3] == expected_trigger[:3]
        if expected_trigger[3]:
            assert trigger[3] == pgh.datetime_from_timestamp(TIME)
        else:
            assert (time_now - trigger[3]).total_seconds() <= 1


@pytest.mark.config(UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'udid, park_driver_profile_ids, decoupled_udid, '
    'decoupled_park_driver_profile_ids, expected_udid_contractors, '
    'expected_decoupled_udid_contractors',
    [
        ('udid0', [], 'new_udid0', [{'id': 'pid0_dpid0'}], [], []),
        (
            'udid9',
            [{'id': 'pid90_dpid90'}, {'id': 'pid92_dpid92'}],
            'decoupled_udid9',
            [
                {'id': 'pid91_dpid91'},
                {'id': 'pid93_dpid93'},
                {'id': 'pid94_dpid94'},
                {'id': 'pid95_dpid95'},
            ],
            [('udid9', 'pid90', 'dpid90')],
            [
                ('decoupled_udid9', 'pid91', 'dpid91'),
                ('decoupled_udid9', 'pid94', 'dpid94'),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'contractor_statistics_view',
    files=['insert_in_triggers_and_contractors.sql'],
)
async def test_uniques_divide_events(
        taxi_contractor_statistics_view,
        logbroker_helper,
        testpoint,
        pgsql,
        udid,
        park_driver_profile_ids,
        decoupled_udid,
        decoupled_park_driver_profile_ids,
        expected_udid_contractors,
        expected_decoupled_udid_contractors,
):
    @testpoint(
        'contractor-statistics-view-uniques-divide-events::ProcessMessage',
    )
    def processed(data):
        # pylint: disable=unused-variable
        pass

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_contractor_statistics_view)

    lb_message = {
        'producer': {'source': 'admin', 'login': 'login'},
        'unique_driver': {
            'id': udid,
            'park_driver_profile_ids': park_driver_profile_ids,
        },
        'decoupled_unique_driver': {
            'id': decoupled_udid,
            'park_driver_profile_ids': decoupled_park_driver_profile_ids,
        },
    }

    await lb_helper.send_json(
        'uniques-divide-events',
        lb_message,
        topic='/taxi/unique-drivers/testing/uniques-divide-events',
        cookie='cookie',
    )

    async with taxi_contractor_statistics_view.spawn_task(
            'contractor-statistics-view-uniques-divide-events',
    ):
        await commit.wait_call()

    def get_contractor_query(udid):
        return f"""
                SELECT unique_driver_id, park_id, driver_profile_id, updated_at
                FROM contractor_statistics_view.contractors
                WHERE unique_driver_id = '{udid}';
                """

    cursor = pgsql['contractor_statistics_view'].cursor()

    cursor.execute(get_contractor_query(udid))
    rows = cursor.fetchall()
    assert len(rows) == len(expected_udid_contractors)
    for [contractor, expected_contractor] in zip(
            rows, expected_udid_contractors,
    ):
        assert contractor[:3] == expected_contractor
        assert contractor[3] == pgh.datetime_from_timestamp(TIME)

    cursor.execute(get_contractor_query(decoupled_udid))
    rows = cursor.fetchall()
    time_now = pgh.datetime_from_timestamp(
        str(datetime.datetime.now()), fmt='%Y-%m-%d %H:%M:%S.%f',
    )
    assert len(rows) == len(expected_decoupled_udid_contractors)
    for [contractor, expected_contractor] in zip(
            rows, expected_decoupled_udid_contractors,
    ):
        assert contractor[:3] == expected_contractor
        assert (time_now - contractor[3]).total_seconds() <= 1
