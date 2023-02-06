import json

import pytest


_UPDATES_MARKER = 'parks_activation_updates'
_SERVICE = '/parks-activation'
# Usage: @pytest.mark.parks_activation_updates(
#            parks = [
#                {
#                    'revision': 1,
#                    'last_modified': '1970-01-15T03:56:07.000',
#                    'park_id': 'park1',
#                    'city_id': 'city1',
#                    'data': {
#                        'deactivated': True,
#                        'deactivated_reason': 'reason1',
#                        'can_cash': False,
#                        'can_card': False,
#                        'can_coupon': True,
#                        'can_corp': False,
#                     },
#                },
#                ...
#            ]
#        )
_UPDATES_URL = '/v1/parks/activation/updates'


class ParksActivationContext:
    def __init__(self):
        self.parks = []

    def reset(self):
        self.parks = []

    def set_parks(self, parks):
        self.parks = list(sorted(parks, key=lambda x: x['revision']))


@pytest.fixture(name='parks_activation_mocks')
def _parks_activation_mocks(mockserver):
    parks_activation_context = ParksActivationContext()

    @mockserver.handler(_SERVICE + _UPDATES_URL)
    def _mock_updates(request):
        last_known_revision = request.json.get('last_known_revision', -1)
        limit = request.json.get('limit', 3000)
        additional_revisions = request.json.get('additional_revisions')

        parks = []
        if additional_revisions:
            for park in parks_activation_context.parks:
                if park['revision'] in additional_revisions:
                    parks.append(park)

        for park in parks_activation_context.parks:
            if park['revision'] > last_known_revision and len(parks) < limit:
                parks.append(park)

        last_revision = parks[-1]['revision'] if parks else 0
        response = {'last_revision': last_revision, 'parks_activation': parks}
        return mockserver.make_response(json.dumps(response), 200)

    return parks_activation_context


@pytest.fixture(name='parks_activation_fixture', autouse=True)
def _parks_activation_fixture(parks_activation_mocks, request):
    parks_activation_mocks.reset()

    marker = request.node.get_closest_marker(_UPDATES_MARKER)
    if marker:
        parks_activation_mocks.set_parks(**marker.kwargs)

    yield parks_activation_mocks

    parks_activation_mocks.reset()
