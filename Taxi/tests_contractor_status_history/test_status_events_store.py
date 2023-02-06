import datetime
import json

import pytest
import pytz


EVENTS_TABLES_COUNT = 16


def _make_table_name(i):
    return 'history.events_{:03d}'.format(i)


def _get_events_count_total(pgsql):
    total = 0
    cursor = pgsql['contractor_status_history'].cursor()
    for i in range(EVENTS_TABLES_COUNT):
        table_name = _make_table_name(i)
        cursor.execute(
            'WITH status_events AS'
            '(SELECT park_id, profile_id, unnest(event_list) '
            f'FROM {table_name}) '
            f'SELECT count(*) FROM status_events;',
        )
        total += cursor.fetchone()[0]

    return total


def _get_events_count_in_table(pgsql, table_name):
    cursor = pgsql['contractor_status_history'].cursor()
    cursor.execute(
        'WITH status_events AS'
        '(SELECT park_id, profile_id, unnest(event_list) '
        f'FROM {table_name}) '
        f'SELECT count(*) FROM status_events;',
    )
    return cursor.fetchone()[0]


def _to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.UTC).replace(tzinfo=None)
    return stamp


def _check_events_table(
        pgsql, table_name, event_ts, contractor_id, status, orders,
):
    cursor = pgsql['contractor_status_history'].cursor()
    cursor.execute(
        'WITH status_events AS'
        '(SELECT park_id, profile_id, unnest(event_list) as event '
        f'FROM {table_name} '
        f'WHERE (park_id,profile_id) = {contractor_id}) '
        'SELECT (event).event_ts, park_id, profile_id, (event).status,'
        '(event).order_statuses '
        'FROM status_events',
    )
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == datetime.datetime.strptime(
        event_ts, '%Y-%m-%dT%H:%M:%S.%f%z',
    )
    assert row[1] == contractor_id[0]
    assert row[2] == contractor_id[1]
    assert row[3] == status
    assert row[4] == orders


@pytest.mark.parametrize(
    'batch,table,event_ts,contractor_id,status,orders',
    [
        pytest.param(
            '{"park_id":"park1","profile_id":"contractor1","status":"online",'
            '"updated_ts":"2020-11-15T21:56:18.0+03:00","orders":[]}',
            'history.events_005',
            '2020-11-15T21:56:18.0+0300',
            ('park1', 'contractor1'),
            'online',
            '{}',
        ),
        pytest.param(
            '{"park_id":"park1","profile_id":"contractor1","status":"online",'
            '"updated_ts":"2020-11-15T21:56:18.0+03:00",'
            '"orders":[{"status":"transporting","provider":"yandex"}]}',
            'history.events_005',
            '2020-11-15T21:56:18.0+0300',
            ('park1', 'contractor1'),
            'online',
            '{transporting}',
        ),
        pytest.param(
            '{"park_id":"park1","profile_id":"contractor1","status":"online",'
            '"updated_ts":"2020-11-15T21:56:18.0+03:00",'
            '"orders":[{"status":"transporting","provider":"yandex"},'
            '{"status":"waiting","provider":"yandex"}]}',
            'history.events_005',
            '2020-11-15T21:56:18.0+0300',
            ('park1', 'contractor1'),
            'online',
            '{transporting,waiting}',
        ),
    ],
)
async def test_status_events_basic(
        taxi_contractor_status_history,
        pgsql,
        testpoint,
        mocked_time,
        batch,
        table,
        event_ts,
        contractor_id,
        status,
        orders,
):
    now = datetime.datetime(
        2020, 11, 15, 21, 56, 18, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now)

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    response = await taxi_contractor_status_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'statuses-events-consumer',
                'data': batch,
                'topic': '/taxi/testing-contractor-statuses-events',
                'cookie': 'cookie',
            },
        ),
    )
    assert response.status_code == 200
    await commit.wait_call()

    _check_events_table(pgsql, table, event_ts, contractor_id, status, orders)


@pytest.mark.parametrize(
    'batch,table,event_ts,contractor_id,status,orders',
    [
        pytest.param(
            '{"park_id":"park_1","profile_id":"contractor1","status":"online",'
            '"updated_ts":"2020-11-15T21:56:18.0+03:00",'
            '"orders":[{"status":"transporting","provider":"yandex"},'
            '{"status":"waiting","provider":"yandex"}]}',
            'history.events_005',
            '2020-11-15T21:56:18.0+0300',
            ('park_1', 'contractor1'),
            'online',
            '{transporting,waiting}',
        ),
        pytest.param(
            '{"park_id":"park1","profile_id":"contractor_1","status":"online",'
            '"updated_ts":"2020-11-15T21:56:18.0+03:00",'
            '"orders":[{"status":"transporting","provider":"yandex"},'
            '{"status":"waiting","provider":"yandex"}]}',
            'history.events_005',
            '2020-11-15T21:56:18.0+0300',
            ('park1', 'contractor_1'),
            'online',
            '{transporting,waiting}',
        ),
    ],
)
async def test_status_events_park_profile_validation(
        taxi_contractor_status_history,
        pgsql,
        testpoint,
        mocked_time,
        batch,
        table,
        event_ts,
        contractor_id,
        status,
        orders,
):
    now = datetime.datetime(
        2020, 11, 15, 21, 56, 18, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now)

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    response = await taxi_contractor_status_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'statuses-events-consumer',
                'data': batch,
                'topic': '/taxi/testing-contractor-statuses-events',
                'cookie': 'cookie',
            },
        ),
    )
    assert response.status_code == 200
    await commit.wait_call()

    cursor = pgsql['contractor_status_history'].cursor()
    cursor.execute(
        'WITH status_events AS'
        '(SELECT park_id, profile_id, unnest(event_list) as event '
        f'FROM {table} '
        f'WHERE (park_id,profile_id) = {contractor_id}) '
        'SELECT (event).event_ts, park_id, profile_id, (event).status,'
        '(event).order_statuses '
        'FROM status_events',
    )
    row = cursor.fetchone()
    assert row is None


