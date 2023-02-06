import pytest


@pytest.fixture(name='clowny_alert_manager_recipients_set_default')
def _clowny_alert_manager_recipients_set_default(mock_clowny_alert_manager):
    @mock_clowny_alert_manager('/v1/recipients/unified/set-default/')
    async def recipients_set_default(request):
        assert request.method == 'POST'
        return {}

    return recipients_set_default
