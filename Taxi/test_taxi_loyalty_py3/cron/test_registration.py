# pylint: disable=redefined-outer-name

import pytest

from taxi_loyalty_py3.generated.cron import run_cron

TAGS_ASSIGN_PATH = '/tags/v1/assign'
DMS_URL = '/driver-metrics-storage/v1/wallet/balance'


def select_status(pgsql, unique_driver_id):
    cursor = pgsql['loyalty'].cursor()
    cursor.execute(
        'SELECT status '
        'FROM loyalty.loyalty_accounts '
        f'WHERE unique_driver_id=\'{unique_driver_id}\'',
    )
    result = [row for row in cursor]
    cursor.close()
    return result


def select_logs(pgsql, unique_driver_id):
    cursor = pgsql['loyalty'].cursor()
    cursor.execute(
        'SELECT status, reason, points '
        'FROM loyalty.status_logs '
        f'WHERE unique_driver_id=\'{unique_driver_id}\'',
    )
    result = [row for row in cursor]
    cursor.close()
    return result


@pytest.mark.now('2019-04-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, created, updated, next_recount, status)
        VALUES
        (
          '1',
          '000000000000000000000001',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        ),
        (
          '2',
          '000000000000000000000002',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'bronze'
        )
        """,
    ],
)
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=100, sleep=0),
    ),
    LOYALTY_NEWBIE_THRESHOLD=300000,
    LOYALTY_STATUSES=[
        dict(name='bronze', value=5),
        dict(name='silver', value=75),
        dict(name='gold', value=150),
        dict(name='platinum', value=300),
    ],
)
@pytest.mark.parametrize(
    'wallet_balance, status',
    [
        (3, 'none'),
        (5, 'bronze'),
        (10, 'bronze'),
        (75, 'silver'),
        (120, 'silver'),
        (150, 'gold'),
        (250, 'gold'),
        (300, 'platinum'),
        (500, 'platinum'),
    ],
)
async def test_registration(
        patch,
        patch_aiohttp_session,
        response_mock,
        pgsql,
        mockserver,
        wallet_balance,
        status,
):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [
            {
                'udid': x,
                'value': wallet_balance,
                'last_ts': '2019-04-13T00:00:00.000000+0000',
            }
            for x in data['udids']
        ]

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    await run_cron.main(['taxi_loyalty_py3.crontasks.registration', '-t', '0'])

    dms_calls = mock_dms.times_called
    assert dms_calls == 1
    assert mock_dms.next_call()['request'].json == dict(
        ts_from='2019-03-31T21:00:00Z',
        ts_to='2019-04-14T00:00:00Z',
        udids=['000000000000000000000001'],
    )

    tags_calls = mock_tags.times_called
    if status == 'none':
        assert not tags_calls
    else:
        assert tags_calls == 1
        assert mock_tags.next_call()['args'][0].json == dict(
            provider='loyalty',
            entities=[
                dict(
                    type='udid',
                    name='000000000000000000000001',
                    tags={status: {}},
                ),
            ],
        )

    pg_status = select_status(pgsql, '000000000000000000000001')
    assert pg_status == [(status if status != 'none' else 'newbie',)]

    pg_logs = select_logs(pgsql, '000000000000000000000001')
    if status == 'none':
        assert not pg_logs
    else:
        assert pg_logs == [(status, 'registration', wallet_balance)]


# pylint: disable=too-many-locals
@pytest.mark.now('2019-04-14T03:01:45+0300')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, created, updated, next_recount, status)
        VALUES
        (
          '1',
          '000000000000000000000001',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        )
        """,
    ],
)
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=100, sleep=0),
    ),
    LOYALTY_NEWBIE_THRESHOLD=256200,
    LOYALTY_STATUSES=[
        dict(name='bronze', value=5),
        dict(name='silver', value=75),
        dict(name='gold', value=150),
        dict(name='platinum', value=300),
    ],
)
@pytest.mark.parametrize(
    'wallet_balance, status, last_ts, reason',
    [
        (4, 'undefined', '2019-04-10T03:00:00.301973+0000', 'inactive'),
        (4, 'undefined', None, 'inactive'),
        (33, 'bronze', '2019-04-10T03:00:00.301973+0000', 'registration'),
    ],
)
async def test_registration_drop_inactive(
        patch,
        patch_aiohttp_session,
        response_mock,
        pgsql,
        mockserver,
        wallet_balance,
        status,
        last_ts,
        reason,
):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [
            {'udid': x, 'value': wallet_balance, 'last_ts': last_ts}
            for x in data['udids']
        ]

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    await run_cron.main(['taxi_loyalty_py3.crontasks.registration', '-t', '0'])

    dms_calls = mock_dms.times_called
    assert dms_calls == 1
    assert mock_dms.next_call()['request'].json == dict(
        ts_from='2019-03-31T21:00:00Z',
        ts_to='2019-04-14T03:01:45Z',
        udids=['000000000000000000000001'],
    )

    tags_calls = mock_tags.times_called
    if status == 'undefined':
        assert not tags_calls
    else:
        assert tags_calls == 1

    pg_status = select_status(pgsql, '000000000000000000000001')
    assert pg_status == [(status,)]

    pg_logs = select_logs(pgsql, '000000000000000000000001')
    assert pg_logs == [(status, reason, wallet_balance)]


