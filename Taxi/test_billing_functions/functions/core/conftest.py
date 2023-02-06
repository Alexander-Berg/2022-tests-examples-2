import datetime as dt
import decimal
import uuid

import pytest

from billing_functions.repositories import commission_agreements as ca


@pytest.fixture(name='make_agreement')
def _make_agreement():
    def _builder(
            *,
            kind,
            group,
            rate,
            unrealized_rate=None,
            unrealized_commission=None,
            vat_rate=decimal.Decimal('1.1'),
            agreement_id=None,
            category=None,
    ):
        cancellation_settings = ca.CancellationSettings(
            billable_cancel_distance=10,
            billable_user_interval=ca.CancellationInterval(
                before_order_due=dt.timedelta(seconds=1),
                after_order_due=dt.timedelta(seconds=10),
            ),
            billable_park_interval=ca.CancellationInterval(
                before_order_due=dt.timedelta(seconds=1),
                after_order_due=dt.timedelta(seconds=10),
            ),
        )
        return ca.Agreement(
            id=agreement_id or uuid.uuid4(),
            rate=rate,
            unrealized_commission=unrealized_commission,
            unrealized_rate=unrealized_rate,
            vat_rate=vat_rate,
            group=group,
            kind=kind,
            category=category,
            effective_billing_type='_billing_type',
            branding_discounts=[],
            cancellation_settings=cancellation_settings,
            cost_info=None,
            support_info=None,
            settings=None,
        )

    return _builder
