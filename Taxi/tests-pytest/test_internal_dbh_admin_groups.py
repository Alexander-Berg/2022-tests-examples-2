import pytest

from taxi.internal import dbh


@pytest.inline_callbacks
def test_get_groups_permissions():
    permissions = yield dbh.admin_groups.Doc.get_groups_permissions(['foo'])
    assert permissions == {
        'p1': dbh.admin_groups.unrestricted_perm(),
        'p2': dbh.admin_groups.unrestricted_perm()
    }

    permissions = yield dbh.admin_groups.Doc.get_groups_permissions(['bar'])
    assert permissions == {
        'p2': dbh.admin_groups.unrestricted_perm(),
        'p3': dbh.admin_groups.unrestricted_perm()
    }

    permissions = yield dbh.admin_groups.Doc.get_groups_permissions(
        ['foo', 'bar']
    )
    assert permissions == {
        'p1': dbh.admin_groups.unrestricted_perm(),
        'p2': dbh.admin_groups.unrestricted_perm(),
        'p3': dbh.admin_groups.unrestricted_perm(),
    }

    permissions = yield dbh.admin_groups.Doc.get_groups_permissions(
        ['bar', 'baz']
    )
    assert permissions == {
        'p2': dbh.admin_groups.unrestricted_perm(),
        'p3': dbh.admin_groups.unrestricted_perm(),
    }

    permissions = yield dbh.admin_groups.Doc.get_groups_permissions(
        ['baz', 'qux']
    )
    assert permissions == {
        'p2': dbh.admin_groups.unrestricted_perm(),
        'p3': dbh.admin_groups.countries_perm(['rus', 'blr']),
    }

    permissions = yield dbh.admin_groups.Doc.get_groups_permissions([])
    assert permissions == {}

    permissions = yield dbh.admin_groups.Doc.get_groups_permissions(['unknown'])
    assert permissions == {}
