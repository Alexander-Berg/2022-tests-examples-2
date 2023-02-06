# coding: utf-8

import functools as ft

import pytest

from common import crypto
from yasandbox.database import mapping

import yasandbox.api.json.tests.vault as jsonapi_vault_tests

client_and_task = jsonapi_vault_tests.client_and_task


def _user(user_controller, login, super_user=False):
    user_controller.validated(login)
    user = user_controller.valid(login)
    user.super_user = super_user
    return user


def _group(group_controller, name, users):
    return group_controller.create(mapping.Group(name=name, users=users, email='mail'))


@pytest.fixture()
def super_user(user_controller):
    return _user(user_controller, 'super_user', True)


@pytest.fixture()
def secret_to_dict(vault_controller):
    def wrapped(item, decrypt=False):
        return dict(
            owner=item.owner,
            name=item.name,
            allowed_users=list(item.allowed_users),
            data=vault_controller._Vault__decrypt(item.data) if decrypt else str(item.data),
        )
    return wrapped


class TestVaultController:
    """
    Test some use cases for Vault Controller
    """

    def __update(self, fields, model, **kws):
        fields.update(kws)
        for k, v in kws.iteritems():
            setattr(model, k, v)

    def test__create(self, vault_controller):
        model = mapping.Vault(owner='user1', name='key1', data='secret')
        vault_controller.create(model)
        model = mapping.Vault(owner='user1', name='key1', data='secret')
        pytest.raises(vault_controller.AlreadyExists, vault_controller.create, model)
        model = mapping.Vault(owner='user1', name='key2', data='secret')
        vault_controller.create(model)
        model = mapping.Vault(owner='user2', name='key1', data='secret')
        vault_controller.create(model)

    def test__list(self, vault_controller, secret_to_dict):
        assert not vault_controller.list()
        items = []
        for i in xrange(10):
            for j in xrange(10):
                fields = dict(owner='user' + str(i), name='key' + str(j), data='secret')
                vault_controller.create(mapping.Vault(**fields))
                fields['allowed_users'] = []
                items.append(fields)

        secret_to_dict = ft.partial(secret_to_dict, decrypt=True)
        assert map(secret_to_dict, vault_controller.list()) == items
        for i in xrange(10):
            assert map(secret_to_dict, vault_controller.list('user' + str(i))) == items[i * 10:(i + 1) * 10]

    def test__list_owner_with_group(self, vault_controller, group_controller, user_controller, secret_to_dict):
        users = [_user(user_controller, 'A_USER{}'.format(i)) for i in xrange(10)]
        user_vaults = {}
        for user in users:
            fields = dict(owner=user.login, name='a_user_{}'.format(user.login), data='secret', allowed_users=[])
            vault_controller.create(mapping.Vault(**fields))
            user_vaults[user.login] = [fields]
        for group_id, (left, right) in enumerate([(0, 5), (3, 8), (7, 10)]):
            group = _group(group_controller, 'B_GROUP{}'.format(group_id), [user.login for user in users[left:right]])
            fields = dict(owner=group.name, name='b_group_{}'.format(group_id), data='secret', allowed_users=[])
            vault_controller.create(mapping.Vault(**fields))
            [user_vaults[user.login].append(fields) for user in users[left:right]]

        secret_to_dict = ft.partial(secret_to_dict, decrypt=True)
        for user in users:
            assert map(secret_to_dict, vault_controller.list(user.login)) == user_vaults[user.login]

    def test__get(self, vault_controller, group_controller, user_controller, super_user, secret_to_dict):
        u1, u2, u3, u4, u5 = [_user(user_controller, 'user' + str(i)) for i in xrange(5)]
        g = _group(group_controller, 'GROUP', [u4.login, u5.login])
        name = 'key'
        fields = dict(owner=u1.login, name=name, data='secret', allowed_users=[u2.login, g.name])
        vault_controller.create(mapping.Vault(**fields))
        assert secret_to_dict(vault_controller.get(u1, u1.login, name)) == fields
        assert secret_to_dict(vault_controller.get(u2, u1.login, name)) == fields
        assert secret_to_dict(vault_controller.get(u4, u1.login, name)) == fields
        assert secret_to_dict(vault_controller.get(u5, u1.login, name)) == fields
        assert secret_to_dict(vault_controller.get(super_user, u1.login, name)) == fields
        assert secret_to_dict(vault_controller.get(g, u1.login, name)) == fields
        pytest.raises(vault_controller.NotAllowed, vault_controller.get, u3, u1.login, name)
        pytest.raises(vault_controller.NotExists, vault_controller.get, u1, u1.login, name + '123')
        pytest.raises(vault_controller.NotExists, vault_controller.get, u1, u2.login, name)

    def test__get_by_id(self, vault_controller, group_controller, user_controller, super_user, secret_to_dict):
        u1, u2, u3, u4, u5 = [_user(user_controller, 'user' + str(i)) for i in xrange(5)]
        g = _group(group_controller, 'GROUP', [u4.login, u5.login])
        items = []
        for i in xrange(10):
            fields = dict(owner=u1.login, name='key' + str(i), allowed_users=[u2.login, g.name], data='secret')
            items.append((vault_controller.create(mapping.Vault(**fields)).id, fields))
        for item_id, fields in items:
            assert secret_to_dict(vault_controller.get_by_id(u1, item_id)) == fields
            assert secret_to_dict(vault_controller.get_by_id(u2, item_id)) == fields
            assert secret_to_dict(vault_controller.get_by_id(u4, item_id)) == fields
            assert secret_to_dict(vault_controller.get_by_id(u5, item_id)) == fields
            assert secret_to_dict(vault_controller.get_by_id(super_user, item_id)) == fields
            assert secret_to_dict(vault_controller.get_by_id(g, item_id)) == fields
            pytest.raises(vault_controller.NotAllowed, vault_controller.get_by_id, u3, item_id)

    def test__update(self, vault_controller, user_controller, group_controller, super_user, secret_to_dict):
        u1, u2, u3 = [_user(user_controller, 'user' + str(i)) for i in xrange(3)]
        g = _group(group_controller, 'GROUP', [u1.login])
        fields = dict(owner=u1.login, name='key', allowed_users=[], data='secret')
        model = vault_controller.create(mapping.Vault(**fields))

        self.__update(fields, model, name='newkey', allowed_users=[u2.login, g.name], data='newsecret')
        vault_controller.update(u1, model)
        assert secret_to_dict(vault_controller.get_by_id(u1, model.id)) == fields

        assert secret_to_dict(vault_controller.get_by_id(g, model.id)) == fields

        self.__update(fields, model, name='newkey1')
        vault_controller.update(u1, model, encrypt=False)
        assert secret_to_dict(vault_controller.get_by_id(u1, model.id)) == fields

        self.__update(fields, model, name='newkey2')
        vault_controller.update(super_user, model, encrypt=False)
        assert secret_to_dict(vault_controller.get_by_id(u1, model.id)) == fields

        self.__update(fields, model, name='')
        pytest.raises(vault_controller.InvalidFields, vault_controller.update, u1, model)

        self.__update(fields, model, name='newkey')
        pytest.raises(vault_controller.NotAllowed, vault_controller.update, u2, model)
        pytest.raises(vault_controller.NotAllowed, vault_controller.update, u3, model)

    def test__delete(self, vault_controller, user_controller, group_controller, super_user, secret_to_dict):
        u1, u2, u3 = [_user(user_controller, 'user' + str(i)) for i in xrange(3)]
        fields = dict(owner=u1.login, name='key', allowed_users=[u2.login], data='secret')
        model = vault_controller.create(mapping.Vault(**fields))
        pytest.raises(vault_controller.NotAllowed, vault_controller.delete, u2, model)
        pytest.raises(vault_controller.NotAllowed, vault_controller.delete, u3, model)
        assert secret_to_dict(vault_controller.get_by_id(u1, model.id)) == fields

        vault_controller.delete(u1, model)
        pytest.raises(vault_controller.NotExists, vault_controller.get_by_id, u1, model.id)
        model = vault_controller.create(mapping.Vault(**fields))
        vault_controller.delete(super_user, model)
        pytest.raises(vault_controller.NotExists, vault_controller.get_by_id, u1, model.id)

        g = _group(group_controller, 'GROUP', [u1.login])
        fields = dict(owner=g.name, name='key', allowed_users=[u2.login], data='secret')
        model = vault_controller.create(mapping.Vault(**fields))
        vault_controller.delete(g, model)
        pytest.raises(vault_controller.NotExists, vault_controller.get_by_id, g, model.id)

    def test__get_encrypted_data(self, vault_controller, user_controller, client_and_task):
        user = _user(user_controller, 'user')
        name = 'key'
        data = 'topsecret'

        fields = dict(owner=user.login, name=name, data=data)
        vault = vault_controller.create(mapping.Vault(**fields))
        _, task = client_and_task
        task.author = user.login
        task.owner = user.login
        task.save()
        pytest.raises(
            vault_controller.EncryptionKeyNotDefined,
            vault_controller.encrypt_data,
            vault, task, None
        )
        cipher = crypto.AES()
        encrypted_data = vault_controller.encrypt_data(vault, task, cipher.key)
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == data

    def test__get_encrypted_data_by_group(self, vault_controller, user_controller, group_controller, client_and_task):
        user = _user(user_controller, 'user')
        group = _group(group_controller, 'GROUP', [user.login])
        name = 'key'
        data = 'topsecret'
        fields = dict(owner=group.name, name=name, data=data)
        vault = vault_controller.create(mapping.Vault(**fields))
        _, task = client_and_task
        task.author = user.login
        task.owner = group.name
        task.save()
        cipher = crypto.AES()
        encrypted_data = vault_controller.encrypt_data(vault, task, cipher.key)
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == data
