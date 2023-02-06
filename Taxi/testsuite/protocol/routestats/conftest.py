import json
import shutil

import pytest

from protocol.routestats import utils


@pytest.fixture(autouse=True)
def clear_exp3_cache(exp3_cache_path):
    shutil.rmtree(exp3_cache_path, True)


class ServicesContext:
    def __init__(self):
        self.surge_value = 1
        self.is_lightweight_routestats = None

    def set_surge_value(self, value):
        self.surge_value = value

    def set_is_lightweight_routestats(self, value):
        self.is_lightweight_routestats = value


@pytest.fixture
def local_services_base(request, load_binary, load_json, mockserver):
    context = ServicesContext()

    @mockserver.json_handler('/alt/alt/v1/pin')
    def mock_alt_pin(request):
        body = json.loads(request.get_data())
        assert body['selected_class'] == 'econom'
        assert len(body['extra']['prices']) == 1
        assert body['surge_value']
        return load_json('altpoints.json')

    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_calculator(request):
        return utils.get_surge_calculator_response(
            request, context.surge_value,
        )

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def _mock_pin_storage(request):
        assert request.headers['Content-Type'] == 'application/json'
        assert request.headers.get('Expect') != '*'
        request_json = json.loads(request.get_data())
        assert 'pin' in request_json
        pin = request_json['pin']
        assert 'tariff_zone' in pin
        if context.is_lightweight_routestats is True:
            assert 'extra' in pin
            assert pin['extra'] == {'is_lightweight_routestats': True}

        return {'timestamp': '2021-01-01T00:00:00.000Z'}

    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    return context


class Context:
    def __init__(self):
        self.driver_eta_expected_classes = None
        self.driver_eta_request_expected_args = None
        self.driver_eta_expected_times_called = None
        self.driver_eta_request_expected_headers = None

    def set_driver_eta_expected_classes(self, classes):
        self.driver_eta_expected_classes = classes

    def set_driver_eta_request_expected_args(self, args_dict):
        self.driver_eta_request_expected_args = args_dict

    def set_driver_eta_request_expected_headers(self, headers_dict):
        self.driver_eta_request_expected_headers = headers_dict

    def set_driver_eta_expected_times_called(self, n):
        self.driver_eta_expected_times_called = n


@pytest.fixture
def local_services(local_services_base, request, load_json, mockserver):
    context = Context()

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        if context.driver_eta_expected_classes is not None:
            request_json = json.loads(request.get_data())
            assert (
                request_json['classes'] == context.driver_eta_expected_classes
            )

        if context.driver_eta_request_expected_args is not None:
            request_args = request.args
            for key, value in context.driver_eta_request_expected_args.items():
                assert request_args.get(key) == value

        expected_headers = context.driver_eta_request_expected_headers
        if expected_headers is not None:
            request_headers = request.headers
            for key, value in expected_headers.items():
                assert request_headers.get(key) == value

        return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    if context.driver_eta_expected_times_called is not None:
        assert (
            mock_driver_eta.times_called
            == context.driver_eta_expected_times_called
        )

    return context


@pytest.fixture
def local_services_fixed_price(local_services, request, mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        _data = json.loads(request.get_data())
        assert set(_data['fixed_price_classes']) >= set(_data['classes'])
        return utils.get_surge_calculator_response(request, 1)
