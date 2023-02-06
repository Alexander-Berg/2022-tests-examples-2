import random

import pytest

from taxi.util import cars


@pytest.mark.filldb(_fill=True)
@pytest.mark.now('2015-12-23 18:04:00+05')
@pytest.mark.parametrize(
    'mark_code,model_code,age,expected_price',
    [
        # In db, and cache valid
        ('Chevrolet', 'Niva', 2013, 500000),
        # In db and valid, but price is unknown
        ('Jeep', 'Cherokee', 1998, -1),
        # Price unknown, and the closest year (up) is in db
        ('Chevrolet', 'Niva', 2012, 450000),
        # Price unknown, and the closest year (down) is in db
        ('Chevrolet', 'Niva', 2014, 550000),
        # Closest year in the db has no known price
        ('Jeep', 'Cherokee', 1999, -1),
        # Price unknown, and the car is unknown too
        ('ZAZ', '968', 1981, -1),
        # Error when parsing the response
        ('Tesla', 'Model S', 2014, -1),
    ]
)
@pytest.inline_callbacks
def test_corrector_detect_price(mark_code, model_code, age,
                                expected_price, patch, load):
    corrector = cars.Corrector()
    corrector.prepare()
    corrector.warmup()

    price_key = cars.build_price_key(mark_code, model_code, age)

    price = yield corrector.detect_price(mark_code, model_code, age)
    if expected_price > 0:
        assert int(price) == expected_price
    else:
        assert price == -1

    # Check that we can use cached value
    fake_price = random.randint(100000, 1000000)
    assert fake_price != price  # just to be sure
    corrector.price_cache[price_key] = {'price': fake_price}

    price = yield corrector.detect_price(mark_code, model_code, age)
    assert price == fake_price
