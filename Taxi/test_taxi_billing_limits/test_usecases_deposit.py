# pylint: disable=redefined-outer-name
import datetime
import decimal
from unittest import mock

import pytest

from taxi_billing_limits import limits
from taxi_billing_limits import payments
from taxi_billing_limits.usecases import deposit


@pytest.fixture
def payment():
    return payments.Payment(
        currency='RUB',
        amount=decimal.Decimal(100),
        payment_ref='deadbeef',
        event_at=datetime.datetime(2019, 11, 10, 12, 30),
        limit_ref='limit_id',
        use_dry=False,
    )


async def test_deposit_success(payment):
    repo = LimitsRepositoryStub()
    doc = mock.Mock(spec=limits.PaymentDoc)
    accountant = DepositaryStub(doc=doc)
    checker = CheckSchedulerStub()

    usecase = deposit.DepositPaymentUseCase(
        repo=repo, depositary=accountant, checker=checker,
    )
    await usecase(payment)

    assert accountant.calls == [dict(limit=repo.limit, payment=payment)]
    assert checker.calls == [dict(limit=repo.limit, doc=doc)]


async def test_deposit_limit_not_found(payment):
    class LimitNotFoundRepository(deposit.PaymentLimitsRepository):
        async def get_limit_for_payment(self, *, payment):
            del payment  # not used
            return None

    repo = LimitNotFoundRepository()
    accountant = DepositaryStub()
    checker = CheckSchedulerStub()

    usecase = deposit.DepositPaymentUseCase(
        repo=repo, depositary=accountant, checker=checker,
    )
    with pytest.raises(deposit.LimitNotFound) as excinfo:
        await usecase(payment)

    assert str(excinfo.value) == 'Limit "limit_id" not found.'
    assert accountant.calls == []
    assert checker.calls == []


async def test_deposit_invalid_currency(payment):
    msg = 'Payment currency "RUB" does not match limit currency "USD".'
    repo = LimitsRepositoryStub(currency='USD')
    accountant = DepositaryStub()
    checker = CheckSchedulerStub()

    usecase = deposit.DepositPaymentUseCase(
        repo=repo, depositary=accountant, checker=checker,
    )
    with pytest.raises(deposit.PaymentInvalid) as excinfo:
        await usecase(payment)
    assert str(excinfo.value) == msg
    assert accountant.calls == []
    assert checker.calls == []


class LimitsRepositoryStub(deposit.PaymentLimitsRepository):
    def __init__(self, currency='RUB'):
        self.limit = limits.Limit(
            ref='limit',
            currency=currency,
            label='label',
            account_id='budget/limit',
            tickets=[],
        )

    async def get_limit_for_payment(self, *, payment):
        del payment  # not used
        return self.limit


class DepositaryStub(deposit.Depositary):
    def __init__(self, doc=None):
        self.calls = []
        self.doc = doc or mock.Mock()

    async def deposit(self, *, limit, payment):
        self.calls.append({'limit': limit, 'payment': payment})
        return self.doc


class CheckSchedulerStub(deposit.CheckScheduler):
    def __init__(self):
        self.calls = []

    async def schedule_check(
            self, *, limit: limits.Limit, doc: limits.PaymentDoc,
    ):
        self.calls.append({'limit': limit, 'doc': doc})
