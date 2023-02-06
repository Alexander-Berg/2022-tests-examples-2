import pytest


@pytest.fixture(name='hejmdal_start_event')
def _hejmdal_start_event(mock_hejmdal):
    @mock_hejmdal('/v1/external-event/start')
    async def start_event(request):
        assert request.method == 'POST'
        return {}

    return start_event


@pytest.fixture(name='hejmdal_finish_event')
def _hejmdal_finish_event(mock_hejmdal):
    @mock_hejmdal('/v1/external-event/finish')
    async def finish_event(request):
        assert request.method == 'POST'
        return {}

    return finish_event
