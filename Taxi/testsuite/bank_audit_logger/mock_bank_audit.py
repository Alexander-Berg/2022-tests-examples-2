import pytest


@pytest.fixture(autouse=True)
def bank_audit(mockserver):
    @mockserver.json_handler('/bank-core-audit-log-http-collector/v1/message')
    def _handler(request):
        return mockserver.make_response(status=204)
