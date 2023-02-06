import pytest


@pytest.fixture(name='personal_mock')
def _personal_mock(mock_personal, mockserver, load_json):
    @mock_personal('/v1/emails/bulk_store')
    async def _store_emails(request):
        resp = load_json('emails_data.json')
        return resp


@pytest.fixture(name='sticker_mock')
def _sticker_mock(mock_sticker, mockserver):
    @mock_sticker('/send/')
    async def _send(request):
        return {}
