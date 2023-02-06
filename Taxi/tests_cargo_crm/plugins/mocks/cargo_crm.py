import pytest

from tests_cargo_crm import const
from tests_cargo_crm.plugins.mocks.basic.basic_mock import BasicMock


@pytest.fixture(name='mocked_cargo_crm')
async def _mocked_cargo_crm(mockserver):
    class Context:
        def __init__(self):
            self.notification_contract_accepted = BasicMock()

        @property
        def notification_contract_accepted_times_called(self):
            return _notification_contract_accepted.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-crm/internal/cargo-crm/notification/contract-accepted',
    )
    async def _notification_contract_accepted(request):
        assert (
            request.json
            == context.notification_contract_accepted.get_expected_data()
        )
        response = context.notification_contract_accepted.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context
