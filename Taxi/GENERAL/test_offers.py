from library.offers import get_offers, confirm_offer
from library.mocks.offers import get_offer_data, get_pvz_data
from library.mocks.authorization import MIGUNOV_CLIENT_ID, STATION_MIGUNOV, STATION_YD, YD_OFFERS_CLIENT_ID, STATION_YD_PVZ, STATION_BEFORE_PVZ, PVZ_CLIENT_ID, STATION_YD_TARN


def test_offers():
    offers = get_offers(get_offer_data(STATION_MIGUNOV), MIGUNOV_CLIENT_ID, raise_for_status=True)
    assert len(offers) > 0


def test_offers_yd():
    offers = get_offers(get_offer_data(STATION_YD), YD_OFFERS_CLIENT_ID, raise_for_status=True)
    assert len(offers) > 0


def test_offers_pvz():
    offers = get_offers(get_pvz_data(STATION_BEFORE_PVZ, STATION_YD_PVZ), PVZ_CLIENT_ID, raise_for_status=True)
    assert len(offers) > 0
    confirmation_result = confirm_offer(offers[-1], PVZ_CLIENT_ID)
    assert confirmation_result
    print(confirmation_result)


if __name__ == '__main__':
    test_offers_pvz()
