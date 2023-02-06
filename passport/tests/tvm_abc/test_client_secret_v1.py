# -*- coding: utf-8 -*-

from django.conf import settings
from django.urls import reverse_lazy
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.tvm_api.tests.base.vault_test import (
    TEST_VAULT_SECRET_UUID_1,
    TEST_VAULT_VERSION_UUID_1,
    TEST_VAULT_VERSION_UUID_2,
    VaultMockMixin,
)
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient

from .base import (
    BaseTvmAbcTestcaseWithCookieOrToken,
    CommonRoleTests,
    CommonUserAuthTests,
    TEST_ABC_SERVICE_ID,
    TEST_OTHER_UID,
)


class BaseClientSecretV1Testcase(BaseTvmAbcTestcaseWithCookieOrToken):
    http_method = 'POST'

    def default_params(self):
        return dict(
            super(BaseClientSecretV1Testcase, self).default_params(),
            client_id=self.test_client.id,
        )


class CheckSecretSavedMixin(VaultMockMixin):
    def test_secrets_not_saved_to_vault(self):
        with UPDATE(self.test_client) as client:
            del client.vault_version_uuid
        rv = self.make_request()
        self.assert_status_error(rv, ['secret.not_put_to_vault'])

    def test_disabe_check_secrets_not_saved_to_vault(self):
        try:
            old_dcs_flag = settings.DISABLE_CHECK_SECRET_SAVED_TO_VAULT
            settings.DISABLE_CHECK_SECRET_SAVED_TO_VAULT = True

            with UPDATE(self.test_client) as client:
                del client.vault_version_uuid
            with self.vault_mock() as vault:
                self.register_default_mocks(vault)
                rv = self.make_request()
            self.assert_status_ok(rv)
        finally:
            settings.DISABLE_CHECK_SECRET_SAVED_TO_VAULT = old_dcs_flag