@pytest.mark.parametrize(
    'batch,n_expected_lines,expected_table',
    [
        pytest.param(
            'some unparseable string',
            0,
            None,
            id='single line, incorrect json',
        ),
        pytest.param(
            '{"key":"value"}',
            0,
            None,
            id='single line, correct json not parseable as status event',
        ),
        pytest.param(
            '{"park_id":"park1","profile_id":"contractor1"}',
            0,
            None,
            id='single line, incomplete correct json',
        ),
        pytest.param(
            # note: single line
            '{"park_id":"park1","profile_id":"contractor1","status":"online",'
            '"updated_ts":"2020-11-15T21:56:18.0+00:00","orders":[]}',
            1,
            'history.events_005',
            id='single line, correct json',
        ),
        pytest.param(
            # note: two lines
            '{"park_id":"park1","profile_id":"contractor1","status":"online",'
            '"updated_ts":"2020-11-15T21:56:18.0+00:00","orders":[]}\n'
            'some unparseable string',
            1,
            'history.events_005',
            id='single line, correct json',
        ),
    ],
)
async def test_corrupted_message(
        taxi_contractor_status_history,
        pgsql,
        mocked_time,
        testpoint,
        batch,
        n_expected_lines,
        expected_table,
):
    now = datetime.datetime(
        2020, 11, 15, 22, 00, 00, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now)

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    response = await taxi_contractor_status_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'statuses-events-consumer',
                'data': batch,
                'topic': '/taxi/testing-contractor-statuses-events',
                'cookie': 'cookie',
            },
        ),
    )
    assert response.status_code == 200
    await commit.wait_call()

    if expected_table is not None:
        assert (
            _get_events_count_in_table(pgsql, expected_table)
            == n_expected_lines
        )
    else:
        assert _get_events_count_total(pgsql) == n_expected_lines


@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=64,
)
async def test_batch_with_different_dates(
        taxi_contractor_status_history, pgsql, mocked_time, testpoint,
):
    now = datetime.datetime(
        2020, 11, 17, 21, 00, 00, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now)

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    batch = (
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-14T23:59:59.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-15T00:56:18.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-16T00:56:18.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-17T21:00:00.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-17T21:00:01.0+00:00",'
        '"orders":[{"status":"driving","provider":"yandex"}]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"busy",'
        '"updated_ts":"2020-11-17T21:00:18.0+00:00",'
        '"orders":[{"status":"waiting","provider":"yandex"}]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-17T21:00:19.0+03:00",'
        '"orders":[{"status":"transporting","provider":"yandex"}]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"busy",'
        '"updated_ts":"2020-11-17T21:00:18.0+03:00",'
        '"orders":[{"status":"transporting","provider":"yandex"},'
        '{"status":"waiting","provider":"yandex"}]}\n'
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-17T25:00:01.0+03:00",'
        '"orders":[{"status":"transporting","provider":"yandex"}]}\n'
    )

    response = await taxi_contractor_status_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'statuses-events-consumer',
                'data': batch,
                'topic': '/taxi/testing-contractor-statuses-events',
                'cookie': 'cookie',
            },
        ),
    )
    assert response.status_code == 200
    await commit.wait_call()

    assert _get_events_count_in_table(pgsql, 'history.events_004') == 0
    assert _get_events_count_in_table(pgsql, 'history.events_005') == 0
    assert _get_events_count_in_table(pgsql, 'history.events_006') == 1
    assert _get_events_count_in_table(pgsql, 'history.events_007') == 5
    assert _get_events_count_total(pgsql) == 6


@pytest.mark.config(CONTRACTOR_STATUS_HISTORY_STORE_EVENTS_BATCH_MAX_SIZE=2)
async def test_batch_size_settings(
        taxi_contractor_status_history, pgsql, mocked_time, testpoint,
):
    now = datetime.datetime(
        2020, 11, 17, 21, 00, 00, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now)

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    batch = (
        '{"park_id":"park1","profile_id":"contractor1","status":"online",'
        '"updated_ts":"2020-11-17T21:00:00.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor2","status":"online",'
        '"updated_ts":"2020-11-17T21:00:00.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor3","status":"busy",'
        '"updated_ts":"2020-11-17T21:00:00.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor4","status":"online",'
        '"updated_ts":"2020-11-17T21:00:00.0+00:00","orders":[]}\n'
        '{"park_id":"park1","profile_id":"contractor5","status":"busy",'
        '"updated_ts":"2020-11-17T21:00:00.0+00:00","orders":[]}\n'
    )

    response = await taxi_contractor_status_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'statuses-events-consumer',
                'data': batch,
                'topic': '/taxi/testing-contractor-statuses-events',
                'cookie': 'cookie',
            },
        ),
    )
    assert response.status_code == 200
    await commit.wait_call()

    assert _get_events_count_in_table(pgsql, 'history.events_007') == 5
    assert _get_events_count_total(pgsql) == 5
