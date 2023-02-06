import decimal
import json

import pytest

from partner_offers import api_parse_utils
from partner_offers import data_for_consumer
from partner_offers import models
from partner_offers import views
from partner_offers.generated.service.swagger.models import api

MODEL_VALUES = [
    models.Coupon(
        text='Hello',
        price=decimal.Decimal('5.700000000000000000005'),
        currency='USD',
    ),
    models.Discount(
        text='Hello', percent=decimal.Decimal('5.700000000000000000005'),
    ),
    models.FixPrice(
        old_price=decimal.Decimal('5.700000000000000000005'),
        new_price=decimal.Decimal('10.7'),
        old_currency='RUB',
        new_currency='EUR',
    ),
]

EXPECTED = [
    api.DealKindCoupon(
        text='Hello',
        price=api.Price(
            currency='USD', decimal_value='5.700000000000000000005',
        ),
    ),
    api.DealKindDiscount(
        text='Hello', decimal_percent='5.700000000000000000005',
    ),
    api.DealKindFixPrice(
        old_price=api.Price(
            currency='RUB', decimal_value='5.700000000000000000005',
        ),
        new_price=api.Price(currency='EUR', decimal_value='10.7'),
    ),
]

TAXIMETER_DEALS = [
    api.ConsumerTermsCoupon(text='Hello', price='5.700000000000000000005$'),
    api.ConsumerTermsDiscount(
        text='Hello', percent='5.700000000000000000005%',
    ),
    api.ConsumerTermsFixPrice(
        old_price='5.700000000000000000005₽', new_price='10.7€',
    ),
]


@pytest.mark.parametrize('kind,conversion_res', zip(MODEL_VALUES, EXPECTED))
def test_convert_internal_kind_to_api(kind, conversion_res):
    # pylint: disable=no-member
    allowed_types = models.DealMinimal.__annotations__['kind'].__args__
    assert [x for x in allowed_types if isinstance(kind, x)], (
        kind,
        allowed_types,
    )
    assert len(MODEL_VALUES) == len(allowed_types)
    assert len(MODEL_VALUES) == len(EXPECTED)
    result = views.convert_internal_kind_to_api(kind)
    assert repr(result) == repr(conversion_res)


@pytest.mark.parametrize('kind,source', zip(MODEL_VALUES, EXPECTED))
def test_convert_external_to_internal(kind, source):
    # pylint: disable=protected-access
    api_data = api_parse_utils._parse_kind(source)
    assert api_data == kind, api_data


@pytest.mark.parametrize('kind', MODEL_VALUES)
def test_convert_two_way(kind):
    serialized = json.loads(kind.as_json_str())
    assert kind == type(kind).from_json(serialized), serialized


@pytest.mark.parametrize('source,result', zip(MODEL_VALUES, TAXIMETER_DEALS))
def test_convert_taximeter(source, result):
    res = data_for_consumer._get_api_terms(  # pylint: disable=protected-access
        source, {'RUB': '₽', 'USD': '$', 'EUR': '€'},
    )
    assert repr(res) == repr(result)
