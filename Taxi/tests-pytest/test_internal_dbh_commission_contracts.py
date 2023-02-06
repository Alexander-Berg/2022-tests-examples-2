import datetime

import pytest

from taxi.internal import dbh
from taxi.internal import commission_manager


@pytest.mark.filldb(
    commission_contracts='for_test_find_many_by_conditions',
)
@pytest.mark.parametrize(
    'payment_type,zone,tariff_class,find_subset_conditions,expected_ids', [
        (
            'card', 'moscow', 'uberx', False,
            {
                'some_old_moscow_uberx_card_contract_id',
                'some_new_moscow_uberx_card_contract_id',
            }
        ),
        # we don't find more specific contracts if tariff_class = None
        (
            'card', 'moscow', None, False,
            {
                'some_new_moscow_card_contract_id',
            }
        ),
    ]
)
@pytest.inline_callbacks
def test_find_many_by_conditions(
        payment_type, zone, tariff_class, find_subset_conditions,
        expected_ids):
    conditions = commission_manager.Conditions(
        payment_type=payment_type,
        zone=zone,
        tariff_class=tariff_class,
        city=None,
        tag=None,
    )
    contracts = yield dbh.commission_contracts.Doc.find_many_by_conditions(
        begins_before_or_at=datetime.datetime.max,
        ends_after=datetime.datetime.min,
        conditions=conditions,
        find_subset_conditions=find_subset_conditions,
    )
    actual_ids = dbh.commission_contracts.Doc.get_ids(contracts)
    assert set(actual_ids) == expected_ids
