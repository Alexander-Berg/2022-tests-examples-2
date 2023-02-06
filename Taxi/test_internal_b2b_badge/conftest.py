# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest

import internal_b2b_badge.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = ['internal_b2b_badge.generated.service.pytest_plugins']


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(
            pytest.mark.filterwarnings('ignore:Task.current_task:'),
        )


@pytest.fixture(autouse=True)
def patch_request(patch):
    @patch('aiogram.bot.api.request')
    async def nothing_request(*args, **kwargs):  # pylint: disable=W0612
        return {}


@pytest.fixture
def mock_badgepay_payment_tokens(mock_badgepay):
    @mock_badgepay('/pg/paymentTokens', raw_request=False)
    async def _handler(request):
        allowed_users = {
            'good_boy': b'good_boy_token',
            'another_good_boy': b'another_good_boy_token',
            'boy_who_crash_badgepay': None,
        }
        login = request.json['login']

        if login == 'boy_who_crash_badgepay':
            resp = web.Response(
                body=allowed_users[login],
                content_type='image/png',
                status=500,
            )
        else:
            resp = web.Response(
                body=allowed_users[login], content_type='image/png',
            )
        return resp
