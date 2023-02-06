from typing import List

import pytest
import pytz

from taxi_billing_subventions.common import models
from taxi_billing_subventions.common.models import driver_modes


class EmptyRuleFetcher(driver_modes.RuleFetcher):
    async def on_order_ready_for_billing(
            self, doc: models.doc.OrderReadyForBilling,
    ) -> List[models.Rule]:
        return []

    async def on_driver_geoarea_activity(
            self, doc: models.doc.DriverGeoareaActivity,
    ) -> List[models.Rule]:
        return []

    async def on_order_commission_changed(
            self, doc: models.OrderCommissionChangedEvent,
    ) -> List[models.Rule]:
        return []

    async def on_order_subvention_changed(
            self, doc: models.OrderSubventionChangedEvent,
    ) -> List[models.Rule]:
        return []


@pytest.mark.parametrize(
    'reference_rule_id, events_json, expected_rules_json',
    [
        (
            '_id/5dc45e833fd694916ab26be1',
            'events.json',
            'rules_matched_by_id.json',
        ),
        (
            '_id/5dc45e833fd694916ab26be2',
            'events.json',
            'rules_matched_by_key.json',
        ),
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_driver_fix_rule_fetcher')
async def test_driver_fix_rule_fetcher(
        db, load_py_json, reference_rule_id, events_json, expected_rules_json,
):
    fetcher = driver_modes.DriverFixRuleFetcher(
        database=db,
        reference_rule_id=reference_rule_id,
        default_rule_fetcher=EmptyRuleFetcher(),
        tzinfo_by_zone={'moscow': pytz.timezone('Europe/Moscow')},
    )
    events = load_py_json(events_json)
    driver_geoarea_activity = events['driver_geoarea_activity']
    order_commission_changed = events['order_commission_changed']
    order_subvention_changed = events['order_subvention_changed']
    order_ready_for_billing = events['order_ready_for_billing']
    expected_rules = load_py_json(expected_rules_json)
    assert (
        await fetcher.on_driver_geoarea_activity(driver_geoarea_activity)
        == expected_rules
    )
    assert (
        await fetcher.on_order_commission_changed(order_commission_changed)
        == expected_rules
    )
    assert (
        await fetcher.on_order_subvention_changed(order_subvention_changed)
        == expected_rules
    )
    assert (
        await fetcher.on_order_ready_for_billing(order_ready_for_billing)
        == expected_rules
    )