class SaveSecretToVaultV1Testcase(BaseClientSecretV1Testcase, CommonUserAuthTests, CommonRoleTests, VaultMockMixin):
    default_url = reverse_lazy('tvm_abc_save_secret_to_vault_v1')

    def test_ok(self):
        with UPDATE(self.test_client) as client:
            del client.vault_secret_uuid
            del client.vault_version_uuid

        with self.vault_mock() as vault:
            self.vault_register_create_complete_secret_ok(vault)
            rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        ok_(not client.old_client_secret)
        eq_(client.modified, DatetimeNow())
        eq_(
            rv['content'],
            {
                'attributes': {
                    'secret_uuid': client.vault_secret_uuid,
                    'version_uuid': client.vault_version_uuid,
                    'vault_link': settings.VAULT_SECRET_LINK_TEMPLATE.format(
                        secret_uuid=client.vault_secret_uuid,
                        version_uuid=client.vault_version_uuid,
                    ),
                },
            },
        )
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, TEST_VAULT_VERSION_UUID_1)

        eq_(len(vault.request_history), 1)

        self.assert_vault_request_equals(
            vault.request_history[0],
            {
                'body': {
                    'comment': 'TVM-secret, ID %s' % client.id,
                    'name': 'tvm.secret.%s' % client.id,
                    'roles': [
                        dict(role='OWNER', abc_id=TEST_ABC_SERVICE_ID, abc_role_id=abc_role_id)
                        for abc_role_id in settings.VAULT_SECRET_TVM_ROLES
                    ],
                    'secret_version': {
                        'value': [{
                            'key': 'client_secret',
                            'value': client.client_secret,
                        }],
                    },
                    'tags': settings.VAULT_SECRET_TAGS,
                },
                'method': 'POST',
                'path': '/web/secrets/',
                'query': '',
            },
        )

    def test_create_version_ok(self):
        with UPDATE(self.test_client) as client:
            del client.vault_version_uuid

        with self.vault_mock() as vault:
            self.vault_register_create_secret_version_ok(vault)
            rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        ok_(not client.old_client_secret)
        eq_(client.modified, DatetimeNow())
        eq_(
            rv['content'],
            {
                'attributes': {
                    'secret_uuid': client.vault_secret_uuid,
                    'version_uuid': client.vault_version_uuid,
                    'vault_link': settings.VAULT_SECRET_LINK_TEMPLATE.format(
                        secret_uuid=client.vault_secret_uuid,
                        version_uuid=client.vault_version_uuid,
                    ),
                },
            },
        )
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, TEST_VAULT_VERSION_UUID_1)

        eq_(len(vault.request_history), 1)

        self.assert_vault_request_equals(
            vault.request_history[0],
            {
                'body': {
                    'value': [{
                        'key': 'client_secret',
                        'value': client.client_secret,
                    }],
                },
                'method': 'POST',
                'path': '/1/secrets/%s/versions/' % TEST_VAULT_SECRET_UUID_1,
                'query': '',
            },
        )

    def test_create_complete_secret_error(self):
        with UPDATE(self.test_client) as client:
            del client.vault_secret_uuid
            del client.vault_version_uuid

        with self.vault_mock() as vault:
            self.vault_register_create_complete_secret_error(vault)
            rv = self.make_request()

        self.assert_status_error(rv, ['secret.not_put_to_vault'])

        client = TVMClient.by_id(self.test_client.id)
        ok_(not client.old_client_secret)
        eq_(client.vault_secret_uuid, '')
        eq_(client.vault_version_uuid, '')

    def test_create_secret_version_error(self):
        with UPDATE(self.test_client) as client:
            del client.vault_version_uuid

        with self.vault_mock() as vault:
            self.vault_register_create_secret_version_error(vault)
            rv = self.make_request()

        self.assert_status_error(rv, ['secret.not_put_to_vault'])

        client = TVMClient.by_id(self.test_client.id)
        ok_(not client.old_client_secret)
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, '')

    def test_client_without_abc(self):
        with UPDATE(self.test_client) as client:
            del client.vault_secret_uuid
            del client.vault_version_uuid
            del client.abc_service_id
            del client.abc_request_id
        rv = self.make_request()
        self.assert_status_error(rv, ['abc_team.member_required'])


class RecreateClientSecretV1Testcase(BaseClientSecretV1Testcase, CommonUserAuthTests, CommonRoleTests, CheckSecretSavedMixin, VaultMockMixin):
    default_url = reverse_lazy('tvm_abc_recreate_client_secret_v1')

    def test_ok(self):
        secret = self.test_client.client_secret

        with self.vault_mock() as vault:
            self.vault_register_create_secret_version_ok(vault, version_uuid=TEST_VAULT_VERSION_UUID_2)
            rv = self.make_request()
        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        ok_(client.client_secret != secret)
        eq_(client.old_client_secret, secret)
        eq_(client.modified, DatetimeNow())
        eq_(
            rv['content'],
            {
                'attributes': {
                    'client_secret': client.client_secret,
                    'old_client_secret': client.old_client_secret,
                    'secret_uuid': client.vault_secret_uuid,
                    'version_uuid': client.vault_version_uuid,
                    'vault_link': settings.VAULT_SECRET_LINK_TEMPLATE.format(
                        secret_uuid=client.vault_secret_uuid,
                        version_uuid=client.vault_version_uuid,
                    ),
                },
            },
        )
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, TEST_VAULT_VERSION_UUID_2)

    def test_create_vault_version_error(self):
        secret = self.test_client.client_secret

        with self.vault_mock() as vault:
            self.vault_register_create_secret_version_error(vault)
            rv = self.make_request()
        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        ok_(client.client_secret != secret)
        eq_(client.old_client_secret, secret)
        eq_(client.modified, DatetimeNow())
        eq_(
            rv['content'],
            {
                'attributes': {
                    'client_secret': client.client_secret,
                    'old_client_secret': client.old_client_secret,
                },
            },
        )
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, '')

    def test_old_secret_exists(self):
        with UPDATE(self.test_client) as client:
            client.generate_client_secret()  # чтобы образовался old_client_secret
        rv = self.make_request()
        self.assert_status_error(rv, errors=['old_secret.exists'])

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])

    def test_unknown_uid(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['abc_team.member_required'])


