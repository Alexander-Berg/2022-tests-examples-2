# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import sticker.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['sticker.generated.service.pytest_plugins']


@pytest.fixture
def mock_tvm(patch):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body: bytes, **kwargs):
        if ticket_body == b'good':
            return 'src_test_service'
        if ticket_body == b'auth_fail':
            return None
        return ticket_body.decode()

    return get_service_name


@pytest.fixture(autouse=True)
def _patch_sticker_gen_message_id(patch):
    @patch('sticker.mail.smailik.xml._gen_message_id')
    def _patch():
        return 'hex'
