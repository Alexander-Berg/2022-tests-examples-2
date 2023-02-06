import pytest

_TARIFFS_MARKER = 'tariffs_cache'
# Usage:
# @pytest.mark.tariffs_cache(filename='filename.json')
# Or
# @pytest.mark.tariffs_cache(data=
#   [
#     {
#       "id": "1234567890abba0987654321",
#       "home_zone": "hz",
#       "activation_zone": "hz_activation",
#       "related_zones": [
#         "hz123",
#         "hz456"
#       ],
#       "categories_names": [
#         "some_tariff"
#       ]
#     },
#     ...
#   ]
# )

_SERVICE = 'taxi-tariffs'
_V1_TARIFFS_URL = '/v1/tariffs'


class TariffsContext:
    def __init__(self, load_json):
        self.tariffs = []
        self.load_json = load_json

    def reset(self):
        self.tariffs = []

    def set_tariffs_from_file(self, filename):
        self.tariffs = self.load_json(filename)

    def set_tariffs_data(self, data):
        self.tariffs = data

    def get_tariffs(self):
        return self.tariffs


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_TARIFFS_MARKER}: tariffs cache')


@pytest.fixture(name='tariffs_mocks')
def _tariffs_mock(mockserver, load_json):
    tariffs_context = TariffsContext(load_json)

    @mockserver.json_handler(_SERVICE + _V1_TARIFFS_URL)
    def _mock_v1_tariffs(request):
        return {'tariffs': tariffs_context.get_tariffs()}

    return tariffs_context


@pytest.fixture(name='tariffs_fixture', autouse=True)
def _tariffs_fixture(tariffs_mocks, request):
    tariffs_mocks.reset()

    marker = request.node.get_closest_marker(_TARIFFS_MARKER)
    if marker:
        filename = marker.kwargs.get('filename')
        data = marker.kwargs.get('data')
        if filename is not None:
            tariffs_mocks.set_tariffs_from_file(filename)
        elif data is not None:
            tariffs_mocks.set_tariffs_data(data)

    yield tariffs_mocks

    tariffs_mocks.reset()
