import datetime
import decimal
from unittest import mock

import pytest

from taxi_billing_limits import limits
from taxi_billing_limits.usecases import check

_TUMBLING = limits.TumblingWindow(
    pkey=1,
    size=604800,
    value=decimal.Decimal(1000),
    threshold=110,
    label='Tumbling',
    start=datetime.datetime.fromisoformat('2019-11-10T21:00:00+00:00'),
)

_TUMBLING_DAILY = limits.TumblingWindow(
    pkey=2,
    size=86400,
    value=decimal.Decimal(100),
    threshold=120,
    label='Tumbling daily',
    start=datetime.datetime.fromisoformat('2019-11-10T21:00:00+00:00'),
)

_SLIDING = limits.SlidingWindow(
    pkey=3,
    size=604800,
    value=decimal.Decimal(1000),
    threshold=105,
    label='Sliding',
)

_SLIDING_DAILY = limits.SlidingWindow(
    pkey=4,
    size=86400,
    value=decimal.Decimal(100),
    threshold=130,
    label='Sliding daily',
)


@pytest.mark.now('2019-11-20T18:00:00+00:00')
async def test_check_limit_not_found():
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    repo = GetLimitByRefRepositoryStub(limit=None)
    accountant = AccountantStub()
    notifier = NotifySchedulerStub()
    tracer = mock.Mock(spec=check.CheckLimitTracer)
    usecase = check.CheckLimitUseCase(
        repo=repo,
        windows_repo=GetWindowLastNotifiedRepositoryStub(),
        accountant=accountant,
        notifier_selector=NotifierSelector(notifier),
        tracer=tracer,
    )
    await usecase(ref='limit_id', now=now)
    assert not accountant.called
    assert not notifier.called
    tracer.limit_not_found.assert_called_once()


@pytest.mark.now('2019-11-20T18:00:00+00:00')
@pytest.mark.parametrize(
    'window,since_expected',
    (
        (_TUMBLING, '2019-11-17T21:00:00+00:00'),
        (_TUMBLING_DAILY, '2019-11-19T21:00:00+00:00'),
        (_SLIDING, '2019-11-13T18:00:00+00:00'),
        (_SLIDING_DAILY, '2019-11-19T18:00:00+00:00'),
    ),
)
async def test_check_limit_ok(window, since_expected):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    balance = decimal.Decimal(
        0.99 * (window.threshold / 100) * float(window.value),
    )
    limit = limits.Limit(
        ref='limit_id',
        currency='RUB',
        label='',
        account_id='budget/limit_id',
        windows=[window],
    )
    repo = GetLimitByRefRepositoryStub(limit=limit)
    accountant = AccountantStub(balance)
    notifier = NotifySchedulerStub()
    tracer = mock.Mock(spec=check.CheckLimitTracer)

    usecase = check.CheckLimitUseCase(
        repo=repo,
        windows_repo=GetWindowLastNotifiedRepositoryStub(),
        accountant=accountant,
        notifier_selector=NotifierSelector(notifier),
        tracer=tracer,
    )
    await usecase(ref='limit_id', now=now)

    assert accountant.called == [
        {
            'limit': limit,
            'since': datetime.datetime.fromisoformat(since_expected),
            'till': now,
        },
    ]
    assert not notifier.called


@pytest.mark.now('2019-11-20T18:00:00+00:00')
@pytest.mark.parametrize(
    'window,since_expected',
    (
        (_TUMBLING, '2019-11-17T21:00:00+00:00'),
        (_TUMBLING_DAILY, '2019-11-19T21:00:00+00:00'),
        (_SLIDING, '2019-11-13T18:00:00+00:00'),
        (_SLIDING_DAILY, '2019-11-19T18:00:00+00:00'),
    ),
)
async def test_check_limit_exhausted(window, since_expected):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    balance = decimal.Decimal(
        1.1 * (window.threshold / 100) * float(window.value),
    )
    limit = limits.Limit(
        ref='limit_id',
        currency='RUB',
        label='',
        account_id='budget/limit_id',
        windows=[window],
    )
    repo = GetLimitByRefRepositoryStub(limit=limit)
    accountant = AccountantStub(balance)
    notifier = NotifySchedulerStub()
    tracer = mock.Mock(spec=check.CheckLimitTracer)

    usecase = check.CheckLimitUseCase(
        repo=repo,
        windows_repo=GetWindowLastNotifiedRepositoryStub(),
        accountant=accountant,
        notifier_selector=NotifierSelector(notifier),
        tracer=tracer,
    )
    await usecase(ref='limit_id', now=now)

    assert accountant.called == [
        {
            'limit': limit,
            'since': datetime.datetime.fromisoformat(since_expected),
            'till': now,
        },
    ]
    assert notifier.called == [
        {'limit': limit, 'window': window, 'balance': balance, 'now': now},
    ]
    tracer.exhaustion_already_notified.not_called()


