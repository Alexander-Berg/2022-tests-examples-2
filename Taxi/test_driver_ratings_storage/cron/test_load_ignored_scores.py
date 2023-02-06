# pylint: disable=redefined-outer-name,duplicate-code,unused-variable
import datetime as dt

import pytest

from driver_ratings_storage.generated.cron import run_cron


@pytest.mark.pgsql(
    'driver_ratings_storage', files=['pg_driver_scores_ignored.sql'],
)
@pytest.mark.now('2019-07-16 00:00.000000')
async def test_cron(pgsql, patch):
    plugin_path = (
        'driver_ratings_storage.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
    )

    @patch(plugin_path + '.list')
    async def yt_list(*args, **kwargs):
        dates = ['2019-05-15', '2019-07-15']
        return (x for x in dates)

    @patch(plugin_path + '.exists')
    async def yt_exists(path, *args, **kwargs):
        return '2019-05-15' in path or '2019-07-15' in path

    @patch(plugin_path + '.run_sort')
    async def yt_sort(path, *args, sort_by=None, **kwargs):
        assert sort_by == ['etl_updated']
        assert '2019-05-15' in path or '2019-07-15' in path

    @patch(plugin_path + '.row_count')
    async def yt_row_count(path):
        if '2019-05-15' in str(path):
            return 4
        if '2019-07-15' in str(path):
            return 1
        raise Exception(f'Unexpected table {path}')

    @patch(plugin_path + '.read_table')
    async def yt_read(path, *args, **kwargs):
        if '2019-05-15' in str(path):
            order_ids = ['order_1_2', 'order_2_2', 'order_3_2', 'order_4_2']
            modes = ['IGNORE', 'RESTORE', 'IGNORE', 'RESTORE']
            etl_updated = '2019-05-15 15:00:00'
        elif '2019-07-15' in str(path):
            order_ids = ['order_6_2']
            modes = ['IGNORE']
            etl_updated = '2019-07-15 15:00:00'
        else:
            raise Exception(f'Unexpected table {path}')
        pairs = zip(order_ids, modes)

        def make_json(data):
            return {
                'etl_updated': etl_updated,
                'order_id': data[0],
                'action_type': data[1],
                'login_name': 'some_support_login',
            }

        return map(make_json, pairs)

    await run_cron.main(
        ['driver_ratings_storage.crontasks.load_ignored_scores', '-t', '0'],
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(
            """
            SELECT order_id, ignore_started_at
            FROM driver_ratings_storage.scores;
            """,
        )
        rows = dict(cursor)
    assert rows['order_1_2']
    assert not rows['order_2_2']
    assert rows['order_3_2'].replace(tzinfo=None) == (
        dt.datetime.fromisoformat('2019-05-14 15:00:00.000000')
    )
    assert not rows['order_4_2']
    assert rows['order_6_2']

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(
            """
            SELECT driver_id, updated_at
            FROM driver_ratings_storage.drivers;
            """,
        )
        rows = list(cursor)
    assert len(rows) == 1
    driver = rows[0]
    assert driver[1].replace(tzinfo=None) > (
        dt.datetime.fromisoformat('2019-05-14 00:00:00.000000')
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM driver_ratings_storage.driver_score_status_history;
            """,
        )
        assert cursor.fetchone()[0] == 5


@pytest.mark.pgsql(
    'driver_ratings_storage',
    files=['pg_driver_scores_ignored.sql'],
    queries=[
        """
        INSERT INTO common.events(task_id, name, created_at, details)
        VALUES ('3333333333', 'load_ignored_scores',
                '2019-08-13 15:00:00.000000',
                '{"uploaded_at": "2019-08-13 15:00:00.000000+00:00"}'::JSONB)
        ;
        """,
    ],
)
@pytest.mark.now('2019-08-16 00:00.000000')
@pytest.mark.parametrize('apply_manual_changes', [False, True])
async def test_last_uploaded_at(pgsql, patch, load, apply_manual_changes):
    plugin_path = (
        'driver_ratings_storage.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
    )

    @patch(plugin_path + '.list')
    async def yt_list(*args, **kwargs):
        return [f'2019-08-13']

    @patch(plugin_path + '.exists')
    async def yt_exists(path, *args, **kwargs):
        return '2019-08-13' in path

    @patch(plugin_path + '.run_sort')
    async def yt_sort(path, *args, sort_by=None, **kwargs):
        assert sort_by == ['etl_updated']
        assert '2019-08-13' in path

    @patch(plugin_path + '.row_count')
    async def yt_row_count(path):
        assert '2019-08-13' in path
        return 4

    @patch(plugin_path + '.read_table')
    async def yt_read(path, *args, **kwargs):
        response = [
            # MUST not be applied
            {
                'etl_updated': '2019-08-13 14:00:00',
                'order_id': 'order_1_2',
                'action_type': 'IGNORE',
                'login_name': 'some_support_login',
            },
            {
                'etl_updated': '2019-08-13 14:00:00',
                'order_id': 'order_3_2',
                'action_type': 'RESTORE',
                'login_name': 'some_support_login',
            },
            # MUST be applied
            {
                'etl_updated': '2019-08-13 16:00:00',
                'order_id': 'order_2_2',
                'action_type': 'IGNORE',
                'login_name': 'some_support_login',
            },
            {
                'etl_updated': '2019-08-13 16:00:00',
                'order_id': 'order_4_2',
                'action_type': 'RESTORE',
                'login_name': 'some_support_login',
            },
        ]
        # return iterator that can be read only once
        return (x for x in response)

    if apply_manual_changes:
        with pgsql['driver_ratings_storage'].cursor() as cursor:
            cursor.execute(load('pg_driver_score_status_history.sql'))

    await run_cron.main(
        ['driver_ratings_storage.crontasks.load_ignored_scores', '-t', '0'],
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(
            """
            SELECT order_id, ignore_started_at
            FROM driver_ratings_storage.scores;
            """,
        )
        rows = dict(cursor)

    assert not rows['order_1_2']

    assert not rows['order_4_2']

    if not apply_manual_changes:
        assert rows['order_3_2']
        assert rows['order_2_2']
    else:
        assert not rows['order_3_2']
        assert rows['order_2_2']

        assert rows['order_7_1']
        assert not rows['order_7_2']
        assert rows['order_7_3']

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM driver_ratings_storage.driver_score_status_history;
            """,
        )
        assert cursor.fetchone()[0] == 2 + (8 if apply_manual_changes else 0)


@pytest.mark.pgsql(
    'driver_ratings_storage',
    queries=[
        """
        INSERT INTO driver_ratings_storage.scores(
            order_id, driver_id, score, scored_at, ignore_started_at
        )
         VALUES
            ('order_1_2', 'driver_2', 5, '2019-05-14 00:00:00.000000', NULL);
        INSERT INTO driver_ratings_storage.drivers
          (driver_id, updated_at)
        VALUES
          ('driver_2', '2019-05-14 00:00:00.000000')
        ;
        INSERT INTO common.events(task_id, name, created_at, details)
        VALUES ('3333333333', 'load_ignored_scores',
                '2019-08-13 15:00:00.000000',
                '{"uploaded_at": "2019-08-13 15:00:00.000000+00:00"}'::JSONB)
        ;
        INSERT INTO driver_ratings_storage.driver_score_status_history
          (order_id, source, login, is_ignored, description, event_at)
        VALUES
          ('order_1_2', 'support', 'ivan', TRUE, 'Ivans description',
            '2019-08-15 15:00:00'::TIMESTAMP  AT TIME ZONE 'UTC'),
          ('order_2_2', 'support', 'ivan', TRUE, 'Petrs description',
          '2019-08-15 15:00:00'::TIMESTAMP  AT TIME ZONE 'UTC');
        """,
    ],
)
@pytest.mark.now('2019-08-16 00:00.000000')
async def test_not_existed_score_ignore_not_apply(patch, pgsql):
    plugin_path = (
        'driver_ratings_storage.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
    )

    @patch(plugin_path + '.list')
    async def yt_list(*args, **kwargs):
        return []

    await run_cron.main(
        ['driver_ratings_storage.crontasks.load_ignored_scores', '-t', '0'],
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(
            'SELECT order_id, is_applied FROM'
            ' driver_ratings_storage.driver_score_status_history'
            ' ORDER BY order_id ASC;',
        )
        rows = list(cursor)
    assert rows == [('order_1_2', True), ('order_2_2', False)]
