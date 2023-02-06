# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from garage_api_plugins import *  # noqa: F403 F401


def params_equals(request, file_request, params):
    return all([request[i] == file_request[i] for i in params])


def request2response(request, file, params):
    for mock_i in file:
        if params_equals(request, mock_i['request'], params):
            return mock_i['response']
    return None


@pytest.fixture()
def classifier_mock_200(mockserver, load_json):
    @mockserver.json_handler('/classifier/v1/vehicle-classification')
    def _mock_vehicle_classification(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=200,
            json=request2response(
                request.json, load_json('classifier.json'), ['brand_model'],
            ),
        )


@pytest.fixture()
def classifier_mock_404(mockserver, load_json):
    @mockserver.json_handler('/classifier/v1/vehicle-classification')
    def _mock_vehicle_classification(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Ony one'},
        )


@pytest.fixture()
def cars_catalog_mock_200(mockserver, load_json):
    @mockserver.json_handler('/cars-catalog/v1/vehicles/check-stats')
    def _mock_vehicles_check_stats(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            status=200,
            json=request2response(
                request.query,
                load_json('cars_catalog.json'),
                ['mark', 'model'],
            ),
        )


@pytest.fixture()
def cars_catalog_mock_400(mockserver):
    @mockserver.json_handler('/cars-catalog/v1/vehicles/check-stats')
    def _mock_vehicles_check_stats(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Ony one'},
        )


@pytest.fixture()
def cars_catalog_mock_404(mockserver):
    @mockserver.json_handler('/cars-catalog/v1/vehicles/check-stats')
    def _mock_vehicles_check_stats(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Ony one'},
        )
