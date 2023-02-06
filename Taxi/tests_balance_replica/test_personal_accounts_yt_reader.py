import pytest


def get_config(enabled):
    config = {
        'enabled': enabled,
        'idle_sleep_sec': 300,
        'pg_write_batch': 1000,
        'sleep_ms': 1000,
        'yt_clusters': ['hahn', 'arnold'],
        'yt_read_batch': 10000,
    }
    return config


def _get_cursor(pgsql):
    cursor = pgsql['balance-replica'].cursor()
    cursor.execute('SELECT * from personal_accounts.cursor')
    result = list(row for row in cursor)
    assert len(result) < 2
    return result


def _insert_cursor(pgsql, revision, offset):
    cursor = pgsql['balance-replica'].cursor()
    cursor.execute(
        'INSERT INTO personal_accounts.cursor '
        f'VALUES ({revision}, {offset}, \'hahn\')',
    )


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_personal_accounts_schema.yaml'],
    static_table_data=['yt_personal_accounts.yaml'],
)
async def test_insert_all(
        taxi_balance_replica, pgsql, yt_apply, get_personal_accounts,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    accounts = get_personal_accounts()
    assert accounts == []  # No accounts

    await taxi_balance_replica.run_task('personal-accounts-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (2, 'hahn')

    accounts = get_personal_accounts()
    assert len(accounts) == 2
    assert accounts == [
        {
            'id': 0,
            'version': 0,
            'contract_id': 0,
            'external_id': 'ЛСТ-0',
            'service_code': 'YANDEX_SERVICE',
        },
        {
            'id': 1,
            'version': 0,
            'contract_id': 1,
            'external_id': 'ЛСТ-1',
            'service_code': 'AGENT_REWARD',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_personal_accounts_schema.yaml'],
    static_table_data=['yt_personal_accounts_with_null.yaml'],
)
async def test_skip_null(
        taxi_balance_replica, pgsql, yt_apply, get_personal_accounts,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    accounts = get_personal_accounts()
    assert accounts == []  # No accounts

    await taxi_balance_replica.run_task('personal-accounts-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (3, 'hahn')

    accounts = get_personal_accounts()
    assert len(accounts) == 1
    assert accounts == [
        {
            'id': 0,
            'version': 0,
            'contract_id': 0,
            'external_id': 'ЛСТ-0',
            'service_code': 'YANDEX_SERVICE',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_personal_accounts_schema.yaml'],
    static_table_data=['yt_personal_accounts_second_version.yaml'],
)
@pytest.mark.pgsql(
    'balance-replica',
    queries=[
        'INSERT INTO personal_accounts.personal_account('
        'id, version, contract_id, external_id, service_code'
        ') '
        'VALUES (0, 0, 0, \'ЛСТ-0\', \'YANDEX_SERVICE\'),'
        '       (1, 0, 1, \'ЛСТ-1\', \'AGENT_REWARD\')',
    ],
)
async def test_insert_only_new_version(
        taxi_balance_replica,
        pgsql,
        yt_apply,
        yt_client,
        get_personal_accounts,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    accounts = get_personal_accounts()
    assert len(accounts) == 2

    await taxi_balance_replica.run_task('personal-accounts-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (2, 'hahn')

    accounts = get_personal_accounts()
    assert len(accounts) == 3
    assert accounts == [
        {
            'id': 0,
            'version': 0,
            'contract_id': 0,
            'external_id': 'ЛСТ-0',
            'service_code': 'YANDEX_SERVICE',
        },
        {
            'id': 1,
            'version': 0,
            'contract_id': 1,
            'external_id': 'ЛСТ-1',
            'service_code': 'AGENT_REWARD',
        },
        {
            'id': 1,
            'version': 1,
            'contract_id': 1,
            'external_id': 'ЛСТ-1',
            'service_code': 'AGENT_REWARD',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_personal_accounts_schema.yaml'],
    static_table_data=['yt_personal_accounts.yaml'],
)
async def test_start_from_cursor(
        taxi_balance_replica,
        pgsql,
        yt_apply,
        testpoint,
        yt_client,
        get_personal_accounts,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    accounts = get_personal_accounts()
    assert accounts == []  # No accounts

    @testpoint('personal-accounts-yt-reader_revision')
    def _revision(data):
        _insert_cursor(pgsql, data['revision'], 1)

    await taxi_balance_replica.run_task('personal-accounts-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (2, 'hahn')

    accounts = get_personal_accounts()
    assert len(accounts) == 1
    assert accounts == [
        {
            'id': 1,
            'version': 0,
            'contract_id': 1,
            'external_id': 'ЛСТ-1',
            'service_code': 'AGENT_REWARD',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_personal_accounts_schema.yaml'],
    static_table_data=['yt_personal_accounts.yaml'],
)
async def test_null_cursor_when_table_ended(
        taxi_balance_replica,
        pgsql,
        yt_apply,
        testpoint,
        yt_client,
        get_personal_accounts,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    accounts = get_personal_accounts()
    assert accounts == []  # No accounts

    await taxi_balance_replica.run_task('personal-accounts-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (2, 'hahn')

    # Offset turns 'NULL' after we are sure
    # that cursor has reached the end of the table
    await taxi_balance_replica.run_task('personal-accounts-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (None, 'hahn')


@pytest.mark.config(
    BALANCE_REPLICA_YT_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_yt_reader': get_config(enabled=True),
    },
)
@pytest.mark.yt(
    schemas=['yt_personal_accounts_schema.yaml'],
    static_table_data=['yt_personal_accounts_error.yaml'],
)
async def test_error(
        taxi_balance_replica,
        pgsql,
        yt_apply,
        testpoint,
        yt_client,
        get_personal_accounts,
        stq,
):
    cursor = _get_cursor(pgsql)
    assert cursor == []  # No cursor
    accounts = get_personal_accounts()
    assert accounts == []  # No accounts

    await taxi_balance_replica.run_task('personal-accounts-yt-reader')

    cursor = _get_cursor(pgsql)
    assert len(cursor) == 1
    assert (cursor[0][1], cursor[0][2]) == (2, 'hahn')

    accounts = get_personal_accounts()
    assert accounts == [
        {
            'id': 1,
            'version': 0,
            'contract_id': 1,
            'external_id': 'ЛСТ-1',
            'service_code': 'AGENT_REWARD',
        },
    ]

    assert stq.balance_replica_personal_accounts.times_called == 1
    stq_call = stq.balance_replica_personal_accounts.next_call()
    stq_call.pop('eta')
    stq_call['kwargs'].pop('log_extra')
    assert stq_call == {
        'queue': 'balance_replica_personal_accounts',
        'id': 'personal_accounts_error_ae76fbf75b4cc69610fda0cd936d4026',
        'args': [],
        'kwargs': {
            'error_msg': (
                'Field \'/\' is of a wrong type. '
                'Expected: uintValue, actual: nullValue'
            ),
            'raw_data': (
                '{"pa.id":0,"pa.version":0,'
                '"pa.contract_id":null,"pa.obj":null}'
            ),
            'source': 'yt',
        },
    }
