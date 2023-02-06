# coding: utf-8
from __future__ import unicode_literals, absolute_import

import pytest
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from sandbox.step.django_idm_api.hooks import BaseHooks
from sandbox.step.django_idm_api.tests.utils import refresh, create_group

pytestmark = pytest.mark.django_db


@pytest.mark.xfail(run=False)
def test_deprive_superuser_role(client, frodo):
    url = reverse('client-api:remove-role')

    frodo.is_superuser = True
    frodo.is_staff = True
    frodo.save()

    response = client.json.post(url, {
        'login': 'frodo',
        'role': {
            'role': 'superuser'
        }
    })
    assert response.status_code == 200
    assert response.json() == {
        'code': 0
    }

    frodo = refresh(frodo)
    assert frodo.is_superuser is False
    assert frodo.is_staff is False


@pytest.mark.xfail(run=False)
def test_deprive_usual_role(client, frodo):
    url = reverse('client-api:remove-role')

    group = create_group('Менеджеры')
    frodo.groups.add(group)
    frodo.is_staff = True
    frodo.save()

    response = client.json.post(url, {
        'login': 'frodo',
        'role': {
            'role': 'group-%d' % group.pk
        }
    })
    assert response.status_code == 200
    assert response.json() == {'code': 0}
    frodo = refresh(frodo)
    assert frodo.groups.count() == 0
    assert frodo.is_staff is False


@pytest.mark.xfail(run=False)
def test_deprive_unknown_role_returns_success(client):
    url = reverse('client-api:remove-role')
    response = client.json.post(url, {
        'login': 'unknown-login',
        'role': {
            'bad': 'role'
        }
    })
    assert response.status_code == 200
    assert response.json() == {'code': 0}


@pytest.mark.xfail(run=False)
def test_deprive_role_bad_req(client):
    url = reverse('client-api:remove-role')

    # bad json request
    response = client.json.post(url, {
        'login': 'unknown-login',
        'role': 'gibberish'
    })
    assert response.status_code == 200
    assert response.json() == {
        'code': 400,
        'fatal': 'incorrect json data in field `role`: gibberish'
    }

    # null role request - возвращает ОК, т.к. мы не говорим, если такой роли не было
    response = client.json.post(url, {
        'login': 'unknown-login',
        'role': {
            'role': None
        }
    })
    assert response.status_code == 200
    assert response.json() == {'code': 0}


@pytest.mark.xfail(run=False)
def test_is_staff_remains_if_other_roles(client, frodo):
    """Проверим, что is_staff остаётся, если у пользователя есть хотя бы одна роль"""
    url = reverse('client-api:remove-role')

    group = create_group('Менеджер')
    group2 = create_group('Админ')
    frodo.groups.add(group)
    frodo.groups.add(group2)
    frodo.is_staff = True
    frodo.save()

    response = client.json.post(url, {
        'login': 'frodo',
        'role': {
            'role': 'group-%d' % group.pk
        }
    })
    assert response.status_code == 200
    assert response.json() == {'code': 0}
    frodo = refresh(frodo)
    assert frodo.groups.count() == 1
    assert frodo.groups.get() == group2
    assert frodo.is_staff is True


@pytest.mark.xfail(run=False)
def test_is_staff_remains_if_still_superuser(client, frodo):
    """Проверим, что is_staff остаётся, если пользователь - суперюзер"""
    url = reverse('client-api:remove-role')

    group = create_group('Менеджер')
    frodo.groups.add(group)
    frodo.is_superuser = True
    frodo.is_staff = True
    frodo.save()

    response = client.json.post(url, {
        'login': 'frodo',
        'role': {
            'role': 'group-%d' % group.pk
        }
    })
    assert response.status_code == 200
    assert response.json() == {'code': 0}

    frodo = refresh(frodo)
    assert frodo.groups.count() == 0
    assert frodo.is_superuser is True
    assert frodo.is_staff is True


@pytest.mark.xfail(run=False)
def test_deprive_group_role_if_system_is_aware(client):
    """Если включена соответствующая настройка, то система сама следит за составом групп.
    Мы (пока?) не предоставляем готового механизма для отслеживания состава групп, так что хуки тоже
    будут переопределены"""

    url = reverse('client-api:remove-role')

    class CustomHooks(BaseHooks):
        role_is_removed = None

        def remove_group_role_impl(self, group, role, data, is_deleted, **kwargs):
            CustomHooks.role_is_removed = True
            CustomHooks.group = group
            CustomHooks.role = role
            CustomHooks.data = data
            CustomHooks.is_deleted = is_deleted
            return self._successful_result

    with override_settings(ROLES_HOOKS=CustomHooks, ROLES_SYSTEM_IS_GROUP_AWARE=True):
        response = client.json.post(url, {
            'group': 13,
            'role': {
                'role': 'superuser'
            },
            'data': {
                'token': 'mellon'
            }
        })
        assert response.status_code == 200
        assert response.json() == {'code': 0}
        assert CustomHooks.group == 13
        assert CustomHooks.role == {'role': 'superuser'}
        assert CustomHooks.data == {'token': 'mellon'}
        assert CustomHooks.is_deleted is False
