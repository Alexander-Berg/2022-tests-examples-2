# pylint: disable=import-error
import pytest

from . import utils


class ContractorTransportContext:
    def __init__(self):
        self.transport_types = {}

    def set_transport_type(
            self,
            park_id='park_id',
            contractor_profile_id='profile_id',
            transport_type=None,
    ):
        profile_id = utils.make_profile_id(park_id, contractor_profile_id)
        self.transport_types[profile_id] = transport_type


@pytest.fixture(autouse=True)
def contractor_transport(mockserver, load_json):
    context = ContractorTransportContext()

    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/retrieve-by-contractor-id',
    )
    def _retrieve(request):
        contractors_transport = []
        for profile_id in request.json['id_in_set']:
            if profile_id not in context.transport_types:
                continue
            transport_type = context.transport_types[profile_id]
            if transport_type is None:
                continue
            contractors_transport.append(
                {
                    'contractor_id': profile_id,
                    'transport_active': {'type': transport_type},
                    'revision': '1',
                },
            )
        response_body = {'contractors_transport': contractors_transport}
        return mockserver.make_response(status=200, json=response_body)

    return context
