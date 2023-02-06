import pytest

from billing_functions import consts


@pytest.mark.parametrize(
    'payment_type, is_cargo, expected',
    (
        (consts.PaymentType.CASH, False, 1),
        (consts.PaymentType.COOP_ACCOUNT, False, 1),
        (consts.PaymentType.CORP, False, 1),
        (consts.PaymentType.PERSONAL_WALLET, False, 1),
        (consts.PaymentType.PREPAID, False, 1),
        (consts.PaymentType.CARD, False, 2),
        (consts.PaymentType.APPLEPAY, False, 2),
        (consts.PaymentType.GOOGLEPAY, False, 2),
        (consts.PaymentType.AGENT, False, 2),
        (consts.PaymentType.YANDEX_CARD, False, 2),
        (consts.PaymentType.SBP, False, 2),
        (consts.PaymentType.CASH, True, 3),
        (consts.PaymentType.CARD, True, 4),
    ),
)
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'commission/cash': 1,
        'commission/card': 2,
        'cargo_commission/cash': 3,
        'cargo_commission/card': 4,
    },
)
def test_get_for_commission(payment_type, is_cargo, expected, *, stq3_context):
    repository = stq3_context.service_ids
    assert (
        repository.get_for_commission(payment_type, is_cargo).value == expected
    )


@pytest.mark.parametrize(
    'is_netting, is_cargo, expected',
    [(False, False, 1), (True, False, 2), (False, True, 3), (True, True, 4)],
)
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'coupon/paid': 1,
        'coupon/netted': 2,
        'cargo_coupon/paid': 3,
        'cargo_coupon/netted': 4,
    },
)
def test_get_for_coupon(is_netting, is_cargo, expected, *, stq3_context):
    repo = stq3_context.service_ids
    actual = repo.get_for_coupon(
        is_netting_allowed=is_netting, is_cargo=is_cargo,
    )
    assert actual.value == expected
