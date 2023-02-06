from library.offers import get_offers, confirm_offer
from library.mocks.offers import get_offer_data
from library.requests import finish_request
from library.registry import load_registry
from library.mocks.authorization import MIGUNOV_CLIENT_ID, STATION_MIGUNOV
import time


def test_create_offer_with_pricing():
    offers = get_offers(get_offer_data(STATION_MIGUNOV), MIGUNOV_CLIENT_ID, raise_for_status=True, need_pricing=True)
    assert len(offers) > 0
    request = confirm_offer(offers[0])
    finish_request(request)

def test_load_registry_with_pricing():
    assert load_registry(raise_for_status=True)
