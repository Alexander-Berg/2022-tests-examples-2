import pytest

from taxi.core import async
from taxi.internal import dbh

from taxiadmin import permissions


class DummyRequest(object):
    def __init__(self, superuser, groups):
        self.groups = groups
        self.superuser = superuser


@pytest.mark.parametrize(
    'superuser,permissions_user,permissions_req,expected_result', [
        (True, {}, ['foo'], dbh.admin_groups.unrestricted_perm()),
        (
            False,
            {'bar': dbh.admin_groups.unrestricted_perm()},
            ['foo'],
            None
        ),
        (
            False,
            {
                'foo': dbh.admin_groups.unrestricted_perm(),
                'bar': dbh.admin_groups.countries_perm(['rus', 'blr'])
            },
            ['foo', 'bar'],
            dbh.admin_groups.unrestricted_perm()
        ),
        (
            False,
            {
                'foo': dbh.admin_groups.countries_perm(['rus']),
                'bar': dbh.admin_groups.countries_perm(['rus', 'blr'])
            },
            ['foo', 'bar'],
            dbh.admin_groups.countries_perm(['rus', 'blr'])
        )
    ]
)
@pytest.inline_callbacks
def test_authorize_request(superuser, permissions_user,
                           permissions_req, expected_result, patch):
    class GroupsObject:
        pass

    @patch('taxi.internal.dbh.admin_groups.Doc.get_groups_permissions')
    @async.inline_callbacks
    def get_groups_permissions(groups):
        assert groups is GroupsObject
        yield
        async.return_value(permissions_user)

    request = DummyRequest(superuser, GroupsObject)
    result = yield permissions.authorize_request(request, permissions_req)
    assert result == expected_result


@pytest.inline_callbacks
def test_authorize_request_permissions_cache(patch):
    @patch('taxi.internal.dbh.admin_groups.Doc.get_groups_permissions')
    @async.inline_callbacks
    def get_groups_permissions(groups):
        yield
        async.return_value({
            'foo': dbh.admin_groups.unrestricted_perm(),
            'bar': dbh.admin_groups.countries_perm(['rus', 'blr'])
        })

    request = DummyRequest(False, ['g1'])
    result = yield permissions.authorize_request(request, ['foo'])
    assert result == dbh.admin_groups.unrestricted_perm()
    assert request.permissions == {
        'foo': dbh.admin_groups.unrestricted_perm(),
        'bar': dbh.admin_groups.countries_perm(['rus', 'blr'])
    }

    result = yield permissions.authorize_request(request, ['bar'])
    assert result == dbh.admin_groups.countries_perm(['rus', 'blr'])
    assert request.permissions == {
        'foo': dbh.admin_groups.unrestricted_perm(),
        'bar': dbh.admin_groups.countries_perm(['rus', 'blr'])
    }

    assert get_groups_permissions.calls == [
        {'args': (['g1'],), 'kwargs': {}},
    ]
