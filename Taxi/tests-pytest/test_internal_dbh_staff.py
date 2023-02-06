from taxi.internal import dbh


def test_normalize_login():
    assert dbh.staff.normalize_login('foo') == 'foo'
    assert dbh.staff.normalize_login('Foo') == 'foo'
    assert dbh.staff.normalize_login(' foo ') == 'foo'
    assert dbh.staff.normalize_login('foo-bar') == 'foo-bar'
    assert dbh.staff.normalize_login('foo.bar') == 'foo-bar'
