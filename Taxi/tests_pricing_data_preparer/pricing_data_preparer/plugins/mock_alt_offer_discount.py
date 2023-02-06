# pylint: disable=redefined-outer-name, import-error
import json

from pricing_extended import mocking_base
import pytest


class AltOfferDiscountContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = {
            'offers': [{'type': 'perfect_chain', 'variables': {}}],
        }
        self.user = {'id': 'some_user_id', 'phone_id': 'PHONE_ID'}

    def set_param(self, name: str, value: float):
        self.response['offers'][0]['variables'][name] = value

    def clear_offers(self):
        self.response = {'offers': []}

    def clear_variables(self):
        self.response = {
            'offers': [{'type': 'perfect_chain', 'variables': {}}],
        }

    def check_request(self, request):
        data = json.loads(request.get_data())
        for key in ['request_id', 'route', 'zone', 'categories']:
            assert key in data
        if 'user' in data:
            if 'user_id' in data['user']:
                assert data['user']['user_id'] == self.user['id']
            if 'phone_id' in data['user']:
                assert data['user']['phone_id'] == self.user['phone_id']


@pytest.fixture
def alt_offer_discount():
    return AltOfferDiscountContext()


@pytest.fixture
def mock_alt_offer_discount(mockserver, alt_offer_discount):
    @mockserver.json_handler('/alt-offer-discount/v1/pricing-params')
    def v1_pricing_params(request):
        alt_offer_discount.check_request(request)
        return alt_offer_discount.process(mockserver)

    return v1_pricing_params
