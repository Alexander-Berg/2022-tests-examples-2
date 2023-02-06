"""
Mock for localizations-replica.
"""

import pytest

NAME = 'name'
LAST_UPDATE = 'last_update'


@pytest.fixture(autouse=True)
def mock_localizations_replica(localizations, mockserver):
    @mockserver.json_handler('/v1/keyset')
    def handler(request):
        if NAME not in request.args:
            return mockserver.make_response('BadRequest', 400)
        keyset_name = request.args[NAME]
        if LAST_UPDATE in request.args:
            last_update = request.args[LAST_UPDATE]
            if localizations.is_up_to_data(keyset_name, last_update):
                return mockserver.make_response('NotModified', 304)
        keyset = localizations.get_keyset(keyset_name)
        if keyset is None:
            response_json = {
                'keyset_name': keyset_name,
                'last_update': '1970-01-01T12:34:56.789+0000',
                'keys': [],
            }
            return response_json
        return keyset