class RestoreClientSecretV1Testcase(BaseClientSecretV1Testcase, CommonUserAuthTests, CommonRoleTests, CheckSecretSavedMixin, VaultMockMixin):
    default_url = reverse_lazy('tvm_abc_restore_old_client_secret_v1')

    def setUp(self):
        super(RestoreClientSecretV1Testcase, self).setUp()
        with UPDATE(self.test_client) as client:
            client.generate_client_secret()  # чтобы образовался old_client_secret

    def test_ok(self):
        secret = self.test_client.client_secret

        with UPDATE(self.test_client) as client:
            client.generate_client_secret()

        ok_(client.client_secret != secret)
        eq_(client.modified, DatetimeNow())

        with self.vault_mock() as vault:
            self.vault_register_create_secret_version_ok(vault, version_uuid=TEST_VAULT_VERSION_UUID_2)
            rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        eq_(client.client_secret, secret)
        eq_(
            rv['content'],
            {
                'attributes': {
                    'client_secret': client.client_secret,
                    'old_client_secret': client.old_client_secret,
                    'secret_uuid': client.vault_secret_uuid,
                    'version_uuid': client.vault_version_uuid,
                    'vault_link': settings.VAULT_SECRET_LINK_TEMPLATE.format(
                        secret_uuid=client.vault_secret_uuid,
                        version_uuid=client.vault_version_uuid,
                    ),
                },
            },
        )
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, TEST_VAULT_VERSION_UUID_2)

    def test_create_vault_version_error(self):
        secret = self.test_client.client_secret

        with UPDATE(self.test_client) as client:
            client.generate_client_secret()

        ok_(client.client_secret != secret)
        eq_(client.modified, DatetimeNow())

        with self.vault_mock() as vault:
            self.vault_register_create_secret_version_error(vault)
            rv = self.make_request()

        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        eq_(client.client_secret, secret)
        eq_(
            rv['content'],
            {
                'attributes': {
                    'client_secret': client.client_secret,
                    'old_client_secret': client.old_client_secret,
                },
            },
        )
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, '')

    def test_old_secret_missing(self):
        with UPDATE(self.test_client) as client:
            del client.old_client_secret
        rv = self.make_request()
        self.assert_status_error(rv, errors=['old_secret.not_found'])

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])

    def test_unknown_uid(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['abc_team.member_required'])


class DeleteOldClientSecretV1Testcase(BaseClientSecretV1Testcase, CommonUserAuthTests, CommonRoleTests, CheckSecretSavedMixin):
    default_url = reverse_lazy('tvm_abc_delete_old_client_secret_v1')

    def setUp(self):
        super(DeleteOldClientSecretV1Testcase, self).setUp()
        with UPDATE(self.test_client) as client:
            client.generate_client_secret()  # чтобы образовался old_client_secret

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        ok_(not client.old_client_secret)
        eq_(client.modified, DatetimeNow())
        eq_(
            rv['content'],
            {
                'attributes': {
                    'client_secret': client.client_secret,
                    'old_client_secret': None,
                    'secret_uuid': client.vault_secret_uuid,
                    'version_uuid': client.vault_version_uuid,
                    'vault_link': settings.VAULT_SECRET_LINK_TEMPLATE.format(
                        secret_uuid=client.vault_secret_uuid,
                        version_uuid=client.vault_version_uuid,
                    ),
                },
            },
        )
        eq_(client.vault_secret_uuid, TEST_VAULT_SECRET_UUID_1)
        eq_(client.vault_version_uuid, TEST_VAULT_VERSION_UUID_1)

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])

    def test_unknown_uid(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['abc_team.member_required'])
