import itertools

import pytest

from protocol.yauber import yauber


@pytest.mark.now('2017-02-02T13:00:00+0300')
def test_pricecat_ru(taxi_protocol):
    headers = {'Accept-Language': 'ru', 'User-Agent': yauber.user_agent}
    response = taxi_protocol.post(
        '3.0/pricecat?page=0', {'zone_name': 'moscow'}, headers=headers,
    )
    res = response.json()
    assert response.status_code == 200
    assert 'Cache-Control' in response.headers
    park_tariffs = [park['tariffs'] for park in res['parks']]
    all_tariffs = list(itertools.chain.from_iterable(park_tariffs))
    classes = [tariff['class'] for tariff in all_tariffs]
    assert set(classes) == set(['uberx', 'uberblack'])
