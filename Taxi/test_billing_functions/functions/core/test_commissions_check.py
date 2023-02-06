import datetime as dt
import decimal
from typing import Optional

import pytest

from billing_functions import consts
from billing_functions.functions.core.commissions import check
from billing_functions.functions.core.commissions import models
from billing_functions.repositories import commission_agreements


ClientStatus = consts.OrderStatus
TaxiStatus = consts.OrderTaxiStatus
PaymentType = consts.PaymentType
CancellationSettings = commission_agreements.CancellationSettings
CancellationInterval = commission_agreements.CancellationInterval


def make_context(
        cancel_distance: Optional[float] = None,
        cancelled_at: Optional[dt.datetime] = None,
        cancelled_with_captcha: bool = False,
        cost: decimal.Decimal = decimal.Decimal('0'),
        due: dt.datetime = dt.datetime(2021, 5, 9, tzinfo=dt.timezone.utc),
        need_dispatcher_acceptance: bool = False,
        payment_type: consts.PaymentType = consts.PaymentType.CARD,
        status: str = ClientStatus.FINISHED.value,
        taxi_status: str = TaxiStatus.COMPLETE.value,
):
    return check.Context(**locals())


@pytest.mark.parametrize(
    'context, expected_result',
    [
        (make_context(), models.Match()),
        (
            make_context(
                status=ClientStatus.CANCELLED.value,
                cost=decimal.Decimal('100'),
            ),
            models.Match(
                details={'billable_cancel': {'reason': 'is_paid_cancel'}},
            ),
        ),
        (
            make_context(
                status=ClientStatus.CANCELLED.value,
                taxi_status=TaxiStatus.TRANSPORTING.value,
            ),
            models.Match(),
        ),
        (
            make_context(status=ClientStatus.CANCELLED, cancel_distance=9),
            models.Mismatch(
                reason='close_distance_cancel',
                details={
                    'canceler': 'user',
                    'cancel_distance': 9,
                    'min_cancel_distance_to_take_commission': 10,
                },
            ),
        ),
        (
            make_context(
                status=ClientStatus.CANCELLED.value,
                cancelled_at=dt.datetime(
                    2021, 5, 9, second=11, tzinfo=dt.timezone.utc,
                ),
            ),
            models.Mismatch(
                reason='remote_in_time_cancel',
                details={
                    'canceler': 'user',
                    'billable_interval': (
                        '2021-05-08T23:59:59.000000+00:00',
                        '2021-05-09T00:00:10.000000+00:00',
                    ),
                    'canceled_at': '2021-05-09T00:00:11.000000+00:00',
                },
            ),
        ),
        (
            make_context(
                taxi_status=TaxiStatus.CANCELLED.value,
                cancel_distance=9,
                cancelled_at=dt.datetime(2021, 5, 8, tzinfo=dt.timezone.utc),
            ),
            models.Mismatch(
                reason='early_cancel',
                details={
                    'canceler': 'park',
                    'canceled_at': '2021-05-08T00:00:00.000000+00:00',
                    'min_canceled_at_to_take_commission': (
                        '2021-05-08T23:59:59.000000+00:00'
                    ),
                },
            ),
        ),
        (
            make_context(
                taxi_status=TaxiStatus.CANCELLED.value,
                cancel_distance=11,
                cancelled_at=dt.datetime(
                    2021, 5, 9, second=11, tzinfo=dt.timezone.utc,
                ),
            ),
            models.Match(
                details={
                    'billable_cancel': {
                        'reason': 'early_far_cancel',
                        'min_datetime': '2021-05-08T23:59:59.000000+00:00',
                        'canceled_at': '2021-05-09T00:00:11.000000+00:00',
                        'cancel_distance': 11,
                        'min_cancel_distance_to_take_commission': 10,
                    },
                },
            ),
        ),
    ],
)
def test_is_billable(context, expected_result):
    billable_match_info = check.is_billable(
        context,
        CancellationSettings(
            billable_cancel_distance=10,
            billable_user_interval=CancellationInterval(
                before_order_due=dt.timedelta(seconds=1),
                after_order_due=dt.timedelta(seconds=10),
            ),
            billable_park_interval=CancellationInterval(
                before_order_due=dt.timedelta(seconds=1),
                after_order_due=dt.timedelta(seconds=10),
            ),
        ),
    )
    assert billable_match_info == expected_result
