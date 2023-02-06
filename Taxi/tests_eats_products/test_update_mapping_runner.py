import datetime as dt

import pytest
import pytz

from tests_eats_products import utils


PERIODIC_NAME = 'update-mapping-runner'
NOW = dt.datetime(2019, 1, 1, 0, tzinfo=pytz.UTC)


def _to_utc(stamp):
    if isinstance(stamp, dt.datetime):
        if stamp.tzinfo is not None:
            stamp = stamp.astimezone(pytz.UTC)
    return stamp


def sql_get_place_update_statuses(pgsql):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        f"""
        select place_id, enabled_at,
        mapping_update_in_progress, mapping_update_started_at
        from eats_products.place_update_statuses
    """,
    )
    return {
        row[0]: {
            'place_id': row[0],
            'enabled_at': _to_utc(row[1]),
            'mapping_update_in_progress': row[2],
            'mapping_update_started_at': _to_utc(row[3]),
        }
        for row in cursor
    }


@pytest.mark.pgsql('eats_products', files=['fill_data.sql'])
@pytest.mark.parametrize(
    'update_mapping_pause_sec, update_mapping_limit, '
    'place1_updated, '
    'actual_in_progress, actual_started_at, '
    'expected_in_progress, expected_started_at',
    [
        pytest.param(
            60,
            100,
            True,
            False,
            NOW - dt.timedelta(seconds=61),
            False,
            NOW,
            id='update by in_progress',
        ),
        pytest.param(
            60,
            100,
            True,
            True,
            NOW - dt.timedelta(seconds=61),
            False,
            NOW,
            id='update by started_at',
        ),
        pytest.param(
            60,
            100,
            True,
            False,
            NOW - dt.timedelta(seconds=59),
            False,
            NOW,
            id='update by in_progress 2',
        ),
        pytest.param(
            60,
            100,
            False,
            True,
            NOW - dt.timedelta(seconds=59),
            True,
            NOW - dt.timedelta(seconds=59),
            id='dont update by started_at',
        ),
        pytest.param(
            60,
            1,
            False,
            False,
            NOW - dt.timedelta(seconds=61),
            False,
            NOW - dt.timedelta(seconds=61),
            id='dont update by limit',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_mapping_pause_sec(
        pgsql,
        mockserver,
        testpoint,
        taxi_eats_products,
        load_json,
        stq,
        stq_runner,
        taxi_config,
        update_mapping_pause_sec,
        update_mapping_limit,
        place1_updated,
        actual_in_progress,
        actual_started_at,
        expected_in_progress,
        expected_started_at,
):
    place_id1 = 1
    place_id2 = 2
    place_id3 = 3
    place_id4 = 4

    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        f"""
        insert into eats_products.place_update_statuses
        (place_id, enabled_at,
        mapping_update_in_progress, mapping_update_started_at)
        values
        ({place_id1}, '2018-01-01T00:00:00Z', {actual_in_progress},
        '{actual_started_at}'),
        ({place_id2}, '2018-01-01T01:00:00Z', {actual_in_progress}, null),
        ({place_id3}, '2018-01-01T02:00:00Z', False, null)
    """,
    )

    taxi_config.set(
        EATS_PRODUCTS_SETTINGS={
            'update_mapping_pause_sec': update_mapping_pause_sec,
            'update_mapping_limit': update_mapping_limit,
        },
    )

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_MAPPING)
    def _mock_eats_core_retail_mapping(request):
        if request.json['place_id'] == 'place1':
            return load_json('core_retail_mapping_place1.json')
        return load_json('core_retail_mapping_place2.json')

    @testpoint('eats_products::update-mapping-runner-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    if place1_updated:
        assert stq.eats_products_update_mapping.times_called == 2
    else:
        assert stq.eats_products_update_mapping.times_called == 1

    task_info = stq.eats_products_update_mapping.next_call()
    assert task_info['queue'] == 'eats_products_update_mapping'
    assert task_info['id'] == 'update_id_mapping_place2'
    assert task_info['kwargs']['place_slug'] == 'place2'

    if place1_updated:
        task_info = stq.eats_products_update_mapping.next_call()
        assert task_info['queue'] == 'eats_products_update_mapping'
        assert task_info['id'] == 'update_id_mapping_place1'
        assert task_info['kwargs']['place_slug'] == 'place1'

    # really call stq-tasks
    await stq_runner.eats_products_update_mapping.call(
        task_id=f'update_id_mapping_place2',
        kwargs={'place_slug': 'place2'},
        expect_fail=False,
    )

    if place1_updated:
        await stq_runner.eats_products_update_mapping.call(
            task_id='update_id_mapping_place1',
            kwargs={'place_slug': 'place1'},
            expect_fail=False,
        )

    result = sql_get_place_update_statuses(pgsql)
    assert (
        result[place_id1]['mapping_update_in_progress'] == expected_in_progress
    )
    assert (
        result[place_id1]['mapping_update_started_at'] == expected_started_at
    )
    assert result[place_id2]['mapping_update_in_progress'] is False
    assert result[place_id2]['mapping_update_started_at'] == NOW
    assert result[place_id3]['mapping_update_in_progress'] is False
    assert result[place_id3]['mapping_update_started_at'] is None
    assert place_id4 not in result
