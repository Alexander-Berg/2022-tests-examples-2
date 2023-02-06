import decimal

import pytest

from billing_functions.functions.core.subventions import netting


@pytest.mark.parametrize(
    'args,expected',
    (
        ({'default': 'none', 'mfg': 'none'}, True),
        ({'default': 'none', 'mfg': 'full'}, True),
        ({'default': 'none', 'mfg': 'base_commission'}, True),
        ({'default': 'full', 'mfg': 'none'}, True),
        ({'default': 'full', 'mfg': 'full'}, False),
        ({'default': 'full', 'mfg': 'base_commission'}, False),
    ),
)
def test_netting_has_payable(args, expected):
    cfg = {k: netting.Config.Mode(v) for k, v in args.items()}
    assert netting.Config(**cfg).has_payable() is expected


@pytest.mark.parametrize(
    'config,amount,sum_to_net,expected_payments,expected_sum_to_net',
    (
        (
            # no netting
            netting.Config.Mode.NONE,
            decimal.Decimal('10'),
            decimal.Decimal('5'),
            [netting.NettedPayment(decimal.Decimal('10'), False)],
            decimal.Decimal('5'),
        ),
        (
            # full netting
            netting.Config.Mode.FULL,
            decimal.Decimal('10'),
            decimal.Decimal('5'),
            [netting.NettedPayment(decimal.Decimal('10'), True)],
            decimal.Decimal('5'),
        ),
        (
            # partial netting with zero to net
            netting.Config.Mode.AT_MOST_SUM_TO_NET,
            decimal.Decimal('10'),
            decimal.Decimal(),
            [netting.NettedPayment(decimal.Decimal('10'), False)],
            decimal.Decimal(),
        ),
        (
            # partial netting with sum to net equal to amount
            netting.Config.Mode.AT_MOST_SUM_TO_NET,
            decimal.Decimal('10'),
            decimal.Decimal('10'),
            [netting.NettedPayment(decimal.Decimal('10'), True)],
            decimal.Decimal(),
        ),
        (
            # partial netting with larger sum to net
            netting.Config.Mode.AT_MOST_SUM_TO_NET,
            decimal.Decimal('10'),
            decimal.Decimal('15'),
            [netting.NettedPayment(decimal.Decimal('10'), True)],
            decimal.Decimal('5'),
        ),
        (
            # partial netting with smaller sum to net
            netting.Config.Mode.AT_MOST_SUM_TO_NET,
            decimal.Decimal('10'),
            decimal.Decimal('7'),
            [
                netting.NettedPayment(decimal.Decimal('7'), True),
                netting.NettedPayment(decimal.Decimal('3'), False),
            ],
            decimal.Decimal('0'),
        ),
    ),
)
def test_netting_calculator(
        config, amount, sum_to_net, expected_sum_to_net, expected_payments,
):
    calculator = netting.Config(default=config).get_calculator()
    payments, new_sum_to_net = calculator(amount=amount, sum_to_net=sum_to_net)
    assert payments == expected_payments
    assert new_sum_to_net == expected_sum_to_net
