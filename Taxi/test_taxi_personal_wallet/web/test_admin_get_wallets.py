from aiohttp import test_utils
import pytest


class BillingWalletContext:
    balances = {
        'portal': [
            {'wallet_id': 'wallet/yataxi', 'amount': '0', 'currency': 'RUB'},
            {
                'wallet_id': '5894ae48f9334d48ae2c5a2b3d00a075',
                'amount': '120.10',
                'currency': 'RUB',
            },
            {
                'wallet_id': '229650282dba4d1880f91ca014f332e6',
                'amount': '135.10',
                'currency': 'EUR',
            },
        ],
        'bound_to_portal': [
            {
                'wallet_id': '2ba8410b9657456cb5378b37d730fc0d',
                'amount': '0',
                'currency': 'USD',
            },
            {
                'wallet_id': 'f5a0e10de0174ee980376ace942f4732',
                'amount': '12',
                'currency': 'RUB',
            },
        ],
    }


@pytest.fixture(name='billing_wallet_context')
def _billing_wallet_context():
    return BillingWalletContext()


@pytest.fixture(name='mock_billing_balances')
def _mock_billing_balances(mockserver, billing_wallet_context):
    @mockserver.json_handler('/billing-wallet/balances')
    async def _balances_handler(request):
        yandex_uid = request.json['yandex_uid']
        balances = billing_wallet_context.balances.get(yandex_uid, [])
        return {'balances': balances}


class ZaloginContext:
    status = 200
    uid_info = {
        'type': 'portal',
        'yandex_uid': 'portal',
        'bound_phonishes': ['bound_to_portal'],
    }


@pytest.fixture(name='zalogin_context')
def _zalogin_context():
    return ZaloginContext()


@pytest.fixture(name='mock_zalogin')
def _mock_zalogin(mockserver, zalogin_context):
    @mockserver.handler('/zalogin/v1/internal/uid-info')
    async def _uid_info_handler(request):
        return mockserver.make_response(
            json=zalogin_context.uid_info, status=zalogin_context.status,
        )


async def test_get_wallets_portal(
        web_app_client: test_utils.TestClient,
        mock_billing_balances,
        mock_zalogin,
):

    response = await web_app_client.get(
        '/v1/admin/wallets', params=dict(yandex_uid='portal'),
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data == {
        'wallets': {
            'main': [
                {
                    'wallet_id': 'wallet/yataxi',
                    'yandex_uid': 'portal',
                    'balance': '0',
                    'currency': 'RUB',
                },
                {
                    'wallet_id': '5894ae48f9334d48ae2c5a2b3d00a075',
                    'yandex_uid': 'portal',
                    'currency': 'RUB',
                    'balance': '120.10',
                },
                {
                    'wallet_id': '229650282dba4d1880f91ca014f332e6',
                    'yandex_uid': 'portal',
                    'currency': 'EUR',
                    'balance': '135.10',
                },
            ],
            'bound': [
                {
                    'wallet_id': '2ba8410b9657456cb5378b37d730fc0d',
                    'yandex_uid': 'bound_to_portal',
                    'currency': 'USD',
                    'balance': '0',
                },
                {
                    'wallet_id': 'f5a0e10de0174ee980376ace942f4732',
                    'yandex_uid': 'bound_to_portal',
                    'balance': '12',
                    'currency': 'RUB',
                },
            ],
        },
    }


async def test_get_wallets_phonish(
        web_app_client: test_utils.TestClient,
        mock_billing_balances,
        zalogin_context,
        mock_zalogin,
):
    zalogin_context.uid_info = {
        'type': 'phonish',
        'yandex_uid': 'bound_to_portal',
        'bound_to': 'portal',
    }
    response = await web_app_client.get(
        '/v1/admin/wallets', params=dict(yandex_uid='bound_to_portal'),
    )
    assert response.status == 200
    response_data = await response.json()

    assert response_data == {
        'wallets': {
            'main': [
                {
                    'wallet_id': '2ba8410b9657456cb5378b37d730fc0d',
                    'yandex_uid': 'bound_to_portal',
                    'currency': 'USD',
                    'balance': '0',
                },
                {
                    'wallet_id': 'f5a0e10de0174ee980376ace942f4732',
                    'yandex_uid': 'bound_to_portal',
                    'balance': '12',
                    'currency': 'RUB',
                },
            ],
        },
    }


async def test_get_wallets_no_uid(web_app_client: test_utils.TestClient):
    response = await web_app_client.get('/v1/admin/wallets')
    assert response.status == 400


async def test_get_wallets_uid_not_found(
        web_app_client: test_utils.TestClient,
        zalogin_context,
        mock_zalogin,
        mock_billing_balances,
):
    zalogin_context.status = 409
    zalogin_context.uid_info = {
        'code': 'uid_not_found',
        'message': 'Requested UID not found',
    }

    response = await web_app_client.get(
        '/v1/admin/wallets', params={'yandex_uid': 'bound_to_portal'},
    )

    assert response.status == 200

    response_data = await response.json()
    assert response_data == {
        'wallets': {
            'main': [
                {
                    'wallet_id': '2ba8410b9657456cb5378b37d730fc0d',
                    'yandex_uid': 'bound_to_portal',
                    'currency': 'USD',
                    'balance': '0',
                },
                {
                    'wallet_id': 'f5a0e10de0174ee980376ace942f4732',
                    'yandex_uid': 'bound_to_portal',
                    'balance': '12',
                    'currency': 'RUB',
                },
            ],
        },
    }
