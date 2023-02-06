import pytest


@pytest.fixture(autouse=True)
def mock_experiments3_upstream(mockserver):
    @mockserver.json_handler('/experiments3-upstream/v1/experiments/updates/')
    def handler(request):
        return {'experiments': []}

    @mockserver.json_handler('/experiments3-upstream/v1/configs/updates/')
    def handler2(request):
        return {'configs': []}

    @mockserver.json_handler(
        '/experiments3-upstream/v1/experiments/filters/consumers/names/',
    )
    def handler3(request):
        return {'consumers': []}
