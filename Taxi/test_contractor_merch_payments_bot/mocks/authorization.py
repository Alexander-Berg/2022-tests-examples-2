import dataclasses

import aiohttp.web
import pytest

import testsuite.utils.http as http

import test_contractor_merch_payments_bot.mocks.common as common


_LOGIN_TO_PERSONAL_ID_MAP = {
    'test_username': 'd1206262dea04cca9da5525c176c1b90',
    'test_ivanov_victor_1970': 'sonsdnc9929dn202010e4cnn191nx49c',
    'test_not_registered_merchant_username': 'shsk299s0aks9e7chcn28sdc',
}
_PERSONAL_ID_TO_MERCHANT_ID_MAP = {
    'd1206262dea04cca9da5525c176c1b90': 'test_merchant_id_username',
    'sonsdnc9929dn202010e4cnn191nx49c': 'merchant_id-mcdonalds',
}


def _personal_telegram_logins_find(request: http.Request):
    assert request.method == 'POST'
    value = request.json['value']
    personal_id = _LOGIN_TO_PERSONAL_ID_MAP.get(value)
    if personal_id is not None:
        return {'id': personal_id, 'value': value}
    return None


def _merchant_profiles_id_retrieve(request: http.Request):
    assert request.method == 'GET'
    telegram_login_pd_id = request.args['telegram_login_pd_id']
    merchant_id = _PERSONAL_ID_TO_MERCHANT_ID_MAP.get(telegram_login_pd_id)
    if merchant_id is not None:
        return {'merchant_id': merchant_id}
    return None


def _response_wrapper(response):
    if response is not None:
        return aiohttp.web.json_response(response)
    return aiohttp.web.json_response(
        {'code': '404', 'message': 'Not Found'}, status=404,
    )


@pytest.fixture(name='mock_personal_telegram_logins_find')
def _mock_personal_telegram_logins_find(mock_personal):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mock_personal('/v1/telegram_logins/find')
        async def handler(request):
            if context.response is not None:
                return context.response
            return _response_wrapper(_personal_telegram_logins_find(request))

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@pytest.fixture(name='merchant_profiles_id_by_personal_id')
def _mock_merchant_profiles_id_by_personal_id(mock_merchant_profiles):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mock_merchant_profiles(
            '/merchant/v1/merchant-profiles/id/retrieve_by_telegram_login_pd_id',  # noqa: E501 (line too long)
        )
        async def handler(request):
            if context.response is not None:
                return context.response
            return _response_wrapper(_merchant_profiles_id_retrieve(request))

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@dataclasses.dataclass
class MockedAuthorizationServicesContext:
    personal_telegram_logins_find: common.MockedHandlerContext
    merchant_profiles_id_by_personal_id: common.MockedHandlerContext  # noqa: E501 (line too long)

    def assert_services_called_once(self):
        assert self.personal_telegram_logins_find.handler.times_called == 1
        assert (
            self.merchant_profiles_id_by_personal_id.handler.times_called == 1
        )


@pytest.fixture(name='mock_authorization_services')
def _mock_authorization_services(
        mock_personal_telegram_logins_find,
        merchant_profiles_id_by_personal_id,
):
    return MockedAuthorizationServicesContext(
        personal_telegram_logins_find=mock_personal_telegram_logins_find(),
        merchant_profiles_id_by_personal_id=merchant_profiles_id_by_personal_id(),  # noqa: E501 (line too long)
    )
