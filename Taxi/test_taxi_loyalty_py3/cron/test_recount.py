# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi_loyalty_py3.generated.cron import run_cron
from test_taxi_loyalty_py3 import utils

TAGS_ASSIGN_PATH = '/tags/v1/assign'
DMS_URL = '/driver-metrics-storage/v1/wallet/balance'


# pylint: disable=too-many-locals
@pytest.mark.now('2019-05-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, created, updated, next_recount, status)
        VALUES
        (
          '2',
          '000000000000000000000002',
          '2019-04-10 03:00:00.000000',
          '2019-04-10 03:00:00.000000',
          '2019-04-30 21:00:00.000000',
          'gold'
        )
        """,
    ],
)
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=100, sleep=0, dms_batch_size=30),
    ),
    LOYALTY_STATUSES=[
        dict(name='bronze', value=5),
        dict(name='silver', value=75),
        dict(name='gold', value=150, rating=4.2),
        dict(name='platinum', value=300, rating=4.8),
    ],
    LOYALTY_COMPARE_YT_DMS='oldway',
)
@pytest.mark.parametrize(
    'wallet_balance, rating, status, reason',
    [
        pytest.param(
            250, 3.844, 'silver', 'recount, rating 3.84 (downgrade gold 4.20)',
        ),
        pytest.param(250, 4.2399, 'gold', 'recount, rating 4.24'),
        pytest.param(333, 4.92, 'platinum', 'recount, rating 4.92'),
        pytest.param(
            333,
            3.843,
            'silver',
            'recount, rating 3.84 (downgrade platinum 4.80) '
            '(downgrade gold 4.20)',
        ),
        pytest.param(3, 4.92, 'undefined', 'recount, rating 4.92'),
        pytest.param(88, 3.844, 'silver', 'recount, rating 3.84'),
        pytest.param(333, None, 'platinum', 'recount, rating [none]'),
        pytest.param(
            88,
            3.844,
            'gold',
            'replace status (silver) with gold by not_lower_than_prev policy',
            marks=pytest.mark.client_experiments3(
                consumer='loyalty/recount_policy',
                config_name='loyalty_recount_policy',
                args=[
                    {
                        'name': 'udid',
                        'type': 'string',
                        'value': '000000000000000000000002',
                    },
                ],
                value={'type': 'not_lower_than_prev'},
            ),
            id='use prev by policy',
        ),
        pytest.param(
            88,
            3.844,
            'platinum',
            'replace status (silver) with platinum'
            ' by not_lower_than_value policy',
            marks=pytest.mark.client_experiments3(
                consumer='loyalty/recount_policy',
                config_name='loyalty_recount_policy',
                args=[
                    {
                        'name': 'udid',
                        'type': 'string',
                        'value': '000000000000000000000002',
                    },
                ],
                value={'type': 'not_lower_than_value', 'status': 'platinum'},
            ),
            id='use value by policy',
        ),
    ],
)
async def test_recount(
        patch,
        mockserver,
        mock_driver_ratings,
        pgsql,
        wallet_balance,
        rating,
        status,
        reason,
):
    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [{'udid': x, 'value': wallet_balance} for x in data['udids']]

    mock_driver_ratings.rating = rating

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    dms_calls = mock_dms.times_called
    assert dms_calls == 1
    assert mock_dms.next_call()['request'].json == dict(
        ts_from='2019-04-01T00:00:00Z',
        ts_to='2019-05-01T00:00:00Z',
        udids=['000000000000000000000002'],
    )

    assert mock_driver_ratings.handler_mock.times_called == 1
    driver_ratings_call = mock_driver_ratings.handler_mock.next_call()
    assert driver_ratings_call['request'].json == dict(
        id_in_set=['000000000000000000000002'],
    )
    assert driver_ratings_call['request'].query == dict(
        consumer='taxi_loyalty_py3_cron',
    )

    if status == 'undefined':
        assert mock_tags.times_called == 1
        assert mock_tags.next_call()['args'][0].json == dict(
            provider='loyalty',
            entities=[
                dict(
                    type='udid', name='000000000000000000000002', tags=dict(),
                ),
            ],
        )
    else:
        assert mock_tags.times_called == 1
        assert mock_tags.next_call()['args'][0].json == dict(
            provider='loyalty',
            entities=[
                dict(
                    type='udid',
                    name='000000000000000000000002',
                    tags={status: {}},
                ),
            ],
        )

    pg_account = utils.select_account(pgsql, '000000000000000000000002')
    assert pg_account == [(status, datetime.datetime(2019, 5, 31, 21, 0))]

    pg_logs = utils.select_logs(pgsql, '000000000000000000000002')
    assert pg_logs == [(status, reason, wallet_balance)]


@pytest.mark.now('2019-05-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, created, updated, next_recount, status)
        VALUES
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
        __default__=dict(enabled=True, limit=100, sleep=0, dms_batch_size=30),
    ),
    LOYALTY_STATUSES=[],
    LOYALTY_RECOUNT_WHITE_LIST={
        'gold': [],
        'platinum': ['000000000000000000000002'],
    },
    LOYALTY_COMPARE_YT_DMS='oldway',
)
async def test_recount_white_list(
        patch,
        patch_aiohttp_session,
        response_mock,
        pgsql,
        mockserver,
        mock_driver_ratings,
):
    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    @mockserver.json_handler(DMS_URL)
    def _mock_dms(request, *args, **kwargs):
        data = request.json
        return [{'udid': x, 'value': 5} for x in data['udids']]

    mock_driver_ratings.rating = 2.5

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    assert mock_driver_ratings.handler_mock.times_called == 1
    assert mock_tags.times_called == 1

    pg_account = utils.select_account(pgsql, '000000000000000000000002')
    assert pg_account == [('platinum', datetime.datetime(2019, 5, 31, 21, 0))]

    pg_logs = utils.select_logs(pgsql, '000000000000000000000002')
    assert pg_logs == [('platinum', 'recount, white list', 5)]


@pytest.mark.now('2019-05-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, created, updated, next_recount, status)
        VALUES
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
        __default__=dict(enabled=True, limit=100, sleep=0, dms_batch_size=30),
    ),
    LOYALTY_STATUSES=[dict(name='platinum', value=300, rating=4.8)],
    LOYALTY_EXPERIMENTAL_UNDEFINED_DRIVERS=['000000000000000000000002'],
    LOYALTY_COMPARE_YT_DMS='oldway',
)
async def test_recount_experimental_drivers(
        patch,
        patch_aiohttp_session,
        response_mock,
        pgsql,
        mockserver,
        mock_driver_ratings,
):
    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [{'udid': x, 'value': 300} for x in data['udids']]

    mock_driver_ratings.rating = 5.0

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    assert mock_dms.times_called == 1
    assert mock_driver_ratings.handler_mock.times_called == 1
    assert mock_tags.times_called == 1
    assert mock_tags.next_call()['args'][0].json == dict(
        provider='loyalty',
        entities=[
            dict(type='udid', name='000000000000000000000002', tags=dict()),
        ],
    )

    pg_account = utils.select_account(pgsql, '000000000000000000000002')
    assert pg_account == [('undefined', datetime.datetime(2019, 5, 31, 21, 0))]

    pg_logs = utils.select_logs(pgsql, '000000000000000000000002')
    assert pg_logs == [
        ('undefined', 'recount, rating 5.00, experimental driver', 300),
    ]


@pytest.mark.now('2019-05-14T00:00:00+0000')
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
        __default__=dict(enabled=True, limit=2, sleep=0, dms_batch_size=30),
    ),
    LOYALTY_STATUSES=[dict(name='gold', value=0)],
    LOYALTY_COMPARE_YT_DMS='oldway',
)
async def test_bulk_processing(
        patch,
        patch_aiohttp_session,
        response_mock,
        pgsql,
        mockserver,
        mock_driver_ratings,
):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [{'udid': x, 'value': 0} for x in data['udids']]

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    mock_driver_ratings.rating = 4.4

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    assert mock_dms.times_called == 1
    assert mock_driver_ratings.handler_mock.times_called == 1
    assert mock_tags.times_called == 1

    for i in range(1, 2):
        unique_driver_id = f'00000000000000000000000{i}'
        pg_account = utils.select_account(pgsql, unique_driver_id)
        assert pg_account == [('gold', datetime.datetime(2019, 5, 31, 21, 0))]
        pg_logs = utils.select_logs(pgsql, unique_driver_id)
        assert pg_logs == [('gold', 'recount, rating 4.40', 0)]


@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=100, sleep=0, dms_batch_size=30),
        recount=dict(enabled=False, limit=100, sleep=0, dms_batch_size=30),
    ),
    LOYALTY_COMPARE_YT_DMS='oldway',
)
async def test_disabled(
        patch_aiohttp_session, mockserver, mock_driver_ratings,
):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        return {}

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    assert not mock_dms.times_called
    assert not mock_driver_ratings.handler_mock.times_called
    assert not mock_tags.times_called


@pytest.mark.now('2019-05-14T00:00:00+0000')
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
        __default__=dict(enabled=True, limit=2, sleep=0, dms_batch_size=30),
    ),
    LOYALTY_STATUSES=[dict(name='gold', value=0)],
    USERVICE_TAGS_CLIENT_QOS={
        '/v1/assign': {'attempts': 3, 'timeout-ms': 650},
    },
    LOYALTY_COMPARE_YT_DMS='oldway',
)
@pytest.mark.parametrize(
    'stage', ['dms', 'driver_ratings', 'remove_tags', 'add_tags', 'postgres'],
)
async def test_recount_failed(
        patch,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        mock_driver_ratings,
        stage,
):
    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        if stage == 'dms':
            return mockserver.make_response('', status=500)
        data = request.json
        return [{'udid': x, 'value': 0} for x in data['udids']]

    mock_driver_ratings.rating = 0.85
    mock_driver_ratings.status_code = 500 if stage == 'driver_ratings' else 200

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(request):
        if stage in ('remove_tags', 'add_tags'):
            return mockserver.make_response(
                json={'code': '500', 'message': '500'}, status=500,
            )
        return {}

    @patch('taxi_loyalty_py3.helpers.db.recount_update_status')
    async def update_account(*args, **kwargs):
        if stage == 'postgres':
            raise Exception('Postgres error')

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    dms_calls = mock_dms.times_called
    driver_ratings_calls = mock_driver_ratings.handler_mock.times_called
    tags_calls = mock_tags.times_called
    update_calls = update_account.calls

    if stage == 'dms':
        assert dms_calls == 1
        assert not driver_ratings_calls
        assert not tags_calls
        assert not update_calls
    elif stage == 'driver_ratings':
        assert dms_calls == 1
        assert driver_ratings_calls == 3
        assert not tags_calls
        assert not update_calls
    elif stage == 'remove_tags':
        assert dms_calls == 1
        assert driver_ratings_calls == 1
        assert tags_calls == 3
        assert not update_calls
    elif stage == 'add_tags':
        assert dms_calls == 1
        assert driver_ratings_calls == 1
        assert tags_calls == 3
        assert not update_calls
    else:
        assert dms_calls == 1
        assert driver_ratings_calls == 1
        assert tags_calls == 1
        assert len(update_calls) == 1


@pytest.mark.now('2019-05-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.loyalty_accounts
              (id, unique_driver_id, next_recount, last_active_at, status)
        VALUES
        (
          '4',
          '000000000000000000000004',
          '2019-04-30 21:00:00.000000',
          NULL,
          'bronze'
        ),
        (
          '1',
          '000000000000000000000001',
          '2019-04-30 21:00:00.000000',
          '2019-01-01 00:00:00.000000',
          'bronze'
        ),
        (
          '2',
          '000000000000000000000002',
          '2019-04-30 21:00:00.000000',
          '2019-01-02 00:00:00.000000',
          'bronze'
        ),
        (
          '3',
          '000000000000000000000003',
          '2019-04-30 21:00:00.000000',
          '2018-12-31 00:00:00.000000',
          'bronze'
        )
        """,
    ],
)
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=1, sleep=0, dms_batch_size=30),
    ),
    LOYALTY_COMPARE_YT_DMS='oldway',
)
async def test_recount_order_by_last_active(
        patch, mockserver, mock_driver_ratings,
):
    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def _mock_tags(*args, **kwargs):
        return {}

    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [{'udid': x, 'value': 10} for x in data['udids']]

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    # Check that the driver who was recently active gets processed first
    assert mock_dms.next_call()['request'].json['udids'] == [
        '000000000000000000000002',
    ]
    assert mock_dms.next_call()['request'].json['udids'] == [
        '000000000000000000000001',
    ]
    assert mock_dms.next_call()['request'].json['udids'] == [
        '000000000000000000000003',
    ]
    assert mock_dms.next_call()['request'].json['udids'] == [
        '000000000000000000000004',
    ]
