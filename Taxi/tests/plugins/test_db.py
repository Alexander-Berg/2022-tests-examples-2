import pytest


@pytest.fixture(scope='session')
def mongodb_local(mongodb_local_create):
    return mongodb_local_create(['foo'])


def test_db_simple(db):
    assert db.foo.find_one('unknown') is None
    assert db.foo.find_one('one') == {'_id': 'one', 'source': 'db_foo.json'}


@pytest.mark.filldb(foo='own_fixture')
def test_db_own_fixture(db):
    assert db.foo.find_one('unknown') is None
    assert db.foo.find_one('one') == {
        '_id': 'one', 'source': 'db_foo_own_fixture.json',
    }
