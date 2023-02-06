import pytest


@pytest.fixture
def dummy_feedback(mockserver):
    @mockserver.json_handler('/feedback/1.0/retrieve')
    def mock_retrieve(request):
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/feedback/1.0/wanted/retrieve')
    def mock_wanted(request):
        return {'orders': []}
