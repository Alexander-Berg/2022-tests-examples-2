# pylint: disable=redefined-outer-name
import datetime

import pytest
from yql import config as yql_config

from taxi_loyalty_py3.generated.cron import run_cron
from test_taxi_loyalty_py3 import utils

TAGS_ASSIGN_PATH = '/tags/v1/assign'
DMS_URL = '/driver-metrics-storage/v1/wallet/balance'


class _BaseMockYqlRequestResults:
    is_success = True
    errors = None
    empty = False

    @property
    def dataframe(self):
        assert False

    @property
    def full_dataframe(self):
        return self

    def to_dict(self, *args, **kwargs):
        assert False


class _BaseMockYqlRequestOperation:
    share_url = ''

    def run(self, parameters, *args, **kwargs):
        assert False

    def subscribe(self, *args, **kwargs):
        pass

    def get_results(self, *args, **kwargs):
        assert False


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
        __default__=dict(enabled=True, limit=100, sleep=0, yt_batch_size=1),
    ),
    LOYALTY_STATUSES=[
        dict(name='bronze', value=5),
        dict(name='silver', value=75),
        dict(name='gold', value=150, rating=4.2),
        dict(name='platinum', value=300, rating=4.8),
    ],
    LOYALTY_COMPARE_YT_DMS='newway',
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

    mock_driver_ratings.rating = rating

    class _MockYqlRequestResults(_BaseMockYqlRequestResults):
        def to_dict(self, *args, **kwargs):
            return [
                {'udid': '000000000000000000000002', 'value': wallet_balance},
            ]

    class _MockYqlRequestOperation(_BaseMockYqlRequestOperation):
        def run(self, parameters, *args, **kwargs):
            assert parameters == {
                '$tmp_folder': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/tmp"}'
                ),
                '$wallet_table': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/2019-04"}'
                ),
                '$udids_str': '{"Data": [\"000000000000000000000002\"]}',
            }

        def get_results(self, *args, **kwargs):
            return _MockYqlRequestResults()

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert yql_config.config.db == 'hahn'
        return _MockYqlRequestOperation()

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

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


