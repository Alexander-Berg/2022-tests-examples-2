import pytest


@pytest.fixture(scope='session')
def mongodb_local(mongodb_local_create):
    return mongodb_local_create(['foo'])


def test_mongo_local(mongodb, mongodb_local):
    assert mongodb.get_aliases() == ('foo',)
    assert mongodb_local.get_aliases() == ('foo',)


def test_fixtures_loaded(mongodb):
    assert mongodb.foo.find_one() == {
        '_id': 'foo',
    }
