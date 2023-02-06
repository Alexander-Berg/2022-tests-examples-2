from decimal import Decimal

import pytest

from taxi import billing

from taxi_billing_subventions import common
from taxi_billing_subventions.common import models


@pytest.mark.filldb(tariffs='for_test_fetch_tariff_category')
async def test_fetch_tariff_category(db):
    tariff = await common.db.fetch_tariff_category(db, 'cat1')
    minimal_cost = billing.Money(Decimal(2), 'CCY1')
    assert tariff == models.order.Tariff(
        minimal_cost=minimal_cost,
        modified_minimal_cost=minimal_cost,
        class_='class1',
    )


@pytest.mark.filldb(tariffs='for_test_fetch_tariff_category')
# pylint: disable=invalid-name
async def test_fetch_tariff_category_raises_not_found_error(db):
    with pytest.raises(common.db.TariffNotFoundError):
        await common.db.fetch_tariff_category(db, 'cat5')
