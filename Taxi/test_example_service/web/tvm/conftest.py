import pytest


@pytest.fixture
def patcher_tvm_ticket_check(patch):
    def _patcher(src_service_name):
        return _patch_tvm_ticket_check(patch, src_service_name)

    return _patcher


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'expected_service_name')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good':
            return src_service_name
        return None

    return get_service_name
