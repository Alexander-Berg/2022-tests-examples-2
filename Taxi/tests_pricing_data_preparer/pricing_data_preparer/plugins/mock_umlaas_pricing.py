# pylint: disable=redefined-outer-name, import-error
import copy

from pricing_extended import mocking_base
import pytest


class UmlaasPricingContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = {'stat1': 1.0, 'stat2': 2.0}
        self._expected_request_source = 'pricing-data-preparer'
        self._expected_user_info = {
            'user_id': 'some_user_id',
            'phone_id': 'some_phone_id',
            'personal_phone_id': 'PERSONAL_PHONE_ID',
            'user_tags': [],
        }
        self._expected_tariff_zone = 'moscow'
        self._expected_offer_points = [[37.683, 55.774], [37.656, 55.764]]
        self._expected_route_distance = 2046.0
        self._expected_route_duration = 307.0

    def set_expected_offer_points(self, points):
        self._expected_offer_points = points

    def set_expected_user_info(self, user_info):
        self._expected_user_info = user_info

    def set_expected_request_source(self, expected_request_source):
        self._expected_request_source = expected_request_source

    def get_offer_statistics(self):
        return self.response

    def set_offer_statistic_response(self, value):
        self.response = copy.deepcopy(value)

    def check_request(self, request):
        assert request['request_source'] == self._expected_request_source
        assert 'pricing_prepare_link' in request
        assert request['user_info'] == self._expected_user_info
        assert request['tariff_zone'] == self._expected_tariff_zone
        assert request['offer_points'] == self._expected_offer_points
        assert request['route_distance'] == self._expected_route_distance
        assert request['route_duration'] == self._expected_route_duration


@pytest.fixture
def umlaas_pricing():
    return UmlaasPricingContext()


@pytest.fixture
def mock_umlaas_pricing(mockserver, umlaas_pricing):
    @mockserver.json_handler(
        '/umlaas-pricing/umlaas-pricing/v1/offer-statistics',
    )
    def offer_statistics_handler(request):
        data = request.json
        umlaas_pricing.check_request(data)
        look = umlaas_pricing.process(mockserver)
        return look

    return offer_statistics_handler
