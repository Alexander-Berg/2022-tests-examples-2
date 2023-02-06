import decimal

import pytest

import payments_eda.consts as consts
import payments_eda.utils.split_payment as split_payment

CARD_ID = 'card-x5a4adedaf78dba6f9c56fee4'
WALLET_ID = 'wallet_id/1234567890'


def get_two_payments(
        current_balance=None,
        held=None,
        max_absolute_value=None,
        sum_to_pay=None,
):
    card_payment = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_CARD, method_id=CARD_ID,
    )

    wallet_payment = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_WALLET,
        method_id=WALLET_ID,
        max_absolute_value=max_absolute_value,
        held=held,
        sum_to_pay=sum_to_pay,
        current_balance=current_balance,
    )

    return [card_payment, wallet_payment]


@pytest.mark.parametrize('max_absolute_value', (None, '50', '200'))
@pytest.mark.parametrize('held', (None, '50', '200'))
@pytest.mark.parametrize('current_balance', (None, '50', '200'))
def test_normal_split_with_one_payment(
        max_absolute_value, held, current_balance,
):
    payment = split_payment.PaymentMethodModel(
        type='personal_wallet',
        method_id=WALLET_ID,
        max_absolute_value=max_absolute_value,
        held=held,
        current_balance=current_balance,
    )

    payment_split = split_payment.split_payment(
        amount='100', payments=[payment],
    )
    assert len(payment_split) == 1
    assert payment_split[0].sum_to_pay == 100


@pytest.mark.parametrize('max_absolute_value', (None, '50', '200'))
@pytest.mark.parametrize('held', (None, '50', '200'))
@pytest.mark.parametrize('current_balance', (None, '50', '200'))
def test_normal_split_with_two_payments(
        max_absolute_value, held, current_balance,
):
    if current_balance is None and held is None:
        return

    payments = get_two_payments(
        max_absolute_value=max_absolute_value,
        held=held,
        current_balance=current_balance,
    )

    payment_split = split_payment.split_payment(
        amount='100', payments=payments,
    )

    assert payment_split
    assert sum(split.sum_to_pay for split in payment_split) == decimal.Decimal(
        '100',
    )
    if max_absolute_value is not None:
        assert all(
            decimal.Decimal(split.sum_to_pay)
            <= decimal.Decimal(max_absolute_value)
            for split in payment_split
            if split.payment.type == consts.PAYMENT_TYPE_WALLET
        )


@pytest.mark.parametrize(
    'max_absolute_value,held,current_balance',
    (('100', '0', '100'), ('-1', '100', '100')),
)
def test_raises_on_incorrect_payment(
        max_absolute_value, held, current_balance,
):
    payments = get_two_payments(
        max_absolute_value=max_absolute_value,
        held=held,
        current_balance=current_balance,
    )

    with pytest.raises(split_payment.SplitError):
        split_payment.split_payment(amount='100', payments=payments)


def test_raises_on_lack_of_personal_wallet():
    card_payment = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_CARD, method_id=CARD_ID,
    )

    not_wallet_payment = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_CORP,
        method_id=WALLET_ID,
        current_balance='100',
    )

    with pytest.raises(split_payment.SplitError):
        split_payment.split_payment(
            amount='200', payments=[card_payment, not_wallet_payment],
        )


@pytest.mark.parametrize('amount', ('150', '250'))
def test_raises_on_unequal_balances(amount):
    card_payment = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_CARD,
        method_id=CARD_ID,
        current_balance='100',
    )

    wallet_payment = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_WALLET,
        method_id=WALLET_ID,
        current_balance='100',
    )

    payments = [card_payment, wallet_payment]

    with pytest.raises(split_payment.SplitError):
        split_payment.split_payment(amount=amount, payments=payments)


def test_common_case():
    # moloko == 40
    # kefir == 50
    # hleb == 45
    # max_absolute_value == 100
    amount = '135'

    card = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_CARD, method_id=CARD_ID,
    )
    wallet = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_WALLET,
        method_id=WALLET_ID,
        current_balance='120',
        max_absolute_value='100',
    )
    expected_split = {
        split_payment.SplitModel(
            payment=wallet, sum_to_pay=decimal.Decimal(100),
        ),
        split_payment.SplitModel(payment=card, sum_to_pay=decimal.Decimal(35)),
    }
    splitted = split_payment.split_payment(
        amount=amount, payments=[card, wallet],
    )

    assert len(splitted) == 2
    assert set(splitted) == expected_split

    # moloko == 12
    # kefir == 12 - refund this
    # hleb == 11
    # discount == 100
    amount = '85'

    card = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_CARD,
        method_id=CARD_ID,
        sum_to_pay='23',  # moloko + hleb
    )
    wallet = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_WALLET,
        method_id=WALLET_ID,
        max_absolute_value='100',
    )

    expected_split = {
        split_payment.SplitModel(
            payment=wallet, sum_to_pay=decimal.Decimal(62),
        ),
        split_payment.SplitModel(payment=card, sum_to_pay=decimal.Decimal(23)),
    }
    splitted = split_payment.split_payment(
        amount=amount, payments=[card, wallet],
    )

    assert len(splitted) == 2
    assert set(splitted) == expected_split


def test_part_refund():
    card = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_CARD, method_id=CARD_ID, sum_to_pay='20',
    )
    wallet = split_payment.PaymentMethodModel(
        type=consts.PAYMENT_TYPE_WALLET, method_id=WALLET_ID, held='10',
    )

    expected_split = {
        split_payment.SplitModel(
            payment=wallet, sum_to_pay=decimal.Decimal(0),
        ),
        split_payment.SplitModel(payment=card, sum_to_pay=decimal.Decimal(20)),
    }
    splitted = split_payment.split_payment(
        amount='20', payments=[card, wallet],
    )

    assert len(splitted) == 2
    assert set(splitted) == expected_split
