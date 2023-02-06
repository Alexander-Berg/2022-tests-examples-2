import decimal
import json

import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CASHBACK_ANNIHILATOR_TABLE_UPLOAD={
            'enabled': True,
            'butch_size': 100,
            'sleep_sec': 5,
        },
    ),
]


@pytest.fixture
def _mock_blackbox(mockserver):
    @mockserver.json_handler('/blackbox')
    async def _mock(request):
        assert request.args['method'] == 'userinfo'
        print(request.args['uid'])
        yandex_uid = request.args['uid'].split(',')[0]

        json_response = {
            'users': [
                {
                    'aliases': {'1': 'portal-account'},
                    'attributes': {},
                    'uid': {'value': yandex_uid},
                },
            ],
        }

        return mockserver.make_response(status=200, json=json_response)

    return _mock


def sync_finished(pgsql):
    cursor = pgsql['cashback_annihilator'].cursor()
    cursor.execute(
        """
        SELECT finished_at FROM cashback_annihilator.balance_sync
    """,
    )
    rows = list(cursor)
    assert len(rows) == 1
    assert rows[0][0] is not None


""" This is a fapping test. Need to fix.
@pytest.mark.pgsql('cashback_annihilator', files=['test_active_sync.sql'])
async def test_finished_task(
        taxi_cashback_annihilator, pgsql, testpoint, _mock_blackbox,
):
    @testpoint('task-table-upload-finished')
    def worker_finished(data):
        pass

    async with taxi_cashback_annihilator.spawn_task(
            'distlock/task-table-upload',
    ):
        await worker_finished.wait_call()

        sync_finished(pgsql)
"""  # pylint: disable=pointless-string-statement


@pytest.mark.config(PLUS_SWEET_HOME_IGNORE_LIST_FEATURE_BUNDLES=())
@pytest.mark.yt(static_table_data=['yt_task_table_upload.yaml'])
@pytest.mark.pgsql('cashback_annihilator', files=['test_active_sync.sql'])
async def test_happy_path(
        taxi_cashback_annihilator,
        pgsql,
        testpoint,
        yt_client,
        mockserver,
        _mock_blackbox,
):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        yandex_uid = request.args['yandex_uid']
        if yandex_uid == '12345678':
            wallet_id = 'w/wallet_id1'
        elif yandex_uid == '1234567899999':
            wallet_id = 'w/wallet_id2'
        else:
            # If reached
            raise Exception(
                f'Got unexpected yandex_uid = {yandex_uid}. '
                f'You need to patch static file '
                f'yt_task_table_upload.yaml or yandex_uids conditions',
            )
        balances = [
            {'balance': '120.0000', 'currency': 'RUB', 'wallet_id': wallet_id},
        ]
        return mockserver.make_response(
            json={'balances': balances}, status=200,
        )

    @testpoint('task-table-upload-finished')
    def worker_finished(data):
        pass

    async with taxi_cashback_annihilator.spawn_task(
            'distlock/task-table-upload',
    ):
        await worker_finished.wait_call()

        sync_finished(pgsql)

        cursor = pgsql['cashback_annihilator'].cursor()
        cursor.execute(
            """
            SELECT * FROM cashback_annihilator.balances
        """,
        )
        rows = list(cursor)
        assert len(rows) == 2
        assert rows[0][:4] == (
            decimal.Decimal('120.0000'),
            'w/wallet_id1',
            'RUB',
            '12345678',
        )


