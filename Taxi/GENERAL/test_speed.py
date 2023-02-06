import copy
import json
import requests
import statistics
import time


TM = int(time.time())
TM_DAY_START = TM - TM % 86400 + 86400
TM_DAY_SEVEN = TM_DAY_START + 7 * 3600
N_ATTEMPTS = 15


SOURCE = {
    "type": "market_station",
    "market_station": {
        "lms_id": 10000967620
    },
    "interval": {
        "from": TM_DAY_START,
        "to": TM_DAY_START
    }
}

DESTINATION = {
    "type": "custom_location",
    "custom_location": {
        "latitude": 55.724887,
        "longitude": 37.568111
    },
    "interval": {
        "from": 0,
        "to": 0
    }
}

BASE_OFFERS_CHECK_PAYLOAD = {
    "item": {
        "weight": 5000,
        "dx": 100,
        "dy": 70,
        "dz": 20,
    },
    "last_mile_policy": "time_interval",
}


def _test_offers_check(days, hour_slots_in_day, create_offers, testcase_name):
    payload = copy.deepcopy(BASE_OFFERS_CHECK_PAYLOAD)
    offers = []
    for i in range(days):
        for j in range(hour_slots_in_day):
            source = copy.deepcopy(SOURCE)
            dest = copy.deepcopy(DESTINATION)

            ifrom = TM_DAY_SEVEN + (i + 1) * 86400 + j * 3600
            ito = ifrom + 3600

            dest["interval"]["from"] = ifrom
            dest["interval"]["to"] = ito

            offer = {}
            offer["source"] = source
            offer["destination"] = dest
            offers.append(offer)

    payload["offers"] = offers
    payload["create_offers"] = create_offers
    timings = []
    for _ in range(N_ATTEMPTS):
        time_before_request = time.time()
        r = requests.post(
            "http://logistic-platform.taxi.tst.yandex.net/api/platform/offers/check",
            json=payload
        )
        r.raise_for_status()
        time_elapsed = time.time() - time_before_request
        timings.append(time_elapsed)
    timings.sort()

    print(testcase_name, statistics.median(timings))
    assert statistics.median(timings) < 0.1


def test_offers_check_nooffer_speed():
    _test_offers_check(5, 12, False, 'test_offers_check_nooffer_speed')


def test_offers_check_offer_speed():
    _test_offers_check(1, 1, True, 'test_offers_check_offer_speed')


if __name__ == '__main__':
    test_offers_check_nooffer_speed()
    test_offers_check_offer_speed()
