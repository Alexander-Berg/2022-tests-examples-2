# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from localizations_replica_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True, name='mock_tanker_keysets')
def _mock_tanker_keysets(mockserver):
    @mockserver.json_handler('/keysets/tjson/')
    def _mock_get_tanker_keysets(request, *args, **kwargs):
        assert request.headers['Authorization'] == 'OAuth token_oauth'
        return {}

    @mockserver.json_handler('/fhistory/')
    def _mock_get_tanker_fhistory(request, *args, **kwargs):
        assert request.headers['Authorization'] == 'OAuth token_oauth'
        return {
            'commits': [{'sha1': '4af4f56b2e880a2ce5dbbd7f9e4b858c77b98cf9'}],
        }
