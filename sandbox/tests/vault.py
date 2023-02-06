import json
import pytest
import hashlib

from sandbox import sdk2

from sandbox.common import auth as common_auth
from sandbox.common import rest
from sandbox.common import errors as common_errors

from sandbox.yasandbox.database import mapping as mp


@pytest.yield_fixture()
def prepare_vault(group_controller, rest_session, rest_session_login, rest_session_group, task_session, monkeypatch):

    vault_key = "a" * 16
    sdk2.Vault.vault_key = vault_key

    task_id = rest_session.task(type="TEST_TASK_2", owner=rest_session_group, description="whatever")["id"]
    task_token = task_session(rest_session, task_id, rest_session_login, vault_key=vault_key)
    monkeypatch.setattr(rest.Client, "_external_auth", common_auth.OAuth(task_token))

    yield

    # Reset vault key
    sdk2.Vault._decrypt.im_func.__defaults__ = (None,)


@pytest.mark.usefixtures("server", "prepare_vault")
class TestVaultData(object):

    @staticmethod
    def __data(*args):
        s = json.dumps(args)
        return hashlib.md5(s).hexdigest()

    @classmethod
    def __make_vault(cls, vault_controller, owner, name, shared_with):
        # noinspection PyArgumentList
        vault_controller.create(mp.Vault(
            owner=owner,
            name=name,
            data=cls.__data(owner, name),
            allowed_users=shared_with
        ))

    def test__vault_data(self, vault_controller, rest_su_session_group, rest_session_login, rest_session_group):

        nonexistent = "nonexistent"
        accessible = "accessible"
        inaccessible = "inaccessible"
        only_one_accessible = "only-one-of-these-is-accessible"

        with pytest.raises(common_errors.VaultNotFound):
            sdk2.Vault.data(nonexistent)

        self.__make_vault(vault_controller, rest_session_group, accessible, [])
        self.__make_vault(vault_controller, rest_su_session_group, accessible, [rest_session_login])

        with pytest.raises(common_errors.VaultNotFound):
            sdk2.Vault.data(accessible)

        assert sdk2.Vault.data(rest_session_group, accessible) == self.__data(rest_session_group, accessible)
        assert sdk2.Vault.data(rest_su_session_group, accessible) == self.__data(rest_su_session_group, accessible)

        self.__make_vault(vault_controller, rest_su_session_group, inaccessible, [])
        with pytest.raises(common_errors.VaultNotAllowed):
            sdk2.Vault.data(inaccessible)

        self.__make_vault(vault_controller, rest_session_group, only_one_accessible, [])
        self.__make_vault(vault_controller, rest_su_session_group, only_one_accessible, [])

        assert sdk2.Vault.data(only_one_accessible) == self.__data(rest_session_group, only_one_accessible)

    def test__vault_batch(self, vault_controller, rest_su_session_group, rest_session_group):

        self.__make_vault(vault_controller, rest_session_group, "V1", [])
        self.__make_vault(vault_controller, rest_su_session_group, "V2", [])

        data_v1 = self.__data(rest_session_group, "V1")

        # Non-batch
        assert sdk2.Vault.data("V1") == data_v1

        # Batch
        with sdk2.Vault.batch:
            not_found = sdk2.Vault.data("V0")
            not_allowed = sdk2.Vault.data("V2")

            ok = sdk2.Vault.data("V1")
            ok_with_group = sdk2.Vault.data(rest_session_group, "V1")
            ok_vaultitem = sdk2.VaultItem(rest_session_group, "V1").data()

        with pytest.raises(common_errors.VaultNotFound):
            not_found.result()

        with pytest.raises(common_errors.VaultNotAllowed):
            not_allowed.result()

        assert ok.result() == data_v1
        assert ok_with_group.result() == data_v1
        assert ok_vaultitem.result() == data_v1

        # Non-batch again
        assert sdk2.Vault.data("V1") == data_v1
