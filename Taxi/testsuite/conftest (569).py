import pytest

# root conftest for service scooters-mostrans
pytest_plugins = ['scooters_mostrans_plugins.pytest_plugins']


def _handler_mock(
        wrapper, marker_name, endpoint, request, mockserver, load_json,
):
    marker = request.node.get_closest_marker(marker_name)
    if marker:
        data = marker.kwargs.get('data', wrapper.get_default_data())

        filename = marker.kwargs.get('filename')
        if filename:
            data = load_json(filename)

        status_code = marker.kwargs.get('status_code', 200)

        if status_code != 200:
            wrapper.update(
                mockserver.make_response('fail', status=status_code),
            )
        else:
            wrapper.update(data)

    @mockserver.json_handler(endpoint)
    def _handler(request):
        return wrapper.get_response()

    wrapper.set_handler(_handler)

    return wrapper


class HandlerMockData:
    def __init__(self, default_data):
        self.default_data = default_data
        self.data = default_data
        self.handler = None

    def set_handler(self, handler):
        self.handler = handler

    def get_default_data(self):
        return self.default_data

    def update(self, data):
        self.data = data

    def get_response(self):
        return self.data


@pytest.fixture
def scooters_areas_mock(request, mockserver, load_json):
    return _handler_mock(
        HandlerMockData({'areas': []}),
        'scooters_mostrans_scooters_areas_mock',
        '/scooters-misc/scooters-misc/v1/areas',
        request,
        mockserver,
        load_json,
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'scooters_mostrans_scooters_areas_mock: scooters_areas_mock',
    )
