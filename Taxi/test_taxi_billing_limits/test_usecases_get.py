import typing

import pytest

from taxi_billing_limits import limits
from taxi_billing_limits.usecases import get


async def test_get_nonexisted():
    usecase = get.GetLimitByRefUseCase(repo=GetLimitByRefRepositoryStub())
    with pytest.raises(get.LimitNotFound) as excinfo:
        await usecase(ref='bad')
    assert str(excinfo.value) == 'Limit "bad" not found.'


async def test_get_existed():
    usecase = get.GetLimitByRefUseCase(repo=GetLimitByRefRepositoryStub())
    limit = await usecase(ref='limit_id')
    assert limit == {
        'ref': 'limit_id',
        'currency': 'RUB',
        'label': '',
        'account_id': 'budget/limit_id',
        'tickets': [],
        'approvers': [],
        'tags': [],
        'windows': [],
        'notifications': [],
    }


class GetLimitByRefRepositoryStub(get.GetLimitByRefRepository):
    async def get_limit_by_ref(
            self, *, ref: str,
    ) -> typing.Optional[limits.Limit]:
        if ref == 'limit_id':
            return limits.Limit(
                ref='limit_id',
                currency='RUB',
                label='',
                account_id='budget/limit_id',
            )
        return None
