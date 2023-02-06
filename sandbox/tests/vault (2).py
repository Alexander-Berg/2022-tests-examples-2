import uuid
import json
import base64
import httplib

import pytest
import requests

import common.rest
import common.proxy
import common.crypto
import common.types.misc as ctm
import common.types.user as ctu


import yasandbox.manager
import yasandbox.manager.tests
import yasandbox.database.mapping
import yasandbox.controller


@pytest.fixture()
def client_and_task(server, client_manager, task_manager):
    client = client_manager.create('test_client')
    task = task_manager.create('TEST_TASK', 'unknown_user', 'unknown_user')
    task.host = client.hostname
    task.save()
    return client, task


@pytest.fixture()
def another_user():
    login = 'another_user'
    from yasandbox.controller import user as user_controller
    user = user_controller.User.get(login)
    if not user:
        user = user_controller.User.create(yasandbox.database.mapping.User(
            login=login
        ))
        user_controller.User.validated(user.login)
    return user


@pytest.fixture()
def requests_timeout(monkeypatch):

    class TimeoutSession(requests.sessions.Session):
        def request(self, *args, **kwargs):
            kwargs["timeout"] = 10
            return super(TimeoutSession, self).request(*args, **kwargs)

    monkeypatch.setattr(requests.sessions, "Session", TimeoutSession)
    monkeypatch.setattr(requests, "Session", TimeoutSession)