# pylint: disable=too-many-locals
@pytest.mark.now('2019-05-14T00:00:00+0000')
@pytest.mark.pgsql(
    'loyalty',
    queries=[
        """
        INSERT INTO loyalty.yt_loyalty_accounts
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
        __default__=dict(enabled=True, limit=100, sleep=0, yt_batch_size=1),
    ),
    LOYALTY_STATUSES=[
        dict(name='bronze', value=5),
        dict(name='silver', value=75),
        dict(name='gold', value=150, rating=4.2),
        dict(name='platinum', value=300, rating=4.8),
    ],
    LOYALTY_COMPARE_YT_DMS='newway',
    LOYALTY_ENABLE_DRY_RUN_FOR_TEST=True,
)
@pytest.mark.parametrize(
    'wallet_balance, rating, status, reason',
    [
        pytest.param(
            250, 3.844, 'silver', 'recount, rating 3.84 (downgrade gold 4.20)',
        ),
    ],
)
async def test_dry_run_next_recount_update(
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
    def mock_tags(*args, **kwargs):  # pylint: disable=unused-variable
        assert False

    @mockserver.json_handler(DMS_URL)
    def mock_dms(request, *args, **kwargs):
        data = request.json
        return [{'udid': x, 'value': wallet_balance} for x in data['udids']]

    mock_driver_ratings.rating = rating

    class _MockYqlRequestResults(_BaseMockYqlRequestResults):
        def to_dict(self, *args, **kwargs):
            return [
                {'udid': '000000000000000000000002', 'value': wallet_balance},
            ]

    class _MockYqlRequestOperation(_BaseMockYqlRequestOperation):
        def run(self, parameters, *args, **kwargs):
            assert parameters == {
                '$tmp_folder': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/tmp"}'
                ),
                '$wallet_table': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/2019-05"}'
                ),
                '$udids_str': '{"Data": [\"000000000000000000000002\"]}',
            }

        def get_results(self, *args, **kwargs):
            return _MockYqlRequestResults()

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert yql_config.config.db == 'hahn'
        return _MockYqlRequestOperation()

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    dms_calls = mock_dms.times_called
    assert dms_calls == 0

    assert mock_driver_ratings.handler_mock.times_called == 1

    pg_account_from_yt = utils.select_account(
        pgsql, '000000000000000000000002', yt_dryrun=True,
    )
    pg_account_from_dms = utils.select_account(
        pgsql, '000000000000000000000002', dms_dryrun=True,
    )
    assert pg_account_from_yt == [
        ('silver', datetime.datetime(2019, 5, 31, 21, 0)),
    ]
    assert pg_account_from_dms == []

    pg_logs_from_dms = utils.select_logs(
        pgsql, '000000000000000000000002', dms_dryrun=True,
    )
    assert pg_logs_from_dms == []


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
        __default__=dict(enabled=True, limit=100, sleep=0, yt_batch_size=1),
    ),
    LOYALTY_STATUSES=[],
    LOYALTY_RECOUNT_WHITE_LIST={
        'gold': [],
        'platinum': ['000000000000000000000002'],
    },
    LOYALTY_COMPARE_YT_DMS='newway',
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

    class _MockYqlRequestResults(_BaseMockYqlRequestResults):
        def to_dict(self, *args, **kwargs):
            return [{'udid': '000000000000000000000002', 'value': 5}]

    class _MockYqlRequestOperation(_BaseMockYqlRequestOperation):
        def run(self, parameters, *args, **kwargs):
            assert parameters == {
                '$tmp_folder': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/tmp"}'
                ),
                '$wallet_table': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/2019-04"}'
                ),
                '$udids_str': '{"Data": [\"000000000000000000000002\"]}',
            }

        def get_results(self, *args, **kwargs):
            return _MockYqlRequestResults()

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert yql_config.config.db == 'hahn'
        return _MockYqlRequestOperation()

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
        __default__=dict(enabled=True, limit=100, sleep=0, yt_batch_size=1),
    ),
    LOYALTY_STATUSES=[dict(name='platinum', value=300, rating=4.8)],
    LOYALTY_EXPERIMENTAL_UNDEFINED_DRIVERS=['000000000000000000000002'],
    LOYALTY_COMPARE_YT_DMS='newway',
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

    class _MockYqlRequestResults(_BaseMockYqlRequestResults):
        def to_dict(self, *args, **kwargs):
            return [{'udid': '000000000000000000000002', 'value': 300}]

    class _MockYqlRequestOperation(_BaseMockYqlRequestOperation):
        def run(self, parameters, *args, **kwargs):
            assert parameters == {
                '$tmp_folder': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/tmp"}'
                ),
                '$wallet_table': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/2019-04"}'
                ),
                '$udids_str': '{"Data": [\"000000000000000000000002\"]}',
            }

        def get_results(self, *args, **kwargs):
            return _MockYqlRequestResults()

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert yql_config.config.db == 'hahn'
        return _MockYqlRequestOperation()

    mock_driver_ratings.rating = 5.0

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

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
        __default__=dict(enabled=True, limit=2, sleep=0, yt_batch_size=1),
    ),
    LOYALTY_STATUSES=[dict(name='gold', value=0)],
    LOYALTY_COMPARE_YT_DMS='newway',
)
async def test_bulk_processing(
        patch,
        patch_aiohttp_session,
        response_mock,
        pgsql,
        mockserver,
        mock_driver_ratings,
):
    class _MockYqlRequestResults(_BaseMockYqlRequestResults):
        def to_dict(self, *args, **kwargs):
            return [
                {'udid': udid, 'value': 0}
                for udid in [
                    '000000000000000000000001',
                    '000000000000000000000002',
                ]
            ]

    class _MockYqlRequestOperation(_BaseMockYqlRequestOperation):
        def run(self, parameters, *args, **kwargs):
            assert parameters == {
                '$tmp_folder': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/tmp"}'
                ),
                '$wallet_table': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/2019-04"}'
                ),
                '$udids_str': (
                    '{"Data": [\"000000000000000000000001\", '
                    '\"000000000000000000000002\"]}'
                ),
            }

        def get_results(self, *args, **kwargs):
            return _MockYqlRequestResults()

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert yql_config.config.db == 'hahn'
        return _MockYqlRequestOperation()

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    mock_driver_ratings.rating = 4.4

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    assert mock_driver_ratings.handler_mock.times_called == 2
    assert mock_tags.times_called == 2

    for i in range(1, 2):
        unique_driver_id = f'00000000000000000000000{i}'
        pg_account = utils.select_account(pgsql, unique_driver_id)
        assert pg_account == [('gold', datetime.datetime(2019, 5, 31, 21, 0))]
        pg_logs = utils.select_logs(pgsql, unique_driver_id)
        assert pg_logs == [('gold', 'recount, rating 4.40', 0)]


@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS=dict(
        __default__=dict(enabled=True, limit=100, sleep=0, yt_batch_size=1),
        recount=dict(enabled=False, limit=100, sleep=0, yt_batch_size=1),
    ),
    LOYALTY_COMPARE_YT_DMS='newway',
)
async def test_disabled(
        patch, patch_aiohttp_session, mockserver, mock_driver_ratings,
):
    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert False

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def mock_tags(*args, **kwargs):
        return {}

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])

    assert not mock_driver_ratings.handler_mock.times_called
    assert not mock_tags.times_called


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
        __default__=dict(enabled=True, limit=1, sleep=0, yt_batch_size=1),
    ),
    LOYALTY_COMPARE_YT_DMS='newway',
)
async def test_recount_order_by_last_active(
        patch, mockserver, mock_driver_ratings,
):
    # Check that the driver who was recently active gets processed first
    cnt = 1
    calls = {
        1: '000000000000000000000002',
        2: '000000000000000000000001',
        3: '000000000000000000000003',
        4: '000000000000000000000004',
    }

    class _MockYqlRequestResults(_BaseMockYqlRequestResults):
        def to_dict(self, *args, **kwargs):
            nonlocal calls, cnt
            result = [{'udid': calls[cnt], 'value': 10}]
            cnt += 1
            return result

    class _MockYqlRequestOperation(_BaseMockYqlRequestOperation):
        def run(self, parameters, *args, **kwargs):
            assert parameters == {
                '$tmp_folder': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/tmp"}'
                ),
                '$wallet_table': (
                    '{"Data": "//home/taxi/unittests/'
                    'features/loyalty/dms_wallet/2019-04"}'
                ),
                '$udids_str': '{"Data": ' + f'["{calls[cnt]}"]' '}',
            }

        def get_results(self, *args, **kwargs):
            return _MockYqlRequestResults()

    @patch('yql.api.v1.client.YqlClient.query')
    def _query(query_str, **kwargs):
        assert yql_config.config.db == 'hahn'
        return _MockYqlRequestOperation()

    @mockserver.json_handler(TAGS_ASSIGN_PATH)
    def _mock_tags(*args, **kwargs):
        return {}

    await run_cron.main(['taxi_loyalty_py3.crontasks.recount', '-t', '0'])
