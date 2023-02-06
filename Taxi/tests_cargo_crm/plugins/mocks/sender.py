import pytest
from tests_cargo_crm.plugins.mocks.basic.basic_mock import BasicMock


@pytest.fixture(name='sender_mocks')
async def _sender_mocks(mockserver):
    class Context:
        def __init__(self):
            self.send_autogen_credentials_slug = BasicMock()

        @property
        def send_autogen_credentials_slug_times_called(self):
            return _send_autogen_credentials_slug.times_called

    context = Context()

    @mockserver.json_handler(
        '/sender/api/0/ya.delivery/transactional/autogen_credentials_slug/send',
    )
    async def _send_autogen_credentials_slug(request):
        expected_data = (
            context.send_autogen_credentials_slug.get_expected_data()
        )
        assert request.json == expected_data

        response = context.send_autogen_credentials_slug.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context