@pytest.mark.usefixtures("requests_timeout")
class TestRESTAPIVault(object):
    def test__vault_create(self, json_api_url, gui_session, gui_session_login, vault_controller):
        json_api_url = json_api_url + '/vault'
        headers = {'content-type': 'application/json'}
        vault_data = {'owner': gui_session_login, 'name': 'test-vault', 'data': 'DATA'}
        resp = requests.post(
            json_api_url, data=json.dumps(vault_data), headers=headers)
        assert resp.status_code == requests.codes.UNAUTHORIZED

        headers.update(gui_session)
        vault_data['owner'] = gui_session_login + '-broken'
        resp = requests.post(
            json_api_url, data=json.dumps(vault_data), headers=headers)
        assert resp.status_code == requests.codes.FORBIDDEN

        resp = requests.post(
            json_api_url, data=json.dumps({}), headers=headers)
        assert resp.status_code == requests.codes.BAD_REQUEST

        vault_data['owner'] = gui_session_login
        resp = requests.post(
            json_api_url, data=json.dumps(vault_data), headers=headers)
        assert resp.status_code == requests.codes.CREATED
        ret = resp.json()
        assert ret['rights'] == ctu.Rights.WRITE
        assert ret['owner'] == gui_session_login

    def test__vault_get(
        self, json_api_url, gui_session, gui_session_login, gui_su_session, gui_su_session_login, vault_controller
    ):
        json_api_url = json_api_url + '/vault'
        vault_data = {'owner': gui_su_session_login, 'name': 'test-vault', 'data': 'DATA'}
        headers = {'content-type': 'application/json'}
        headers.update(gui_su_session)
        resp = requests.post(json_api_url, data=json.dumps(vault_data), headers=headers)
        location = resp.headers.get('location')
        vault = requests.get(location, headers=headers).json()
        assert vault['name'] == vault_data['name']
        assert vault['owner'] == gui_su_session_login

        headers.update(gui_session)
        resp = requests.get(location, headers=headers)
        assert resp.status_code == requests.codes.FORBIDDEN

        vault_data['owner'] = gui_session_login
        resp = requests.post(json_api_url, data=json.dumps(vault_data), headers=headers)
        assert resp.status_code == requests.codes.CREATED
        users_vault = requests.get(resp.headers.get('location'), headers=headers).json()
        users_vault.pop("data_length")

        vaults = requests.get('{}?limit=10'.format(json_api_url), headers=headers).json()
        assert vaults['limit'] == 10
        assert vaults['total'] == len(vaults['items']) == 2
        assert users_vault in vaults['items']

        headers.update(gui_su_session)
        vaults = requests.get('{}?limit=10'.format(json_api_url), headers=headers).json()
        assert vaults['total'] == len(vaults['items']) == 2
        assert set(vault['owner'] for vault in vaults['items']) == {gui_su_session_login, gui_session_login}

    def test__vault_update(
        self, json_api_url, gui_session, gui_session_login, group_controller, task_manager, vault_controller
    ):
        data = 'DATA'
        name = 'test-vault'
        updated_name = 'another-test-vault'
        gui_user = yasandbox.controller.User.get(gui_session_login)

        json_api_url = json_api_url + '/vault'
        vault_data = {'owner': gui_session_login, 'name': name, 'data': data}
        headers = {'content-type': 'application/json'}
        headers.update(gui_session)
        resp = requests.post('{}'.format(json_api_url), data=json.dumps(vault_data), headers=headers)
        location = resp.headers.get('location')
        vault = requests.get(location, headers=headers).json()
        assert vault['name'] == vault_data['name']
        assert vault['owner'] == vault_data['owner']
        assert vault['data_length'] == len(vault_data['data'])

        extracted = vault_controller.get(gui_user, gui_session_login, name)
        assert extracted.data == data

        vault_update = {'name': updated_name, 'data': ''}  # GUI sends empty data if there was no update
        resp = requests.put(location, data=json.dumps(vault_update), headers=headers)
        assert resp.status_code == requests.codes.NO_CONTENT

        extracted = vault_controller.get(gui_user, gui_session_login, updated_name)
        assert extracted.data == data

        vault = requests.get(location, headers=headers).json()
        assert vault['name'] == vault_update['name']
        assert vault['owner'] == vault_data['owner']
        assert vault['data_length'] == len(vault_data['data'])

        group_controller.create(yasandbox.database.mapping.Group(name='TGROUP', users=[gui_session_login]))

        vault_update = {'owner': 'TGROUP'}
        headers.update({ctm.HTTPHeader.WANT_UPDATED_DATA: '1'})
        resp = requests.put(location, data=json.dumps(vault_update), headers=headers)
        assert resp.status_code == requests.codes.OK

        vault = resp.json()
        assert vault['owner'] == vault_update['owner']

    def test__vault_delete(self, json_api_url, gui_session, gui_session_login, vault_controller):
        json_api_url = json_api_url + '/vault'
        vault_data = {'owner': gui_session_login, 'name': 'test-vault', 'data': 'DATA'}
        headers = {'content-type': 'application/json'}
        headers.update(gui_session)
        resp = requests.post(json_api_url, data=json.dumps(vault_data), headers=headers)
        location = resp.headers.get('location')
        all_vaults = requests.get('{}?limit=10'.format(json_api_url), headers=headers).json()
        assert all_vaults['total'] == len(all_vaults['items'])

        resp = requests.delete(location, headers=headers)
        assert resp.status_code == requests.codes.NO_CONTENT

        all_vaults = requests.get('{}?limit=10'.format(json_api_url), headers=headers).json()
        assert all_vaults['total'] == len(all_vaults['items']) == 0

    def test__vault_list(
            self,
            json_api_url, gui_session, rest_su_session, rest_session, rest_session_login,
            vault_controller, task_manager
    ):
        ret = rest_su_session.vault[:10]
        assert ret["total"] == 0 and len(ret["items"]) == 0 and ret["limit"] == 10, ret

        vaults = [
            vault_controller.create(yasandbox.database.mapping.Vault(
                owner="vasya",
                name="key",
                data="topsecret123456789"
            )),
            vault_controller.create(yasandbox.database.mapping.Vault(
                owner="petya",
                name="key",
                data="topsecret0987",
                allowed_users=["masha"],
            )),
            vault_controller.create(yasandbox.database.mapping.Vault(
                owner="masha",
                name="yek",
                data="topsecret",
                allowed_users=["vasya", "petya", rest_session_login]
            )),
            vault_controller.create(yasandbox.database.mapping.Vault(
                owner=rest_session_login,
                name="yek",
                data="topsecret",
                allowed_users=["vasya", "petya"]
            )),
        ]
        [_.save() for _ in vaults]

        for rest in (rest_su_session, rest_session):
            ret = rest.vault[:10]
            assert ret["total"] == 4 and ret["limit"] == 10, ret
            ret = ret["items"]
            for i, v in enumerate(vaults):
                rights = None
                if rest == rest_su_session:
                    rights = ctu.Rights.WRITE
                else:
                    if v.owner == rest_session_login:
                        rights = ctu.Rights.WRITE
                    elif rest_session_login in v.allowed_users:
                        rights = ctu.Rights.READ
                assert (
                    ret[i]["rights"] == rights and
                    ret[i]["owner"] == v.owner and ret[i]["name"] == v.name
                ), ret[i]

        headers = {'content-type': 'application/json'}
        headers.update(gui_session)
        ret = requests.get('{}/vault?limit=10'.format(json_api_url), headers=headers).json()
        assert ret["total"] == 4 and len(ret["items"]) == 4 and ret["limit"] == 10, ret
        for item in ret["items"]:
            assert item["rights"] is None, item

        # Filters check
        ret = rest_su_session.vault.read(name="upyaka", limit=10)
        assert ret["total"] == 0 and len(ret["items"]) == 0 and ret["limit"] == 10, ret

        ret = rest_su_session.vault.read(owner="sasha", limit=10)
        assert ret["total"] == 0 and len(ret["items"]) == 0 and ret["limit"] == 10, ret

        ret = rest_su_session.vault.read(name="key", owner="masha", limit=10)
        assert ret["total"] == 0 and len(ret["items"]) == 0 and ret["limit"] == 10, ret

        ret = rest_su_session.vault.read(name="key", owner="vasya", limit=10)
        assert ret["total"] == 1 and len(ret["items"]) == 1 and ret["limit"] == 10, ret

        ret = rest_su_session.vault.read(name="key", limit=10)
        assert ret["total"] == 2 and len(ret["items"]) == 2 and ret["limit"] == 10, ret

        ret = rest_su_session.vault.read(limit=2)
        assert ret["total"] == 4 and len(ret["items"]) == 2 and ret["limit"] == 2, ret  # an admin can read all records

        task = task_manager.create("TEST_TASK", "masha", "masha")
        task.save()
        oauth = yasandbox.database.mapping.OAuthCache(
            token=uuid.uuid4().hex,
            login=rest_session_login,
            ttl=60,
            source=":".join([ctu.TokenSource.CLIENT, "somehost"]),
            task_id=task.id,
        )
        oauth.save()

        task_session = common.rest.Client(json_api_url, auth=common.proxy.Session(None, oauth.token))
        ret = task_session.vault.read({"limit": 10})
        items = ret["items"]

        # there are only records which task owner is allowed to at least read, but "total" shows there are more items
        assert ret["total"] == 4 and len(items) == 2 and ret["limit"] == 10, ret
        for i, (record, rights) in enumerate(zip(
            vaults[1:3],
            [ctu.Rights.READ, ctu.Rights.WRITE]
        )):
            assert items[i]["id"] == record.id and items[i]["rights"] == rights, items[i]

        ret = task_session.vault.read({"name": "key", "limit": 10})
        items = ret["items"]
        # there's only one accessible key, although two keys exist, hence it's instantly available
        assert ret["total"] == 2 and len(items) == 1 and ret["limit"] == 10, ret
        assert items[0]["id"] == vaults[1].id and items[0]["rights"] == ctu.Rights.READ

    def test__vault_get_data(
        self,
        server, json_api_url, rest_su_session_login, rest_su_session, vault_controller, group_controller,
        api_session_login, api_session, api_session_group, client_and_task, another_user
    ):
        random_key = uuid.uuid4().hex
        vault = vault_controller.create(yasandbox.database.mapping.Vault(
            owner="vasya",
            name="key",
            data=random_key
        ))

        with pytest.raises(rest_su_session.HTTPError) as excinfo:
            rest_su_session.vault[vault.id].data.read()
        assert (
            excinfo.value.status == httplib.FORBIDDEN and
            "Allowed only with task session token" in str(excinfo.value)
        )

        client, task = client_and_task

        cipher = common.crypto.AES()
        client.save()
        oauth = yasandbox.database.mapping.OAuthCache(
            token=uuid.uuid4().hex,
            login=rest_su_session_login,
            ttl=60,
            source=":".join([ctu.TokenSource.CLIENT, client.hostname]),
            task_id=task.id,
            vault=cipher.key,
        )
        oauth.save()

        task_session = common.rest.Client(json_api_url, auth=common.proxy.Session(None, oauth.token))
        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault[vault.id + 100].data.read()
        assert excinfo.value.status == httplib.NOT_FOUND

        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault[vault.id].data.read()
        assert (
            excinfo.value.status == httplib.INTERNAL_SERVER_ERROR and
            "Unknown task #{} owner '{}'".format(task.id, task.owner) in str(excinfo.value)
        ), str(excinfo.value)

        task.author = api_session_login
        task.owner = api_session_login
        task.save()
        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault[vault.id].data.read()
        assert (
            excinfo.value.status == httplib.FORBIDDEN and
            all(_ in str(excinfo.value) for _ in ("is not allowed to get vault item", "owned by"))
        ), str(excinfo.value)

        vault.allowed_users = [task.owner]
        vault.save()
        encrypted_data = (task_session >> task_session.BINARY).vault[vault.id].data[...]
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == random_key

        vault.allowed_users = [api_session_group]
        vault.save()
        encrypted_data = (task_session >> task_session.BINARY).vault[vault.id].data[...]
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == random_key

        task.owner = api_session_group
        task.save()
        encrypted_data = (task_session >> task_session.BINARY).vault[vault.id].data[...]
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == random_key

        vault.allowed_users = [task.owner]
        vault.save()
        encrypted_data = (task_session >> task_session.BINARY).vault[vault.id].data[...]
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == random_key

        vault.allowed_users = []
        vault.save()
        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault[vault.id].data.read()
        assert (
            excinfo.value.status == httplib.FORBIDDEN and
            all(_ in str(excinfo.value) for _ in ("is not allowed to get vault item", "owned by"))
        ), str(excinfo.value)

        vault.owner = api_session_group
        vault.save()
        encrypted_data = (task_session >> task_session.BINARY).vault[vault.id].data[...]
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == random_key

        task.owner = api_session_login
        task.save()
        encrypted_data = (task_session >> task_session.BINARY).vault[vault.id].data[...]
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == random_key

        vault.owner = api_session_login
        vault.save()
        encrypted_data = (task_session >> task_session.BINARY).vault[vault.id].data[...]
        decrypted_data = cipher.decrypt(encrypted_data, False)
        assert decrypted_data == random_key

        task.author = another_user.login
        task.owner = api_session_group
        task.save()
        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault[vault.id].data.read()
        assert (
            excinfo.value.status == httplib.FORBIDDEN and
            all(_ in str(excinfo.value) for _ in ("is not allowed to get vault item", "owned by"))
        ), str(excinfo.value)

    def test__vault_data(
            self,
            server, json_api_url, rest_su_session, vault_controller, group_controller, rest_session,
            api_session_login, api_session, api_session_group, client_and_task, another_user, rest_session_login
    ):
        cipher = common.crypto.AES()

        def decrypt_data(data):
            encrypted_data = base64.b64decode(data)
            decrypted_data = cipher.decrypt(encrypted_data, False)
            return decrypted_data

        def check_vault_data(data, vault, random_key):
            assert int(data["id"]) == vault.id
            assert decrypt_data(data["data"]) == random_key

        random_key = uuid.uuid4().hex
        vault = vault_controller.create(yasandbox.database.mapping.Vault(
            owner="vasya",
            name="key",
            data=random_key
        ))

        with pytest.raises(rest_su_session.HTTPError) as excinfo:
            rest_su_session.vault.data.read(name="key", owner="vasya")
        assert (
            excinfo.value.status == httplib.FORBIDDEN
        )

        query = {"name": "key"}

        client, task = client_and_task

        client.save()
        oauth = yasandbox.database.mapping.OAuthCache(
            token=uuid.uuid4().hex,
            login=rest_session_login,
            ttl=60,
            source=":".join([ctu.TokenSource.CLIENT, client.hostname]),
            task_id=task.id,
            vault=cipher.key,
        )
        oauth.save()

        task_session = common.rest.Client(json_api_url, auth=common.proxy.Session(None, oauth.token))

        task.author = api_session_login
        task.owner = api_session_login
        task.save()
        vault.allowed_users = [task.owner]
        vault.save()
        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        vault.allowed_users = [api_session_group]
        vault.save()
        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        task.owner = api_session_group
        task.save()
        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        vault.allowed_users = [task.owner]
        vault.save()
        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        vault.allowed_users = []
        vault.save()
        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault.data.read(**query)
        assert (
            excinfo.value.status == httplib.FORBIDDEN
        ), str(excinfo.value)

        vault.owner = api_session_group
        vault.save()
        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        task.owner = api_session_login
        task.save()
        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        vault.owner = api_session_login
        vault.save()
        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        task.author = another_user.login
        task.owner = api_session_group
        task.save()
        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault.data.read(**query)
        assert (
            excinfo.value.status == httplib.FORBIDDEN
        ), str(excinfo.value)

        vault2 = vault_controller.create(yasandbox.database.mapping.Vault(
            owner="petya",
            name="key",
            data="topsecret0987",
            allowed_users=[],
        ))
        task.author = api_session_login
        task.owner = api_session_login
        task.save()
        vault.allowed_users = [task.owner]
        vault.save()

        data = task_session.vault.data.read(**query)
        check_vault_data(data, vault, random_key)

        vault2.allowed_users = [api_session_group]
        vault2.save()
        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault.data.read(**query)
        assert (
            excinfo.value.status == httplib.NOT_FOUND
        ), str(excinfo.value)

        vault2.name = "key2"
        vault2.allowed_users = []
        vault2.save()

        with pytest.raises(task_session.HTTPError) as excinfo:
            task_session.vault.data.read({"name": "key2"})
        assert (
            excinfo.value.status == httplib.FORBIDDEN
        ), str(excinfo.value)
