import pytest


@pytest.fixture(autouse=True)
def _mock_tvm(mockserver):
    @mockserver.handler('/tvm/ticket')
    def mock_tvm(request):
        return mockserver.make_response('2:1:Ticket', 200)
