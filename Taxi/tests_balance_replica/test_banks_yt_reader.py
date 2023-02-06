import pytest


def get_config(enabled):
    config = {
        'enabled': enabled,
        'idle_sleep_sec': 300,
        'pg_write_batch': 1000,
        'sleep_ms': 1000,
        'yt_clusters': ['hahn'],
        'yt_read_batch': 10000,
    }
    return config


def _get_cursor(pgsql):
    cursor = pgsql['balance-replica'].cursor()
    cursor.execute('SELECT revision, "offset", cluster from banks.cursor')
    result = list(row for row in cursor)
    assert len(result) < 2
    return result


def _insert_cursor(pgsql, revision, offset):
    cursor = pgsql['balance-replica'].cursor()
    cursor.execute(
        'INSERT INTO banks.cursor ' f'VALUES ({revision}, {offset}, \'hahn\')',
    )


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'banks_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_banks_schema.yaml'], static_table_data=['yt_banks.yaml'],
)
async def test_insert_all(taxi_balance_replica, pgsql, yt_apply, get_banks):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    banks = get_banks()
    assert banks == []  # No banks

    await taxi_balance_replica.run_task('banks-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (3, 'hahn')

    banks = get_banks()
    assert len(banks) == 3
    assert banks == [
        {
            'accounts': '\\"[]\\"',
            'bik': '100000001',
            'city': 'city1',
            'cor_acc': '10000000000000000001',
            'cor_acc_type': 'CRSA',
            'hidden': 0,
            'id': 1,
            'info': 'ВРФС',
            'name': 'Банк 1',
            'swift': 'BANK1',
            'update_dt': '2020-01-01T12:00:00Z',
        },
        {
            'accounts': '\\"[]\\"',
            'bik': '100000002',
            'city': 'city2',
            'cor_acc': '10000000000000000002',
            'cor_acc_type': 'CRSA',
            'hidden': 0,
            'id': 2,
            'info': 'ВРФС',
            'name': 'Банк 2',
            'swift': 'BANK2',
            'update_dt': '2020-01-01T12:00:00Z',
        },
        {
            'accounts': '\\"[]\\"',
            'bik': '100000003',
            'city': 'city3',
            'cor_acc': '10000000000000000003',
            'cor_acc_type': 'CRSA',
            'hidden': 0,
            'id': 3,
            'info': 'ВРФС',
            'name': 'Банк 3',
            'swift': 'BANK3',
            'update_dt': '2020-01-01T12:00:00Z',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'banks_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_banks_schema.yaml'], static_table_data=['yt_banks.yaml'],
)
async def test_start_from_cursor(
        taxi_balance_replica, pgsql, yt_apply, testpoint, yt_client, get_banks,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    banks = get_banks()
    assert banks == []  # No banks

    @testpoint('banks-yt-reader_revision')
    def _revision(data):
        _insert_cursor(pgsql, data['revision'], 1)

    await taxi_balance_replica.run_task('banks-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (3, 'hahn')

    banks = get_banks()
    assert len(banks) == 2
    assert banks == [
        {
            'accounts': '\\"[]\\"',
            'bik': '100000002',
            'city': 'city2',
            'cor_acc': '10000000000000000002',
            'cor_acc_type': 'CRSA',
            'hidden': 0,
            'id': 2,
            'info': 'ВРФС',
            'name': 'Банк 2',
            'swift': 'BANK2',
            'update_dt': '2020-01-01T12:00:00Z',
        },
        {
            'accounts': '\\"[]\\"',
            'bik': '100000003',
            'city': 'city3',
            'cor_acc': '10000000000000000003',
            'cor_acc_type': 'CRSA',
            'hidden': 0,
            'id': 3,
            'info': 'ВРФС',
            'name': 'Банк 3',
            'swift': 'BANK3',
            'update_dt': '2020-01-01T12:00:00Z',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'banks_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_banks_schema.yaml'], static_table_data=['yt_banks.yaml'],
)
async def test_null_cursor_when_table_ended(
        taxi_balance_replica, pgsql, yt_apply, testpoint, yt_client, get_banks,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    banks = get_banks()
    assert banks == []  # No banks

    await taxi_balance_replica.run_task('banks-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (3, 'hahn')

    # Offset turns 'NULL' after we are sure
    # that cursor has reached the end of the table
    await taxi_balance_replica.run_task('banks-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (None, 'hahn')


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'banks_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_banks_schema.yaml'],
    static_table_data=['yt_banks_error.yaml'],
)
async def test_error(
        taxi_balance_replica,
        pgsql,
        yt_apply,
        testpoint,
        yt_client,
        get_banks,
        stq,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    banks = get_banks()
    assert banks == []  # No banks

    await taxi_balance_replica.run_task('banks-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (2, 'hahn')

    banks = get_banks()
    assert banks == [
        {
            'accounts': '\\"[]\\"',
            'bik': '100000002',
            'city': 'city2',
            'cor_acc': '10000000000000000002',
            'cor_acc_type': 'CRSA',
            'hidden': 0,
            'id': 2,
            'info': 'ВРФС',
            'name': 'Банк 2',
            'swift': 'BANK2',
            'update_dt': '2020-01-01T12:00:00Z',
        },
    ]
