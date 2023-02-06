# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from gas_stations_plugins import *  # noqa: F403 F401
import pytest

from tests_gas_stations import helpers


class PartnerContractsContext:
    def __init__(self):
        self.response = {}
        self.return_error = False
        self.get_inquiry_id = False
        self.requests = []

    def set_response(self, response):
        self.response = response

    def set_return_error(self):
        self.return_error = True


@pytest.fixture(name='partner_contracts')
def partner_contracts_request(mockserver):
    context = PartnerContractsContext()

    @mockserver.json_handler('/partner-contracts/v1/register_partner/rus/')
    def _park_list(request):
        context.requests.append(request)
        if context.return_error:
            return mockserver.make_response(
                json=helpers.RESPONSE500, status=500,
            )
        return context.response

    return context


class TankerContext:
    def __init__(self):
        self.response = ''
        self.return_error = False

    def set_response(self, response):
        self.response = response

    def set_return_error(self):
        self.return_error = True


@pytest.fixture(name='app_tanker')
def tanker_request(mockserver):
    context = TankerContext()

    @mockserver.json_handler('/app-tanker/api/corporation/taxi')
    def _taxi(request):
        if context.return_error:
            return mockserver.make_response(
                json=helpers.RESPONSE500, status=500,
            )
        return context.response

    return context
