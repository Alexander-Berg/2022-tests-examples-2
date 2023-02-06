import pytest


@pytest.fixture(autouse=True)
def vgw_api_default_handlers(mockserver):
    @mockserver.json_handler('/vgw-api/v1/voice_gateways')
    def mock_voice_gateways(request):
        return []
