from taxi_billing_limits import limits
from taxi_billing_limits.usecases import create


async def test_create_success():
    data = dict(ref='limit_id', currency='RUB', label='spb')
    repo = CreateLimitRepositoryStub()
    refgen = RefGeneratorStub()
    usecase = create.CreateLimitUseCase(repo=repo, refgen=refgen)
    response = await usecase(data=data)
    assert response == {
        'ref': 'limit_id',
        'currency': 'RUB',
        'label': 'spb',
        'account_id': 'budget/limit_id',
        'approvers': [],
        'tickets': [],
        'tags': [],
        'windows': [],
        'notifications': [],
    }
    assert not refgen.called
    assert repo.called == [data]


async def test_create_without_ref_success():
    data = dict(currency='EUR', label='test', approvers=['me'])
    repo = CreateLimitRepositoryStub()
    refgen = RefGeneratorStub()
    usecase = create.CreateLimitUseCase(repo=repo, refgen=refgen)
    response = await usecase(data=data)
    assert response == {
        'ref': 'new_ref',
        'currency': 'EUR',
        'label': 'test',
        'account_id': 'budget/new_ref',
        'approvers': ['me'],
        'tickets': [],
        'tags': [],
        'windows': [],
        'notifications': [],
    }
    assert refgen.called == [data]
    assert repo.called == [{'ref': 'new_ref', **data}]


class CreateLimitRepositoryStub(create.CreateLimitRepository):
    def __init__(self):
        self.called = []

    async def create(self, *, data: dict) -> limits.Limit:
        self.called = [data]
        return limits.Limit(**data)


class RefGeneratorStub(create.RefGenerator):
    def __init__(self):
        self.called = []

    def __call__(self, *, data) -> str:
        self.called.append(data)
        return 'new_ref'
