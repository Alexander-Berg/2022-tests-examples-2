import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from random_discounts_plugins import *  # noqa: F403 F401


@pytest.fixture(name='user_api')
def _user_api(mockserver):
    class Context:
        mock_user_phones = None

    context = Context()

    @mockserver.json_handler('/user-api/v2/user_phones/get')
    async def _user_phones(request):
        assert request.json['id'] == '123456789012345678901234'
        assert request.json['fields'] == ['last_order_nearest_zone']
        return {
            'id': '5df214fc7984b5db623bc342',
            'last_order_nearest_zone': 'moscow',
        }

    context.mock_user_phones = _user_phones

    return context


@pytest.fixture(name='coupons', autouse=True)
def _coupons(mockserver):
    @mockserver.json_handler('/coupons/internal/generate')
    async def _internal_generate(request):
        return {
            'promocode': 'promocode-1',
            'promocode_params': {
                'value': 30,
                'expire_at': '2021-05-20T00:00:00+00:00',
                'currency_code': 'RUB',
            },
        }

    return _internal_generate