@pytest.mark.config(PLUS_SWEET_HOME_IGNORE_LIST_FEATURE_BUNDLES=())
@pytest.mark.yt(static_table_data=['yt_task_table_upload.yaml'])
@pytest.mark.pgsql('cashback_annihilator', files=['test_active_sync.sql'])
async def test_v1_balances_failed(
        taxi_cashback_annihilator,
        pgsql,
        testpoint,
        yt_client,
        mockserver,
        _mock_blackbox,
):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        yandex_uid = request.args['yandex_uid']
        if yandex_uid == '1234567899999':
            wallet_id = 'w/wallet_id2'
        else:
            return mockserver.make_response(status=500)
        balances = [
            {'balance': '120.0000', 'currency': 'RUB', 'wallet_id': wallet_id},
        ]
        return mockserver.make_response(
            json={'balances': balances}, status=200,
        )

    @testpoint('task-table-upload-finished')
    def worker_finished(data):
        pass

    async with taxi_cashback_annihilator.spawn_task(
            'distlock/task-table-upload',
    ):
        await worker_finished.wait_call()

        cursor = pgsql['cashback_annihilator'].cursor()
        cursor.execute(
            """
            SELECT finished_at FROM cashback_annihilator.balance_sync
        """,
        )
        rows = list(cursor)
        assert len(rows) == 1
        assert rows[0][0] is None

        cursor = pgsql['cashback_annihilator'].cursor()
        cursor.execute(
            """
            SELECT * FROM cashback_annihilator.balances
        """,
        )
        rows = list(cursor)
        assert not rows


@pytest.mark.config(PLUS_SWEET_HOME_IGNORE_LIST_FEATURE_BUNDLES=())
@pytest.mark.yt(static_table_data=['yt_task_table_upload.yaml'])
@pytest.mark.pgsql('cashback_annihilator', files=['test_active_sync.sql'])
async def test_user_has_plus(
        taxi_cashback_annihilator, pgsql, testpoint, yt_client, mockserver,
):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        yandex_uid = request.args['yandex_uid']
        if yandex_uid == '12345678':
            wallet_id = 'w/wallet_id1'
        elif yandex_uid == '1234567899999':
            wallet_id = 'w/wallet_id2'
        else:
            # If reached
            raise Exception(
                f'Got unexpected yandex_uid = {yandex_uid}. '
                f'You need to patch static file '
                f'yt_task_table_upload.yaml or yandex_uids conditions',
            )
        balances = [
            {'balance': '120.0000', 'currency': 'RUB', 'wallet_id': wallet_id},
        ]
        return mockserver.make_response(
            json={'balances': balances}, status=200,
        )

    @mockserver.json_handler('/blackbox')
    async def _mock_blackbox(request):
        assert request.args['method'] == 'userinfo'
        yandex_uid = request.args['uid'].split(',')[0]

        json_response = {
            'users': [
                {
                    'aliases': {'1': 'portal-account'},
                    'attributes': {},
                    'uid': {'value': yandex_uid},
                },
            ],
        }

        if yandex_uid == '1234567899999':
            json_response = {
                'users': [
                    {
                        'aliases': {'1': 'portal-account'},
                        'attributes': {'1015': '1', '1025': '1'},
                        'uid': {'value': '1111111'},
                    },
                ],
            }

        return mockserver.make_response(status=200, json=json_response)

    @mockserver.handler('/fast-prices-notify/billing/user/state')
    async def _mock_fast_prices(request, *args, **kwargs):
        yandex_uid = request.args['uid']
        if yandex_uid == '12345678':
            return mockserver.make_response(
                json.dumps({'activeIntervals': [], 'uid': int(yandex_uid)}),
            )
        if yandex_uid == '1234567899999':
            return mockserver.make_response(
                json.dumps(
                    {
                        'activeIntervals': [
                            {
                                'featureBundle': 'new-plus',
                                'end': '2021-01-07T18:21:26Z',
                                'orderType': 'native-auto-subscription',
                            },
                        ],
                        'uid': int(yandex_uid),
                    },
                ),
            )
        # If reached
        raise Exception(
            f'Got unexpected yandex_uid = {yandex_uid}. '
            f'You need to patch static file '
            f'yt_task_table_upload.yaml or yandex_uids conditions',
        )

    @testpoint('task-table-upload-finished')
    def worker_finished(data):
        pass

    async with taxi_cashback_annihilator.spawn_task(
            'distlock/task-table-upload',
    ):
        await worker_finished.wait_call()

        sync_finished(pgsql)

        cursor = pgsql['cashback_annihilator'].cursor()
        cursor.execute(
            """
            SELECT * FROM cashback_annihilator.balances
        """,
        )
        rows = list(cursor)
        assert len(rows) == 1
        assert rows[0][:4] == (
            decimal.Decimal('120.0000'),
            'w/wallet_id1',
            'RUB',
            '12345678',
        )
