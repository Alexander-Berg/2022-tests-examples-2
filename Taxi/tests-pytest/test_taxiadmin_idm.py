from __future__ import unicode_literals

import pytest

from taxi.internal import dbh
from taxiadmin import idm


@pytest.mark.asyncenv('blocking')
def test_get_all_roles_impl():
    hook = idm.TaxiAdminHooks()
    roles = hook.get_all_roles_impl()
    assert sorted(roles) == [
        ('user-dotted', []),
        ('user_0', []),
        ('user_1', [{'role': 'superuser'}]),
        ('user_2', [{'role': 'cabinet'}]),
        ('user_3', [{'role': 'group-foo'}, {'role': 'group-bar'}]),
        ('user_4', [{'role': 'group-baz'}, {'role': 'group-qux'}]),
    ]


@pytest.mark.asyncenv('blocking')
def test_info_impl():
    hook = idm.TaxiAdminHooks()
    info = hook.info_impl()
    assert info == {
        'cabinet': 'cabinet',
        'superuser': 'superuser',
        'group-foo': 'Foo group',
        'group-bar': 'Bar group',
    }


@pytest.mark.asyncenv('blocking')
def test_create_new_user():
    hook = idm.TaxiAdminHooks()
    hook.add_role_impl('brandnew', {'role': 'superuser'}, {})
    user = dbh.staff.Doc.find_one_by_yandex_team_login('brandnew')

    assert user.admin_superuser
    assert not user.access_to_cabinet
    assert not user.admin_groups
    assert user.yandex_team_login == 'brandnew'


@pytest.mark.asyncenv('blocking')
def test_role_remove_add():
    hook = idm.TaxiAdminHooks()

    # Add superuser
    hook.add_role_impl('user_0', {'role': 'superuser'}, {})
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user_0')
    assert user.admin_superuser
    assert not user.access_to_cabinet
    assert not user.admin_groups

    # Remove superuser
    hook.remove_role_impl('user_0', {'role': 'superuser'}, None, False)
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user_0')
    assert not user.admin_superuser
    assert not user.access_to_cabinet
    assert not user.admin_groups

    # Add cabinet
    hook.add_role_impl('user_0', {'role': 'cabinet'}, {})
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user_0')
    assert not user.admin_superuser
    assert user.access_to_cabinet
    assert not user.admin_groups

    # Remove cabinet
    hook.remove_role_impl('user_0', {'role': 'cabinet'}, None, False)
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user_0')
    assert not user.admin_superuser
    assert not user.access_to_cabinet
    assert not user.admin_groups

    # Add group-foo
    hook.add_role_impl('user_0', {'role': 'group-foo'}, {})
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user_0')
    assert not user.admin_superuser
    assert not user.access_to_cabinet
    assert user.admin_groups == ['foo']

    # Remove group-foo
    hook.remove_role_impl('user_0', {'role': 'group-foo'}, None, False)
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user_0')
    assert not user.admin_superuser
    assert not user.access_to_cabinet
    assert not user.admin_groups

    # Add superuser
    hook.add_role_impl('user-dotted', {'role': 'superuser'}, {})
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user-dotted')
    assert user.admin_superuser
    assert not user.access_to_cabinet
    assert not user.admin_groups

    # Remove superuser
    hook.remove_role_impl('user.dotted', {'role': 'superuser'}, None, False)
    user = dbh.staff.Doc.find_one_by_yandex_team_login('user-dotted')
    assert not user.admin_superuser
    assert not user.access_to_cabinet
    assert not user.admin_groups
