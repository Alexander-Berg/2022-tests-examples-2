# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest

from coord_control_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def contractor_transport_request(request, mockserver, load_json):
    marker = request.node.get_closest_marker('contractors_transport')
    data = marker.args[0] if marker else load_json('contractors_default.json')

    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == data['cursor']:
            return {'contractors_transport': [], 'cursor': '1234567_4'}
        return mockserver.make_response(response=json.dumps(data))
