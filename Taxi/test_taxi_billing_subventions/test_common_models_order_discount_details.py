from taxi import billing

from taxi_billing_subventions.common import models


def test_zero():
    actual = models.order.DiscountDetails.zero('RUB')
    expected = models.order.DiscountDetails(
        billing.Money.zero('RUB'), amendments=[],
    )
    assert expected == actual
