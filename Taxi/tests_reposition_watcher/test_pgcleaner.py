# pylint: disable=C5521, W0621
import pytest

from tests_reposition_watcher.utils import select_named


@pytest.mark.now('2019-09-01T00:00:00')
@pytest.mark.pgsql('reposition_watcher', files=['checks.sql'])
@pytest.mark.config(
    REPOSITION_WATCHER_PGCLEANER={
        'query_timeout': 10,
        'chunk_size': 1000,
        'max_size': 10000,
    },
)
async def test_clean_checks(taxi_reposition_watcher, pgsql, testpoint):
    @testpoint('old-checks-end')
    def old_checks_end(_):
        pass

    @testpoint('old-config-conditions-end')
    def old_config_conditions_end(_):
        pass

    rows = select_named(
        'SELECT config_id FROM checks.config', pgsql['reposition_watcher'],
    )

    assert rows == [
        {'config_id': 1},
        {'config_id': 2},
        {'config_id': 3},
        {'config_id': 4},
        {'config_id': 5},
    ]

    rows = select_named(
        'SELECT condition_id FROM checks.conditions',
        pgsql['reposition_watcher'],
    )

    assert rows == [
        {'condition_id': 1},
        {'condition_id': 2},
        {'condition_id': 3},
        {'condition_id': 4},
    ]

    assert (
        await taxi_reposition_watcher.post(
            '/service/cron', json={'task_name': 'pgcleaner-old-checks'},
        )
    ).status_code == 200

    await old_checks_end.wait_call()

    rows = select_named(
        'SELECT check_id FROM checks.duration', pgsql['reposition_watcher'],
    )

    assert rows == [{'check_id': 1302}]

    rows = select_named(
        'SELECT check_id FROM checks.arrival', pgsql['reposition_watcher'],
    )

    assert rows == [{'check_id': 1602}]

    # config/conditions untouched

    rows = select_named(
        'SELECT config_id FROM checks.config', pgsql['reposition_watcher'],
    )

    assert rows == [
        {'config_id': 1},
        {'config_id': 2},
        {'config_id': 3},
        {'config_id': 4},
        {'config_id': 5},
    ]

    rows = select_named(
        'SELECT condition_id FROM checks.conditions',
        pgsql['reposition_watcher'],
    )

    assert rows == [
        {'condition_id': 1},
        {'condition_id': 2},
        {'condition_id': 3},
        {'condition_id': 4},
    ]

    assert (
        await taxi_reposition_watcher.post(
            '/service/cron',
            json={'task_name': 'pgcleaner-old-config-conditions'},
        )
    ).status_code == 200

    await old_config_conditions_end.wait_call()

    # config/conditions cleaned

    rows = select_named(
        'SELECT config_id FROM checks.config', pgsql['reposition_watcher'],
    )

    assert rows == [{'config_id': 2}, {'config_id': 5}]

    rows = select_named(
        'SELECT condition_id FROM checks.conditions',
        pgsql['reposition_watcher'],
    )

    assert rows == [{'condition_id': 2}, {'condition_id': 4}]