@pytest.mark.now('2019-11-20T18:00:00+00:00')
async def test_check_limit_already_notified():
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    balance = decimal.Decimal(200)
    limit = limits.Limit(
        ref='limit_id',
        currency='RUB',
        label='',
        account_id='budget/limit_id',
        windows=[_TUMBLING_DAILY],
    )
    repo = GetLimitByRefRepositoryStub(limit=limit)
    accountant = AccountantStub(balance)
    notifier = NotifySchedulerStub()
    tracer = mock.Mock(spec=check.CheckLimitTracer)

    usecase = check.CheckLimitUseCase(
        repo=repo,
        windows_repo=GetWindowLastNotifiedRepositoryStub(
            notified=_TUMBLING_DAILY.notify_interval_id(now),
        ),
        accountant=accountant,
        notifier_selector=NotifierSelector(notifier),
        tracer=tracer,
    )
    await usecase(ref='limit_id', now=now)
    assert accountant.called == []
    assert notifier.called == []
    tracer.exhaustion_already_notified.assert_called_once()
    tracer.balance_checked.not_called()


@pytest.mark.now('2019-11-20T18:00:00+00:00')
async def test_broken_notify_scheduler():
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    limit = limits.Limit(
        ref='limit_id',
        currency='RUB',
        label='',
        account_id='budget/limit_id',
        windows=[_TUMBLING_DAILY],
    )
    repo = GetLimitByRefRepositoryStub(limit=limit)
    accountant = AccountantStub(decimal.Decimal(200))
    notifier = BrokenNotifySchedulerStub()
    tracer = mock.Mock(spec=check.CheckLimitTracer)
    windows_repo = GetWindowLastNotifiedRepositoryStub()

    usecase = check.CheckLimitUseCase(
        repo=repo,
        windows_repo=windows_repo,
        accountant=accountant,
        notifier_selector=NotifierSelector(notifier),
        tracer=tracer,
    )
    with pytest.raises(Exception) as excinfo:
        await usecase(ref='limit_id', now=now)
    assert str(excinfo.value) == 'Oops, not available now'
    assert windows_repo.notified == 0


class GetLimitByRefRepositoryStub(check.GetLimitWithWindowsByRefRepository):
    def __init__(self, *, limit):
        self.limit = limit

    async def get_limit_with_windows_by_ref(self, *, ref):
        del ref  # unused
        return self.limit


class GetWindowLastNotifiedRepositoryStub(
        check.GetWindowLastNotifiedRepository,
):
    def __init__(self, notified=None):
        self.notified = notified or 0

    async def get_window_last_notified(self, *, window_pk: int) -> int:
        return self.notified or 0

    async def set_window_last_notified(
            self, *, window_pk: int, last_notified: int,
    ) -> bool:
        self.notified = last_notified
        return True


class AccountantStub(check.Accountant):
    def __init__(self, balance=decimal.Decimal()):
        self.called = []
        self.balance = balance

    async def get_balance_for_period(self, *, limit, since, till):
        self.called.append({'limit': limit, 'since': since, 'till': till})
        return self.balance


class NotifierSelector(check.NotifierSelector):
    def __init__(self, notifier):
        self._notifier = notifier

    def get_notifier(self, notifications):
        return self._notifier


class NotifySchedulerStub(check.NotifyScheduler):
    def __init__(self):
        self.called = []

    async def schedule_notify(self, *, limit, window, balance, now):
        self.called.append(
            {'limit': limit, 'window': window, 'balance': balance, 'now': now},
        )


class BrokenNotifySchedulerStub(check.NotifyScheduler):
    async def schedule_notify(self, *, limit, window, balance, now):
        raise Exception('Oops, not available now')
