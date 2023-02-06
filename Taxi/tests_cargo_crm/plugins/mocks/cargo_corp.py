import pytest

from tests_cargo_crm import const
from tests_cargo_crm.plugins.mocks.basic.basic_mock import BasicMock


@pytest.fixture(name='get_corp_list', autouse=True)
def _corp_list(mockserver):
    class Context:
        def __init__(self):
            self.response_code = 200
            self.response_json = {'corp_clients': []}

        def set_response(self, response_code, response_json):
            self.response_code = response_code
            self.response_json = response_json

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/employee/corp-client/list',
    )
    def _handler(request):
        assert request.query['role_name'] == const.OWNER_ROLE
        return mockserver.make_response(
            status=context.response_code, json=context.response_json,
        )

    return context


@pytest.fixture(name='get_employee_list', autouse=True)
def _employee_list(mockserver):
    class Context:
        def __init__(self):
            self.response_code = 200
            self.response_json = {'employees': []}

        def set_response(self, response_code, response_json):
            self.response_code = response_code
            self.response_json = response_json

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/employee/list',
    )
    def _handler(request):
        return mockserver.make_response(
            status=context.response_code, json=context.response_json,
        )

    return context


@pytest.fixture(name='mocked_cargo_corp')
async def _mocked_cargo_corp(mockserver):
    class Context:
        def __init__(self):
            self.contract_get_active_status = BasicMock()

        @property
        def contract_get_active_status_times_called(self):
            return _contract_get_active_status.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/contract/get-active-status',
    )
    async def _contract_get_active_status(request):
        response = context.contract_get_active_status.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context
