import pytest

from tests_cargo_crm import const
from tests_cargo_crm.plugins.mocks.basic.basic_mock import BasicMock


@pytest.fixture(name='mocked_corp_clients')
async def _mocked_corp_clients(mockserver):
    class Context:
        def __init__(self):
            self.services_cargo = BasicMock()
            self.services_cargo.set_response(
                200,
                {
                    'deactivate_threshold_date': None,
                    'deactivate_threshold_ride': None,
                    'is_test': False,
                    'is_active': False,
                    'is_visible': False,
                },
            )

        @property
        def services_cargo_times_called(self):
            return _services_cargo.times_called

    context = Context()

    @mockserver.json_handler('/corp-clients-uservices/v1/services/cargo')
    async def _services_cargo(request):
        assert 'client_id' in request.query

        if request.method == 'PATCH':
            expected_data = context.services_cargo.get_expected_data()
            assert request.json == expected_data
            return mockserver.make_response(status=200, json={})

        response = context.services_cargo.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context
