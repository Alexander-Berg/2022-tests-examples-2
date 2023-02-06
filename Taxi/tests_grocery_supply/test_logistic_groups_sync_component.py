import datetime

import pytest

from tests_grocery_supply import models

DATETIME_NOW = datetime.datetime.strptime(
    '2020-11-26 10:00:00', '%Y-%m-%d %H:%M:%S',
)


def _get_logistic_groups(pgsql):
    db = pgsql['grocery_supply']
    cursor = db.cursor()
    cursor.execute(
        'SELECT depot_id, logistic_group_id from supply.logistic_groups',
    )
    return cursor.fetchall()


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('logistic-groups-sync-periodic')
async def test_basic(taxi_grocery_supply, eats_core, pgsql):
    eats_core.set_next_response(
        [
            models.LogisticGroupResponse(1, [100], 'lavka'),
            models.LogisticGroupResponse(2, [200], 'ne_lavka'),
            models.LogisticGroupResponse(3, [300], 'lavka'),
        ],
    )

    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)

    assert result == [('100', '1'), ('300', '3')]


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('logistic-groups-sync-periodic')
async def test_empty_response(taxi_grocery_supply, pgsql, eats_core):

    eats_core.set_next_response([])

    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)
    assert not result


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('logistic-groups-sync-periodic')
async def test_bad_request(taxi_grocery_supply, pgsql, eats_core):
    eats_core.set_next_response(models.LogisticGroupsErrorResponse)

    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)
    assert not result


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('logistic-groups-sync-periodic')
async def test_updated_since(
        taxi_grocery_supply, pgsql, eats_core, mocked_time,
):

    eats_core.set_next_response(
        [
            models.LogisticGroupResponse(1, [100], 'lavka'),
            models.LogisticGroupResponse(2, [200], 'ne_lavka'),
            models.LogisticGroupResponse(3, [300], 'lavka'),
        ],
    )

    mocked_time.set(DATETIME_NOW)

    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)
    assert result == [('100', '1'), ('300', '3')]

    mocked_time.set(DATETIME_NOW + datetime.timedelta(minutes=10))

    # remove when mocked time works
    db = pgsql['grocery_supply']
    cursor = db.cursor()
    cursor.execute('TRUNCATE TABLE supply.distlock_periodic_updates')

    eats_core.set_next_response(
        [
            models.LogisticGroupResponse(11, [100], 'lavka'),
            models.LogisticGroupResponse(4, [400], 'lavka'),
        ],
    )
    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)
    assert result == [('300', '3'), ('100', '11'), ('400', '4')]


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('logistic-groups-sync-periodic')
async def test_duplicate_on_update(
        taxi_grocery_supply, pgsql, eats_core, mocked_time,
):
    eats_core.set_next_response(
        [
            models.LogisticGroupResponse(1, [100], 'lavka'),
            models.LogisticGroupResponse(2, [200], 'ne_lavka'),
            models.LogisticGroupResponse(3, [300], 'lavka'),
        ],
    )

    mocked_time.set(DATETIME_NOW)

    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)
    assert result == [('100', '1'), ('300', '3')]

    mocked_time.set(DATETIME_NOW + datetime.timedelta(minutes=10))

    # remove when mocked time works
    db = pgsql['grocery_supply']
    cursor = db.cursor()
    cursor.execute('TRUNCATE TABLE supply.distlock_periodic_updates')

    eats_core.set_next_response(
        [
            models.LogisticGroupResponse(1, [100], 'lavka'),
            models.LogisticGroupResponse(4, [400], 'lavka'),
        ],
    )

    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)
    # no changes since groups are invalid
    assert result == [('300', '3'), ('100', '1'), ('400', '4')]


# TODO: Remove when (LAVKABACKEND-3483) done
@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('logistic-groups-sync-periodic')
async def test_logistic_group_not_unique(
        taxi_grocery_supply, pgsql, eats_core, mocked_time,
):
    eats_core.set_next_response(
        [
            models.LogisticGroupResponse(1, [100, 110], 'lavka'),
            models.LogisticGroupResponse(2, [200, 210], 'ne_lavka'),
            models.LogisticGroupResponse(3, [300, 310], 'lavka'),
        ],
    )

    mocked_time.set(DATETIME_NOW)

    await taxi_grocery_supply.run_periodic_task(
        'logistic-groups-sync-periodic',
    )

    result = _get_logistic_groups(pgsql)
    assert result == [('100', '1'), ('110', '1'), ('300', '3'), ('310', '3')]