@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=100, sleep=0),
        registration=dict(enabled=False, limit=100, sleep=0),
    ),
    LOYALTY_NEWBIE_THRESHOLD=300000,
)
async def test_disabled(mockserver):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        return {}

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    await run_cron.main(['taxi_loyalty_py3.crontasks.registration', '-t', '0'])

    assert not mock_dms.times_called
    assert not mock_tags.times_called


@pytest.mark.now('2019-04-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, created, updated, next_recount, status)
        VALUES
        (
          '1',
          '000000000000000000000001',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        ),
        (
          '2',
          '000000000000000000000002',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        ),
        (
          '3',
          '000000000000000000000003',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-03-30 21:00:00.000000',
          'newbie'
        ),
        (
          '4',
          '000000000000000000000004',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        ),
        (
          '5',
          '000000000000000000000005',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        ),
        (
          '6',
          '000000000000000000000006',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'returnee'
        ),
        (
          '7',
          '000000000000000000000007',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        )
        """,
    ],
)
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=2, sleep=0),
    ),
    LOYALTY_NEWBIE_THRESHOLD=400000,
    LOYALTY_STATUSES=[dict(name='gold', value=0)],
)
async def test_bulk_processing(
        patch, patch_aiohttp_session, response_mock, pgsql, mockserver,
):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [{'udid': x, 'value': 0} for x in data['udids']]

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    await run_cron.main(['taxi_loyalty_py3.crontasks.registration', '-t', '0'])

    assert mock_dms.times_called == 4
    assert mock_tags.times_called == 4

    for i in range(1, 7):
        unique_driver_id = f'00000000000000000000000{i}'
        pg_status = select_status(pgsql, unique_driver_id)
        assert pg_status == [('gold',)]
        pg_logs = select_logs(pgsql, unique_driver_id)
        assert pg_logs == [('gold', 'registration', 0)]


@pytest.mark.now('2019-04-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, created, updated, next_recount, status)
        VALUES
        (
          '1',
          '000000000000000000000001',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        ),
        (
          '2',
          '000000000000000000000002',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'newbie'
        )
        """,
    ],
)
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=2, sleep=0),
    ),
    LOYALTY_NEWBIE_THRESHOLD=400000,
    LOYALTY_STATUSES=[dict(name='gold', value=0)],
    USERVICE_TAGS_CLIENT_QOS={
        '/v1/assign': {'attempts': 3, 'timeout-ms': 650},
    },
)
@pytest.mark.parametrize(
    'stage', ['dms', 'remove_tags', 'add_tags', 'postgres'],
)
async def test_registration_failed(
        patch, patch_aiohttp_session, mockserver, response_mock, stage,
):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        if stage == 'dms':
            return mockserver.make_response('', status=500)
        data = request.json
        return [{'udid': x, 'value': 0} for x in data['udids']]

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        if stage in ('remove_tags', 'add_tags'):
            return mockserver.make_response(
                json={'code': '500', 'message': '500'}, status=500,
            )
        return {}

    @patch('taxi_loyalty_py3.helpers.db.registration_update_status')
    async def update_account(*args, **kwargs):
        if stage == 'postgres':
            raise Exception('Postgres error')

    await run_cron.main(['taxi_loyalty_py3.crontasks.registration', '-t', '0'])

    dms_calls = mock_dms.times_called
    tags_calls = mock_tags.times_called
    update_calls = update_account.calls

    if stage == 'dms':
        assert dms_calls == 1
        assert not tags_calls
        assert not update_calls
    elif stage == 'remove_tags':
        assert dms_calls == 1
        assert tags_calls == 3
        assert not update_calls
    elif stage == 'add_tags':
        assert dms_calls == 1
        assert tags_calls == 3
        assert not update_calls
    else:
        assert dms_calls == 1
        assert tags_calls == 1
        assert len(update_calls) == 2
