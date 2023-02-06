import aiohttp.web
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from gas_stations_api_plugins import *  # noqa: F403 F401


@pytest.fixture(name='gas_stations')
def _gas_stations(mockserver):
    @mockserver.json_handler('/gas-stations/internal/v1/offer/state')
    def _offer_state(request):
        db = {'park_with_offer': True, 'park_without_offer': False}
        park_state = db.get(request.json['park_id'])
        if park_state is not None:
            return {'is_offer_accepted': park_state}

        return aiohttp.web.json_response(
            {'code': '400', 'message': 'park not found'}, status=400,
        )

    return _offer_state
