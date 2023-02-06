import uuid

import pytest


class DiscountsContext:
    def __init__(self):
        self.calls = 0
        self.discounts_by_classes = []
        self.discount_offer_id = str(uuid.uuid4())
        self.peek_discount_response = {'discounts': []}
        self.branding_by_zone_response = {'branding_items': []}
        self.calculate_discount_response = {
            'discounts': [],
            'discount_offer_id': '123456',
        }

    def set_discount_response(self, response):
        self.calculate_discount_response = response

    def set_peek_discount_response(self, response):
        self.peek_discount_response = response

    def set_branding_settings_by_zone_response(self, response):
        self.branding_by_zone_response = response


@pytest.fixture(autouse=True)
def discounts(mockserver):
    discounts_context = DiscountsContext()

    @mockserver.json_handler('/discounts/v1/calculate-discount')
    def _mock_get_discount(request):
        discounts_context.calls += 1
        return discounts_context.calculate_discount_response

    @mockserver.json_handler('/discounts/v1/peek-discount')
    def _mock_peek_discount(request):
        discounts_context.calls += 1
        return discounts_context.peek_discount_response

    @mockserver.json_handler('/discounts/v1/branding-settings-by-zone')
    def _mock_branding_settings_by_zone(request):
        discounts_context.calls += 1
        return discounts_context.branding_by_zone_response

    return discounts_context
