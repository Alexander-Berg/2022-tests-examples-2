import pytest


@pytest.fixture(name='taxi_requirements')
def _taxi_requirements(request, load_json):
    """
    For default taxi_requirements:
    @pytest.mark.taxi_requirements
    async def my_test(...)
    For custom taxi_requirements:
    @pytest.mark.taxi_requirements(filename='your_file.json')
    async def my_test(...)
    """
    context = TaxiRequirementsContext(load_json)

    for marker in request.node.iter_markers('taxi_requirements'):
        context.add_by_marker(marker)

    return context


@pytest.fixture
def mock_taxi_requirements(taxi_requirements, mockserver):
    @mockserver.json_handler('/requirements/v2/all_requirements/')
    def _mock_taxi_requirements_all(request):
        return {'data': taxi_requirements.data}


class TaxiRequirementsContext:
    data: dict = {}

    def __init__(self, load_json):
        self.load_json_func = load_json
        self.fill_data(filename='taxi_requirements.json')

    def add_by_marker(self, marker):
        if 'filename' in marker.kwargs:
            self.fill_data(filename=marker.kwargs['filename'])

    def fill_data(self, filename=None):
        self.data = self.load_json_func(filename)


def pytest_configure(config):
    config.addinivalue_line('markers', 'taxi_requirements: taxi requirements')
