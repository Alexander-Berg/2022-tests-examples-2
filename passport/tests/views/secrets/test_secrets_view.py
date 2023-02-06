# -*- coding: utf-8 -*-

from base64 import b64encode

from library.python.vault_client.errors import ClientError
import mock
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api import errors
from passport.backend.vault.api.models import (
    Roles,
    SecretVersion,
)
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    VALID_SERVICE_TICKET_SINGLESS_1,
    VALID_USER_TICKET_SIGNLESS_1,
)
from passport.backend.vault.api.test.uuid_mock import UuidMock
from passport.backend.vault.api.utils.errors import (
    InvalidUUIDPrefix,
    InvalidUUIDValue,
)
from passport.backend.vault.api.utils.ulid import create_ulid


class TestSecretsView(BaseTestClass):
    send_user_ticket = True

    def setUp(self):
        super(TestSecretsView, self).setUp()
        self.fixture.add_user(uid=200)

    def test_secrets_same_name(self):
        with PermissionsMock(uid=100):
            self.client.create_secret('secret_password', return_raw=True)
            r2 = self.client.create_secret('secret_password', return_raw=True)
            self.assertResponseOk(r2)

    def test_get_secret(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=100):
                with UuidMock(base_value=7000000):
                    self.client.create_token(
                        'sec-0000000000000000000000ygj0',
                        tvm_client_id=999,
                    )
                    self.client.create_token(
                        'sec-0000000000000000000000ygj0',
                        tvm_client_id=2000367,
                    )
                    _, token_3_uuid = self.client.create_token(
                        'sec-0000000000000000000000ygj0',
                        tvm_client_id=2000367,
                    )
                    self.client.revoke_token(token_3_uuid)

            r = self.client.get_secret('sec-0000000000000000000000ygj0', return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secret': {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'secret_versions': [{
                        'created_at': 1445385603.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'keys': ['password'],
                        'version': 'ver-0000000000000000000000ygj4',
                    }, {
                        'created_at': 1445385602.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'keys': ['password'],
                        'version': 'ver-0000000000000000000000ygj3',
                    }, {
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'keys': ['password'],
                        'version': 'ver-0000000000000000000000ygj2',
                    }],
                    'tokens': [{
                        'created_at': 1445385700.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'secret_uuid': 'sec-0000000000000000000000ygj0',
                        'state_name': 'normal',
                        'tvm_client_id': 999,
                        'token_uuid': 'tid-0000000000000000000006nky0',
                    }, {
                        'created_at': 1445385700.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'secret_uuid': 'sec-0000000000000000000000ygj0',
                        'state_name': 'normal',
                        'tvm_client_id': 2000367,
                        u'tvm_app': {
                            u'abc_department': {
                                u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                u'id': 14,
                                u'unique_name': u'passp',
                            },
                            u'abc_state': u'granted',
                            u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                            u'name': u'social api (dev)',
                            u'tvm_client_id': 2000367,
                        },
                        'token_uuid': 'tid-0000000000000000000006nky1',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                },
                'status': 'ok',
            })

    def test_get_secret_version(self):
        with PermissionsMock(uid=100):
            r = self.client.get_version('ver-0000000000000000000000ygj2')
            self.assertDictEqual(r, {
                'created_at': 1445385601,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'value': {'password': '123'},
                'version': 'ver-0000000000000000000000ygj2',
                'secret_name': 'secret_1',
                'secret_uuid': 'sec-0000000000000000000000ygj0',
            })

    def test_get_nonexistent_secret_version(self):
        with PermissionsMock(uid=100):
            uuid = 'ver-00000000000000000000000000'
            r = self.client.get_version(uuid, return_raw=True)
            self.assertResponseError(
                r,
                errors.NonexistentEntityError(
                    entity_class=SecretVersion,
                    entity_id='00000000000000000000000000',
                ),
            )

    def test_get_corrupted_secret_version(self):
        with PermissionsMock(uid=100):
            with mock.patch(
                'passport.backend.vault.api.value_manager.ValueManager.decode',
                side_effect=errors.DecryptionError
            ):
                r = self.client.get_version('ver-0000000000000000000000ygj2', return_raw=True)
                self.assertResponseError(r, errors.DecryptionError)

    def test_list_secrets(self):
        with PermissionsMock(uid=100):
            r = self.client.list_secrets(return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

    def test_get_secrets_with_roles(self):
        with PermissionsMock(uid=100):
            r = self.client.list_secrets(role='READER', return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

    def test_list_your_secret(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=100):
                with UuidMock(base_value=7000000):
                    self.client.create_token(
                        'sec-0000000000000000000000ygj0',
                        tvm_client_id=999,
                    )
                    self.client.create_token(
                        'sec-0000000000000000000000ygj0',
                        tvm_client_id=2000367,
                    )
                    _, token_3_uuid = self.client.create_token(
                        'sec-0000000000000000000000ygj0',
                        tvm_client_id=2000367,
                    )
                    self.client.revoke_token(token_3_uuid)

        with PermissionsMock(uid=100, fixture=self.fixture, staff_groups=[38096]):
            r = self.client.list_secrets(yours=True, return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'role_slug': 'OWNER', 'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'role_slug': 'OWNER', 'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'role_slug': 'OWNER', 'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 2,
                }],
                'status': 'ok',
            })

    def test_get_service_with_staff_group(self):
        with PermissionsMock(uid=100, fixture=self.fixture, staff_groups=[38096]):
            r = self.client.list_secrets(return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'role_slug': 'READER',
                        'staff_id': 38096,
                        'created_at': 1445385610.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'staff_name': u'Управление качества поисковых продуктов',
                        'staff_slug': u'yandex_search_tech_sq',
                        'staff_url': u'https://staff.yandex-team.ru/departments/yandex_search_tech_sq/',
                    }],
                    'effective_role': 'READER',
                    'created_at': 1445385609.0,
                    'created_by': 101,
                    'creator_login': 'vault-test-101',
                    'name': 'secret_3',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygjg'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 101,
                        'created_at': 1445385609.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'login': 'vault-test-101',
                    }, {
                        'role_slug': 'READER',
                        'staff_id': 38096,
                        'created_at': 1445385610.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'staff_name': u'Управление качества поисковых продуктов',
                        'staff_slug': u'yandex_search_tech_sq',
                        'staff_url': u'https://staff.yandex-team.ru/departments/yandex_search_tech_sq/',
                    }],
                    'updated_at': 1445385612.0,
                    'updated_by': 101,
                    'uuid': 'sec-0000000000000000000000ygjb',
                    'versions_count': 3,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'role_slug': 'OWNER', 'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'role_slug': 'OWNER', 'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'role_slug': 'OWNER', 'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

    def test_get_service_with_abc_group(self):
        with PermissionsMock(uid=100, fixture=self.fixture, abc_groups=[(14, 8)]):
            r = self.client.list_secrets(return_raw=True)

            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [
                    {
                        'acl': [{
                            'created_at': 1445385604.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100
                        }],
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'effective_role': 'OWNER',
                        'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                        'name': 'secret_2',
                        'secret_roles': [{
                            'created_at': 1445385604.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100
                        }],
                        'tokens_count': 0,
                        'updated_at': 1445385608.0,
                        'updated_by': 100,
                        'uuid': 'sec-0000000000000000000000ygj5',
                        'versions_count': 4
                    },
                    {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100
                        }],
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'effective_role': 'OWNER',
                        'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                        'name': 'secret_1',
                        'secret_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100
                        }],
                        'tokens_count': 0,
                        'updated_at': 1445385603.0,
                        'updated_by': 100,
                        'uuid': 'sec-0000000000000000000000ygj0',
                        'versions_count': 3
                    }
                ],
                'status': 'ok'
            })

        with PermissionsMock(uid=100, fixture=self.fixture, abc_groups=[(14, 5)]):
            r = self.client.list_secrets(return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'abc_id': 14,
                        'created_at': 1445385614.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'role_slug': 'READER',
                        'abc_name': u'Паспорт',
                        'abc_scope': 'development',
                        'abc_scope_id': 5,
                        'abc_scope_name': u'Разработка',
                        'abc_slug': u'passp',
                        'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                    }],
                    'effective_role': 'READER',
                    'created_at': 1445385613.0,
                    'created_by': 101,
                    'creator_login': 'vault-test-101',
                    'name': 'secret_4',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygjq'},
                    'secret_roles': [{
                        'created_at': 1445385613.0,
                        'created_by': 101,
                        'role_slug': 'OWNER',
                        'uid': 101,
                        'login': 'vault-test-101',
                        'creator_login': 'vault-test-101',
                    }, {
                        'abc_id': 14,
                        'created_at': 1445385614.0,
                        'created_by': 101,
                        'role_slug': 'READER',
                        'creator_login': 'vault-test-101',
                        'abc_name': u'Паспорт',
                        'abc_scope': 'development',
                        'abc_scope_name': u'Разработка',
                        'abc_scope_id': 5,
                        'abc_slug': u'passp',
                        'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                    }],
                    'updated_at': 1445385617.0,
                    'updated_by': 101,
                    'uuid': 'sec-0000000000000000000000ygjh',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

    def test_get_secrets_with_order(self):
        with PermissionsMock(uid=100):
            r = self.client.list_secrets(order_by='uuid', asc=0, return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

    def test_supervisors(self):
        with PermissionsMock(uid=100, supervisor=True):
            self.assertEqual(self.get_roles(1001), [])
            r = self.client.add_supervisor(1001, return_raw=True)
            self.assertResponseEqual(r, {
                'status': 'ok',
            })
            self.assertEqual(self.get_roles(1001), [Roles.SUPERVISOR])

    def test_not_supervisor_add_supervisor(self):
        with PermissionsMock(uid=10011):
            self.assertEqual(self.get_roles(1002), [])
            r = self.client.add_supervisor(1002, return_raw=True)
            self.assertResponseError(r, errors.AccessError)
            self.assertEqual(self.get_roles(1002), [])

    def test_get_secrets_for_supervisor(self):
        with PermissionsMock(uid=100, supervisor=True):
            r = self.client.list_secrets(return_raw=True)
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'created_at': 1445385613.0,
                    'created_by': 101,
                    'creator_login': 'vault-test-101',
                    'name': 'secret_4',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygjq'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 101,
                        'created_at': 1445385613.0,
                        'created_by': 101,
                        'login': 'vault-test-101',
                        'creator_login': 'vault-test-101',
                    }, {
                        'abc_id': 14,
                        'role_slug': 'READER',
                        'created_at': 1445385614.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'abc_name': u'Паспорт',
                        'abc_slug': u'passp',
                        'abc_scope': 'development',
                        'abc_scope_name': u'Разработка',
                        'abc_scope_id': 5,
                        'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                    }],

                    'updated_at': 1445385617.0,
                    'updated_by': 101,
                    'uuid': 'sec-0000000000000000000000ygjh',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'created_at': 1445385609.0,
                    'created_by': 101,
                    'creator_login': 'vault-test-101',
                    'name': 'secret_3',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygjg'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 101,
                        'created_at': 1445385609.0,
                        'created_by': 101,
                        'login': 'vault-test-101',
                        'creator_login': 'vault-test-101',
                    }, {
                        'role_slug': 'READER',
                        'staff_id': 38096,
                        'created_at': 1445385610.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'staff_name': u'Управление качества поисковых продуктов',
                        'staff_slug': u'yandex_search_tech_sq',
                        'staff_url': u'https://staff.yandex-team.ru/departments/yandex_search_tech_sq/',
                    }],
                    'updated_at': 1445385612.0,
                    'updated_by': 101,
                    'uuid': 'sec-0000000000000000000000ygjb',
                    'versions_count': 3,
                    'tokens_count': 0,
                }, {
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

    def test_get_secrets_pagination(self):
        with PermissionsMock(uid=100, fixture=self.fixture, abc_groups=[(14, 5)]):
            r1 = self.client.list_secrets(page=0, page_size=2, return_raw=True)
            self.assertResponseEqual(r1, {
                'page': 0,
                'page_size': 2,
                'secrets': [{
                    'acl': [{
                        'role_slug': 'READER',
                        'abc_id': 14,
                        'created_at': 1445385614.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'abc_name': u'Паспорт',
                        'abc_slug': u'passp',
                        'abc_scope': 'development',
                        'abc_scope_id': 5,
                        'abc_scope_name': u'Разработка',
                        'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                    }],
                    'effective_role': 'READER',
                    'created_at': 1445385613.0,
                    'created_by': 101,
                    'creator_login': 'vault-test-101',
                    'name': 'secret_4',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygjq'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 101,
                        'created_at': 1445385613.0,
                        'created_by': 101,
                        'login': 'vault-test-101',
                        'creator_login': 'vault-test-101',
                    }, {
                        'abc_id': 14,
                        'role_slug': 'READER',
                        'created_at': 1445385614.0,
                        'created_by': 101,
                        'creator_login': 'vault-test-101',
                        'abc_name': u'Паспорт',
                        'abc_scope': 'development',
                        'abc_scope_name': u'Разработка',
                        'abc_scope_id': 5,
                        'abc_slug': u'passp',
                        'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                    }],

                    'updated_at': 1445385617.0,
                    'updated_by': 101,
                    'uuid': 'sec-0000000000000000000000ygjh',
                    'versions_count': 4,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385604.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385608.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'versions_count': 4,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })
            r2 = self.client.list_secrets(page=1, page_size=2, return_raw=True)
            self.assertResponseEqual(r2, {
                'page': 1,
                'page_size': 2,
                'secrets': [{
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'versions_count': 3,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })
            r3 = self.client.list_secrets(page=2, page_size=2, return_raw=True)
            self.assertResponseEqual(r3, {
                'page': 2,
                'page_size': 2,
                'secrets': [],
                'status': 'ok',
            })

    def test_get_secret_pagination(self):
        with PermissionsMock(uid=100):
            r1 = self.client.get_secret('sec-0000000000000000000000ygj0', page=0, page_size=2,
                                        return_raw=True)
            self.assertResponseEqual(r1, {
                'page': 0,
                'page_size': 2,
                'secret': {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'secret_versions': [{
                        'created_at': 1445385603.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'keys': ['password'],
                        'version': 'ver-0000000000000000000000ygj4',
                    }, {
                        'created_at': 1445385602.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'keys': ['password'],
                        'version': 'ver-0000000000000000000000ygj3',
                    }],
                    'tokens': [],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                },
                'status': 'ok',
            })
            r2 = self.client.get_secret('sec-0000000000000000000000ygj0', page=1, page_size=2,
                                        return_raw=True)
            self.assertResponseEqual(r2, {
                'page': 1,
                'page_size': 2,
                'secret': {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'secret_versions': [{
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'keys': ['password'],
                        'version': 'ver-0000000000000000000000ygj2',
                    }],
                    'tokens': [],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                },
                'status': 'ok',
            })
            r3 = self.client.get_secret('sec-0000000000000000000000ygj0', page=2, page_size=2,
                                        return_raw=True)
            self.assertResponseEqual(r3, {
                'page': 2,
                'page_size': 2,
                'secret': {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_1',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'secret_versions': [],
                    'tokens': [],
                    'updated_at': 1445385603.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj0',
                },
                'status': 'ok',
            })

    def test_get_secret_with_diff(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')
                version_1 = self.client.create_secret_version(
                    secret,
                    value={
                        'name': 'pasha',
                        'password': '123456',
                        'pazzword': '654321',
                        'data': {
                            'k1': 'v1',
                            'k2': ['v2_2', 'v2_3'],
                            'k3': 12345,
                        },
                    },
                )
                version_2 = self.client.create_diff_version(
                    version_1,
                    [{
                        'key': 'login',
                        'value': 'pasha',
                    }, {
                        'key': 'pazzword',
                    }, {
                        'key': 'data',
                        'value': {
                            'k1': 'v1',
                            'k2': ['v2_2', 'v2_3', 'v2_4'],
                        },
                    }],
                    comment='fix some fields',
                )
                self.assertDictEqual(
                    self.client.get_secret(secret),
                    {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'effective_role': 'OWNER',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'ololo-secret',
                        'secret_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'secret_versions': [
                            {
                                'comment': 'fix some fields',
                                'created_at': 1445385600.0,
                                'created_by': 200,
                                'keys': ['data', 'login', 'name', 'password'],
                                'parent_diff_keys': {
                                    'added': ['login'],
                                    'removed': ['pazzword'],
                                    'changed': ['data'],
                                },
                                'parent_version_uuid': version_1,
                                'version': version_2,
                            },
                            {
                                'created_at': 1445385600.0,
                                'created_by': 200,
                                'keys': ['data', 'name', 'password', 'pazzword'],
                                'version': version_1,
                            },
                        ],
                        'tokens': [],
                        'updated_at': 1445385600.0,
                        'updated_by': 200,
                        'uuid': secret,
                    },
                )

    def test_get_secret_with_diff_and_empty_value(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')
                version_1 = self.client.create_secret_version(
                    secret,
                    value={
                        'dummy': 'dummy',
                    },
                )
                version_2 = self.client.create_diff_version(
                    version_1,
                    [{'key': 'dummy', 'value': ''}],
                    comment='fix some fields',
                )
                self.assertDictEqual(
                    self.client.get_version(version_2),
                    {
                        'comment': 'fix some fields',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'parent_version_uuid': version_1,
                        'secret_name': 'ololo-secret',
                        'secret_uuid': secret,
                        'value': {'dummy': ''},
                        'version': version_2,
                    },
                )

    def test_get_owners(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('secret_password')
                version = self.client.create_secret_version(secret, value={'key': 'value'})
                self.client.add_user_role_to_secret(secret, role='READER', uid=101)
                self.client.add_user_role_to_secret(secret, role='OWNER', abc_id=50)
                self.client.add_user_role_to_secret(secret, role='APPENDER', abc_id=14)
                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [
                        {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100,
                        },
                        {
                            'abc_id': 50,
                            'abc_name': u'Перевод саджеста',
                            'abc_scope': 'development',
                            'abc_scope_name': u'Разработка',
                            'abc_scope_id': 5,
                            'abc_slug': 'suggest',
                            'abc_url': 'https://abc.yandex-team.ru/services/suggest/',
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'role_slug': 'OWNER',
                        },
                        {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-101',
                            'role_slug': 'READER',
                            'uid': 101,
                        },
                        {
                            u'abc_id': 14,
                            u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                            u'abc_scope': u'development',
                            u'abc_scope_id': 5,
                            u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                            u'abc_slug': u'passp',
                            u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                            u'created_at': 1445385615.0,
                            u'created_by': 100,
                            u'creator_login': u'vault-test-100',
                            u'role_slug': u'APPENDER',
                        },
                    ],
                )

        self.assertResponseEqual(
            self.client.get_owners(secret, return_raw=True),
            {
                'secret_uuid': secret,
                'name': 'secret_password',
                'owners': [
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    },
                    {
                        'abc_id': 50,
                        'abc_name': u'Перевод саджеста',
                        'abc_scope': 'development',
                        'abc_scope_name': u'Разработка',
                        'abc_scope_id': 5,
                        'abc_slug': 'suggest',
                        'abc_url': 'https://abc.yandex-team.ru/services/suggest/',
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'role_slug': 'OWNER',
                    },
                ],
                'status': 'ok',
            },
        )

        self.assertResponseEqual(
            self.client.get_owners(version, return_raw=True),
            {
                'secret_uuid': secret,
                'name': 'secret_password',
                'owners': [
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    },
                    {
                        'abc_id': 50,
                        'abc_name': u'Перевод саджеста',
                        'abc_scope': 'development',
                        'abc_scope_name': u'Разработка',
                        'abc_scope_id': 5,
                        'abc_slug': 'suggest',
                        'abc_url': 'https://abc.yandex-team.ru/services/suggest/',
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'role_slug': 'OWNER',
                    },
                ],
                'status': 'ok',
            },
        )

    def test_get_owners_for_hidden_secret(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('secret_password')
                self.client.add_user_role_to_secret(secret, role='READER', uid=101)
                self.client.add_user_role_to_secret(secret, role='OWNER', abc_id=50)
                self.client.add_user_role_to_secret(secret, role='APPENDER', abc_id=14)
                self.client.update_secret(secret, state='hidden')

        self.assertResponseEqual(
            self.client.get_owners(secret, return_raw=True),
            {
                'secret_uuid': secret,
                'name': 'secret_password',
                'owners': [
                    {
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    },
                    {
                        'abc_id': 50,
                        'abc_name': u'Перевод саджеста',
                        'abc_scope': 'development',
                        'abc_scope_name': u'Разработка',
                        'abc_scope_id': 5,
                        'abc_slug': 'suggest',
                        'abc_url': 'https://abc.yandex-team.ru/services/suggest/',
                        'created_at': 1445385615.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'role_slug': 'OWNER',
                    },
                ],
                'status': 'warning',
                'warning_message': 'version is hidden',
            },
        )

    def test_get_readers(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('secret_password')
                version = self.client.create_secret_version(secret, value={'key': 'value'})
                self.client.add_user_role_to_secret(secret, role='READER', uid=101)
                self.client.add_user_role_to_secret(secret, role='OWNER', abc_id=50)
                self.client.add_user_role_to_secret(secret, role='APPENDER', abc_id=14)
                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [
                        {u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 100},
                        {u'abc_id': 50,
                         u'abc_name': u'Перевод саджеста',
                         u'abc_scope': u'development',
                         u'abc_scope_id': 5,
                         u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                         u'abc_slug': u'suggest',
                         u'abc_url': u'https://abc.yandex-team.ru/services/suggest/',
                         u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'role_slug': u'OWNER'},
                        {u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'login': u'vault-test-101',
                         u'role_slug': u'READER',
                         u'uid': 101},
                        {u'abc_id': 14,
                         u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                         u'abc_scope': u'development',
                         u'abc_scope_id': 5,
                         u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                         u'abc_slug': u'passp',
                         u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                         u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'role_slug': u'APPENDER'},
                    ]
                )

        self.assertResponseEqual(
            self.client.get_readers(secret, return_raw=True),
            {
                u'secret_uuid': secret,
                u'name': u'secret_password',
                u'readers': [
                    {u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'login': u'vault-test-100',
                     u'role_slug': u'OWNER',
                     u'uid': 100},
                    {u'abc_id': 50,
                     u'abc_name': u'Перевод саджеста',
                     u'abc_scope': u'development',
                     u'abc_scope_id': 5,
                     u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                     u'abc_slug': u'suggest',
                     u'abc_url': u'https://abc.yandex-team.ru/services/suggest/',
                     u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'role_slug': u'OWNER'},
                    {u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'login': u'vault-test-101',
                     u'role_slug': u'READER',
                     u'uid': 101},
                ],
                u'status': u'ok',
            }
        )

        self.assertResponseEqual(
            self.client.get_readers(version, return_raw=True),
            {
                u'secret_uuid': secret,
                u'name': u'secret_password',
                u'readers': [
                    {u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'login': u'vault-test-100',
                     u'role_slug': u'OWNER',
                     u'uid': 100},
                    {u'abc_id': 50,
                     u'abc_name': u'Перевод саджеста',
                     u'abc_scope': u'development',
                     u'abc_scope_id': 5,
                     u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                     u'abc_slug': u'suggest',
                     u'abc_url': u'https://abc.yandex-team.ru/services/suggest/',
                     u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'role_slug': u'OWNER'},
                    {u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'login': u'vault-test-101',
                     u'role_slug': u'READER',
                     u'uid': 101},
                ],
                u'status': u'ok',
            }
        )

    def test_get_readers_for_hidden_secret(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('secret_password')
                self.client.add_user_role_to_secret(secret, role='READER', uid=101)
                self.client.add_user_role_to_secret(secret, role='OWNER', abc_id=50)
                self.client.add_user_role_to_secret(secret, role='APPENDER', abc_id=14)
                self.client.update_secret(secret, state='hidden')

        self.assertResponseEqual(
            self.client.get_readers(secret, return_raw=True),
            {
                u'secret_uuid': secret,
                u'name': u'secret_password',
                u'readers': [
                    {u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'login': u'vault-test-100',
                     u'role_slug': u'OWNER',
                     u'uid': 100},
                    {u'abc_id': 50,
                     u'abc_name': u'Перевод саджеста',
                     u'abc_scope': u'development',
                     u'abc_scope_id': 5,
                     u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                     u'abc_slug': u'suggest',
                     u'abc_url': u'https://abc.yandex-team.ru/services/suggest/',
                     u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'role_slug': u'OWNER'},
                    {u'created_at': 1445385615.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'login': u'vault-test-101',
                     u'role_slug': u'READER',
                     u'uid': 101},
                ],
                u'status': u'warning',
                u'warning_message': u'version is hidden',
            }
        )

    def test_get_writers(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('secret_password')
                version = self.client.create_secret_version(secret, value={'key': 'value'})
                self.client.add_user_role_to_secret(secret, role='READER', uid=101)
                self.client.add_user_role_to_secret(secret, role='OWNER', abc_id=50)
                self.client.add_user_role_to_secret(secret, role='APPENDER', abc_id=14)

        self.assertResponseEqual(
            self.client.get_writers(secret, return_raw=True),
            {
                u'secret_uuid': secret,
                u'name': u'secret_password',
                u'status': u'ok',
                u'writers': [{u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'login': u'vault-test-100',
                              u'role_slug': u'OWNER',
                              u'uid': 100},
                             {u'abc_id': 50,
                              u'abc_name': u'\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u0441\u0430\u0434\u0436\u0435\u0441\u0442\u0430',
                              u'abc_scope': u'development',
                              u'abc_scope_id': 5,
                              u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                              u'abc_slug': u'suggest',
                              u'abc_url': u'https://abc.yandex-team.ru/services/suggest/',
                              u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'role_slug': u'OWNER'},
                             {u'abc_id': 14,
                              u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                              u'abc_scope': u'development',
                              u'abc_scope_id': 5,
                              u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                              u'abc_slug': u'passp',
                              u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                              u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'role_slug': u'APPENDER'}],
            }
        )

        self.assertResponseEqual(
            self.client.get_writers(version, return_raw=True),
            {
                u'secret_uuid': secret,
                u'name': u'secret_password',
                u'status': u'ok',
                u'writers': [{u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'login': u'vault-test-100',
                              u'role_slug': u'OWNER',
                              u'uid': 100},
                             {u'abc_id': 50,
                              u'abc_name': u'\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u0441\u0430\u0434\u0436\u0435\u0441\u0442\u0430',
                              u'abc_scope': u'development',
                              u'abc_scope_id': 5,
                              u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                              u'abc_slug': u'suggest',
                              u'abc_url': u'https://abc.yandex-team.ru/services/suggest/',
                              u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'role_slug': u'OWNER'},
                             {u'abc_id': 14,
                              u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                              u'abc_scope': u'development',
                              u'abc_scope_id': 5,
                              u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                              u'abc_slug': u'passp',
                              u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                              u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'role_slug': u'APPENDER'}],
            }
        )

    def test_get_writers_for_hidden_secret(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                secret = self.client.create_secret('secret_password')
                self.client.add_user_role_to_secret(secret, role='READER', uid=101)
                self.client.add_user_role_to_secret(secret, role='OWNER', abc_id=50)
                self.client.add_user_role_to_secret(secret, role='APPENDER', abc_id=14)
                self.client.update_secret(secret, state='hidden')

        self.assertResponseEqual(
            self.client.get_writers(secret, return_raw=True),
            {
                u'secret_uuid': secret,
                u'name': u'secret_password',
                u'status': u'warning',
                u'warning_message': u'version is hidden',
                u'writers': [{u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'login': u'vault-test-100',
                              u'role_slug': u'OWNER',
                              u'uid': 100},
                             {u'abc_id': 50,
                              u'abc_name': u'\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u0441\u0430\u0434\u0436\u0435\u0441\u0442\u0430',
                              u'abc_scope': u'development',
                              u'abc_scope_id': 5,
                              u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                              u'abc_slug': u'suggest',
                              u'abc_url': u'https://abc.yandex-team.ru/services/suggest/',
                              u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'role_slug': u'OWNER'},
                             {u'abc_id': 14,
                              u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                              u'abc_scope': u'development',
                              u'abc_scope_id': 5,
                              u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                              u'abc_slug': u'passp',
                              u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                              u'created_at': 1445385615.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'role_slug': u'APPENDER'}],
            }
        )

    def test_can_user_read_secret(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('secret')
            version = self.client.create_secret_version(secret, value={'key': 'value'})
            self.client.add_user_role_to_secret(secret, role='READER', uid=101)

        self.assertResponseEqual(
            self.client.can_user_read_secret(secret, uid=100, return_raw=True),
            {
                'secret_uuid': secret,
                'name': 'secret',
                'access': 'allowed',
                'status': 'ok',
                'user': {
                    'login': 'vault-test-100',
                    'uid': 100,
                },
            }

        )

        self.assertResponseEqual(
            self.client.can_user_read_secret(version, uid=100, return_raw=True),
            {
                'secret_uuid': secret,
                'name': 'secret',
                'access': 'allowed',
                'status': 'ok',
                'user': {
                    'login': 'vault-test-100',
                    'uid': 100,
                },
            }

        )

        self.assertTrue(self.client.can_user_read_secret(secret, uid=101))
        self.assertFalse(self.client.can_user_read_secret(secret, uid=102))

        self.assertResponseError(
            self.client.can_user_read_secret(
                create_ulid(prefix='sec'),
                uid=100,
                return_raw=True,
            ),
            errors.NonexistentEntityError,
        )
        self.assertResponseError(
            self.client.can_user_read_secret(
                create_ulid(prefix='ver'),
                uid=100,
                return_raw=True,
            ),
            errors.NonexistentEntityError,
        )
        self.assertResponseError(
            self.client.can_user_read_secret(
                secret,
                uid=9999999999999,
                return_raw=True,
            ),
            errors.UserNotFoundError,
        )

    def test_get_expired_version_by_version_uuid(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret, {'a': 1}, ttl=30)

            with TimeMock(offset=50):
                self.assertResponseEqual(
                    self.client.get_version(version_1, return_raw=True),
                    {
                        'status': 'warning',
                        'version': {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'expired': True,
                            'expired_at': 1445385645.0,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret,
                            'value': [{'key': 'a', 'value': '1'}],
                            'version': version_1,
                        },
                        'warning_message': 'version is expired',
                    },
                )

    def test_get_expired_version_by_secret_uuid(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret, {'a': 1})
                    version_2 = self.client.create_secret_version(secret, {'a': 2}, ttl=100)
                    self.client.create_secret_version(secret, {'a': 3}, ttl=30)

            with TimeMock(offset=50):
                self.assertResponseEqual(
                    self.client.get_version(secret, return_raw=True),
                    {
                        'status': 'ok',
                        'version': {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'expired': False,
                            'expired_at': 1445385715.0,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret,
                            'value': [{'key': 'a', 'value': '2'}],
                            'version': version_2,
                        },
                    },
                )

            with TimeMock(offset=2000):
                self.assertResponseEqual(
                    self.client.get_version(secret, return_raw=True),
                    {
                        'status': 'ok',
                        'version': {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret,
                            'value': [{'key': 'a', 'value': '1'}],
                            'version': version_1,
                        },
                    },
                )

            with TimeMock(offset=5000):
                self.client.update_version(version_1, ttl=1)

            with TimeMock(offset=5002):
                self.assertResponseError(
                    self.client.get_version(secret, return_raw=True),
                    errors.NonexistentEntityError(SecretVersion, 'HEAD'),
                )

    def test_get_hidden_version_by_secret_uuid(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret, {'a': 1})
                    version_2 = self.client.create_secret_version(secret, {'a': 2})

                self.assertResponseEqual(
                    self.client.get_version(secret, return_raw=True),
                    {
                        'status': 'ok',
                        'version': {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret,
                            'value': [{'key': 'a', 'value': '2'}],
                            'version': version_2,
                        },
                    },
                )

                self.client.update_version(version_2, state='hidden')
                self.assertResponseEqual(
                    self.client.get_version(secret, return_raw=True),
                    {
                        'status': 'ok',
                        'version': {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret,
                            'value': [{'key': 'a', 'value': '1'}],
                            'version': version_1,
                        },
                    },
                )

    def test_get_secret_with_expired_versions(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': 1})
                    version_2 = self.client.create_secret_version(secret_1, {'a': 2}, ttl=1200)
                    version_3 = self.client.create_secret_version(secret_1, {'a': 3}, ttl=60)

                    self.assertDictEqual(
                        self.client.get_secret(secret_1),
                        {
                            'acl': [{
                                'created_at': 1445385615.0,
                                'created_by': 200,
                                'role_slug': 'OWNER',
                                'uid': 200,
                            }],
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'effective_role': 'OWNER',
                            'name': 'ololo-secret-1',
                            'secret_roles': [{
                                'created_at': 1445385615.0,
                                'created_by': 200,
                                'role_slug': 'OWNER',
                                'uid': 200,
                            }],
                            'secret_versions': [
                                {
                                    'created_at': 1445385615.0,
                                    'created_by': 200,
                                    'expired': False,
                                    'expired_at': 1445385675.0,
                                    'keys': ['a'],
                                    'version': version_3,
                                },
                                {
                                    'created_at': 1445385615.0,
                                    'created_by': 200,
                                    'expired': False,
                                    'expired_at': 1445386815.0,
                                    'keys': ['a'],
                                    'version': version_2,
                                },
                                {
                                    'created_at': 1445385615.0,
                                    'created_by': 200,
                                    'keys': ['a'],
                                    'version': version_1,
                                },
                            ],
                            'tokens': [],
                            'updated_at': 1445385615.0,
                            'updated_by': 200,
                            'uuid': secret_1,
                        },
                    )
            with TimeMock(offset=600):
                self.assertDictEqual(
                    self.client.get_secret(secret_1),
                    {
                        'acl': [{
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'effective_role': 'OWNER',
                        'name': 'ololo-secret-1',
                        'secret_roles': [{
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'secret_versions': [
                            {
                                'created_at': 1445385615.0,
                                'created_by': 200,
                                'expired': False,
                                'expired_at': 1445386815.0,
                                'keys': ['a'],
                                'version': version_2,
                            },
                            {
                                'created_at': 1445385615.0,
                                'created_by': 200,
                                'keys': ['a'],
                                'version': version_1,
                            },
                        ],
                        'tokens': [],
                        'updated_at': 1445385615.0,
                        'updated_by': 200,
                        'uuid': secret_1,
                    },
                )

    def test_list_secrets_with_expired_versions(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    self.client.create_secret_version(secret_1, {'a': 1})
                    version_2 = self.client.create_secret_version(secret_1, {'a': 2}, ttl=1200)
                    self.client.create_secret_version(secret_1, {'a': 3}, ttl=60)

            with TimeMock(offset=600):
                self.assertListEqual(
                    self.client.list_secrets(),
                    [{
                        'acl': [{
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'effective_role': 'OWNER',
                        'last_secret_version': {'version': version_2},
                        'name': 'ololo-secret-1',
                        'secret_roles': [{
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'tokens_count': 0,
                        'updated_at': 1445385615.0,
                        'updated_by': 200,
                        'uuid': secret_1,
                        'versions_count': 2,
                    }],
                )

    def test_list_secrets_with_filter_by_appender_role(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    self.client.create_secret('ololo-secret-1')
                    secret_2 = self.client.create_secret('ololo-secret-2')
                    self.client.create_secret('ololo-secret-3')
                    secret_4 = self.client.create_secret('ololo-secret-4')

                    self.client.add_user_role_to_secret(secret_2, 'APPENDER', uid=200)
                    self.client.add_user_role_to_secret(secret_4, 'APPENDER', uid=200)

            self.assertEqual(len(self.client.list_secrets()), 4)

            filtered_secrets = self.client.list_secrets(role='APPENDER')
            self.assertEqual(len(filtered_secrets), 2)
            self.assertListEqual(
                filtered_secrets,
                [{u'acl': [{u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'OWNER',
                            u'uid': 200},
                           {u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'APPENDER',
                            u'uid': 200}],
                  u'created_at': 1445385615.0,
                  u'created_by': 200,
                  u'effective_role': u'OWNER',
                  u'name': u'ololo-secret-2',
                  u'secret_roles': [{u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'OWNER',
                                     u'uid': 200},
                                    {u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'APPENDER',
                                     u'uid': 200}],
                  u'tokens_count': 0,
                  u'updated_at': 1445385615.0,
                  u'updated_by': 200,
                  u'uuid': secret_2,
                  u'versions_count': 0},
                 {u'acl': [{u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'OWNER',
                            u'uid': 200},
                           {u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'APPENDER',
                            u'uid': 200}],
                  u'created_at': 1445385615.0,
                  u'created_by': 200,
                  u'effective_role': u'OWNER',
                  u'name': u'ololo-secret-4',
                  u'secret_roles': [{u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'OWNER',
                                     u'uid': 200},
                                    {u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'APPENDER',
                                     u'uid': 200}],
                  u'tokens_count': 0,
                  u'updated_at': 1445385615.0,
                  u'updated_by': 200,
                  u'uuid': secret_4,
                  u'versions_count': 0}]
            )

    def test_list_secret_with_hidden_secrets(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    secret_2 = self.client.create_secret('ololo-secret-2')
                    secret_3 = self.client.create_secret('ololo-secret-3')
                    secret_4 = self.client.create_secret('ololo-secret-4')
                    self.client.update_secret(secret_3, state='hidden')

            self.assertEqual(len(self.client.list_secrets()), 3)

            filtered_secrets = self.client.list_secrets(with_hidden_secrets=True)
            self.assertEqual(len(filtered_secrets), 4)
            self.assertListEqual(
                filtered_secrets,
                [{u'acl': [{u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'OWNER',
                            u'uid': 200}],
                  u'created_at': 1445385615.0,
                  u'created_by': 200,
                  u'effective_role': u'OWNER',
                  u'name': u'ololo-secret-1',
                  u'secret_roles': [{u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'OWNER',
                                     u'uid': 200}],
                  u'state_name': u'normal',
                  u'tokens_count': 0,
                  u'updated_at': 1445385615.0,
                  u'updated_by': 200,
                  u'uuid': secret_1,
                  u'versions_count': 0},
                 {u'acl': [{u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'OWNER',
                            u'uid': 200}],
                  u'created_at': 1445385615.0,
                  u'created_by': 200,
                  u'effective_role': u'OWNER',
                  u'name': u'ololo-secret-2',
                  u'secret_roles': [{u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'OWNER',
                                     u'uid': 200}],
                  u'state_name': u'normal',
                  u'tokens_count': 0,
                  u'updated_at': 1445385615.0,
                  u'updated_by': 200,
                  u'uuid': secret_2,
                  u'versions_count': 0},
                 {u'acl': [{u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'OWNER',
                            u'uid': 200}],
                  u'created_at': 1445385615.0,
                  u'created_by': 200,
                  u'effective_role': u'OWNER',
                  u'name': u'ololo-secret-3',
                  u'secret_roles': [{u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'OWNER',
                                     u'uid': 200}],
                  u'state_name': u'hidden',
                  u'tokens_count': 0,
                  u'updated_at': 1445385615.0,
                  u'updated_by': 200,
                  u'uuid': secret_3,
                  u'versions_count': 0},
                 {u'acl': [{u'created_at': 1445385615.0,
                            u'created_by': 200,
                            u'role_slug': u'OWNER',
                            u'uid': 200}],
                  u'created_at': 1445385615.0,
                  u'created_by': 200,
                  u'effective_role': u'OWNER',
                  u'name': u'ololo-secret-4',
                  u'secret_roles': [{u'created_at': 1445385615.0,
                                     u'created_by': 200,
                                     u'role_slug': u'OWNER',
                                     u'uid': 200}],
                  u'state_name': u'normal',
                  u'tokens_count': 0,
                  u'updated_at': 1445385615.0,
                  u'updated_by': 200,
                  u'uuid': secret_4,
                  u'versions_count': 0}]
            )

    def test_get_unaccesed_removed_secret(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            self.client.update_secret(secret, state='hidden')

        with PermissionsMock(uid=101):
            r = self.client.get_secret(secret, return_raw=True)
            self.assertResponseError(
                r,
                errors.AccessError(secret_state_name='hidden'),
            )

    def test_get_secret_with_value_key(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo')
                    version_1 = self.client.create_secret_version(
                        secret,
                        value={'value': 'blah-blah-blah'},
                    )
                    version_2 = self.client.create_diff_version(
                        version_1,
                        diff=[{'key': 'new_key', 'value': 'password'}],
                    )

                    r = self.client.get_version(version_2)
                    self.assertDictEqual(
                        r,
                        {
                            'created_at': 1445385615.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'parent_version_uuid': 'ver-0000000000000000000001x142',
                            'secret_name': 'ololo',
                            'secret_uuid': 'sec-0000000000000000000001x140',
                            'value': {
                                'new_key': 'password',
                                'value': 'blah-blah-blah',
                            },
                            'version': 'ver-0000000000000000000001x143',
                        }
                    )

                    r = self.client.get_secret(secret)
                    self.assertListEqual(
                        r['secret_versions'],
                        [
                            {
                                u'created_at': 1445385615.0,
                                u'created_by': 100,
                                u'creator_login': u'vault-test-100',
                                u'keys': [u'new_key', 'value'],
                                u'parent_diff_keys': {
                                    u'added': [u'new_key'],
                                    u'changed': [],
                                    u'removed': [],
                                },
                                u'parent_version_uuid': u'ver-0000000000000000000001x142',
                                u'version': u'ver-0000000000000000000001x143',
                            },
                            {
                                u'created_at': 1445385615.0,
                                u'created_by': 100,
                                u'creator_login': u'vault-test-100',
                                u'keys': ['value'],
                                u'version': u'ver-0000000000000000000001x142',
                            }
                        ]
                    )

    def test_calculate_effective_role(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('tro-lo-lo')
            self.client.add_user_role_to_secret(secret, 'APPENDER', uid=101)

        with PermissionsMock(uid=101):
            self.assertEqual(
                self.client.get_secret(secret)['effective_role'],
                'APPENDER',
            )

        with PermissionsMock(uid=100):
            self.client.add_user_role_to_secret(secret, 'READER', uid=101)

        with PermissionsMock(uid=101):
            self.assertEqual(
                self.client.get_secret(secret)['effective_role'],
                'READER',
            )

        with PermissionsMock(uid=100):
            self.client.add_user_role_to_secret(secret, 'OWNER', uid=101)

        with PermissionsMock(uid=101):
            self.assertEqual(
                self.client.get_secret(secret)['effective_role'],
                'OWNER',
            )

        with PermissionsMock(uid=100):
            self.client.add_user_role_to_secret(secret, 'APPENDER', uid=100)
            self.assertEqual(
                self.client.get_secret(secret)['effective_role'],
                'OWNER',
            )

    def test_list_secrets_with_tvm_apps(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=100):
                with UuidMock(base_value=7000000):
                    for i in range(15):
                        self.client.create_token(
                            'sec-0000000000000000000000ygj5',
                            tvm_client_id=2000367,
                        )
                        self.client.create_token(
                            'sec-0000000000000000000000ygj0',
                            tvm_client_id=2000355,
                        )
                        self.client.create_token(
                            'sec-0000000000000000000000ygj5',
                            tvm_client_id=2000355,
                        )
                        self.client.create_token(
                            'sec-0000000000000000000000ygj5',
                        )
                        self.client.create_token(
                            'sec-0000000000000000000000ygj0',
                        )
                        self.client.create_token(
                            'sec-0000000000000000000000ygj0',
                            tvm_client_id=1,
                        )

            r = self.client.list_secrets(
                with_tvm_apps=True,
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                u'page': 0,
                u'page_size': 50,
                u'secrets': [{u'acl': [{u'created_at': 1445385604.0,
                                        u'created_by': 100,
                                        u'creator_login': u'vault-test-100',
                                        u'login': u'vault-test-100',
                                        u'role_slug': u'OWNER',
                                        u'uid': 100}],
                              u'created_at': 1445385604.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'effective_role': u'OWNER',
                              u'last_secret_version': {u'version': u'ver-0000000000000000000000ygja'},
                              u'name': u'secret_2',
                              u'secret_roles': [{u'created_at': 1445385604.0,
                                                 u'created_by': 100,
                                                 u'creator_login': u'vault-test-100',
                                                 u'login': u'vault-test-100',
                                                 u'role_slug': u'OWNER',
                                                 u'uid': 100}],
                              u'tokens_count': 45,
                              u'tvm_apps': [{u'abc_department': {u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                                                 u'id': 14,
                                                                 u'unique_name': u'passp'},
                                             u'abc_state': u'granted',
                                             u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                             u'name': u'passport_likers3',
                                             u'tvm_client_id': 2000355},
                                            {u'abc_department': {u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                                                 u'id': 14,
                                                                 u'unique_name': u'passp'},
                                             u'abc_state': u'granted',
                                             u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                             u'name': u'social api (dev)',
                                             u'tvm_client_id': 2000367}],
                              u'updated_at': 1445385608.0,
                              u'updated_by': 100,
                              u'uuid': u'sec-0000000000000000000000ygj5',
                              u'versions_count': 4},
                             {u'acl': [{u'created_at': 1445385600.0,
                                        u'created_by': 100,
                                        u'creator_login': u'vault-test-100',
                                        u'login': u'vault-test-100',
                                        u'role_slug': u'OWNER',
                                        u'uid': 100}],
                              u'created_at': 1445385600.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'effective_role': u'OWNER',
                              u'last_secret_version': {u'version': u'ver-0000000000000000000000ygj4'},
                              u'name': u'secret_1',
                              u'secret_roles': [{u'created_at': 1445385600.0,
                                                 u'created_by': 100,
                                                 u'creator_login': u'vault-test-100',
                                                 u'login': u'vault-test-100',
                                                 u'role_slug': u'OWNER',
                                                 u'uid': 100}],
                              u'tokens_count': 45,
                              u'tvm_apps': [{u'abc_department': {u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                                                 u'id': 14,
                                                                 u'unique_name': u'passp'},
                                             u'abc_state': u'granted',
                                             u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
                                             u'name': u'passport_likers3',
                                             u'tvm_client_id': 2000355}],
                              u'updated_at': 1445385603.0,
                              u'updated_by': 100,
                              u'uuid': u'sec-0000000000000000000000ygj0',
                              u'versions_count': 3}],
                u'status': u'ok'
            })


class TestSearchSecrets(BaseTestClass):
    fill_database = False
    fill_staff = True
    fill_grants = True
    send_user_ticket = True

    DEFAULT_UID = 1120000000038274

    def _build_secrets(self):
        with TimeMock(incrementing=True):
            with UuidMock():
                with PermissionsMock(uid=self.DEFAULT_UID):
                    self.secret_1 = self.client.create_secret(
                        name='backend',
                        comment='secret for top backend secret service',
                    )
                    self.client.create_secret_version(
                        self.secret_1,
                        value={'test': 'ololo'},
                    )

                    self.hidden_secret = self.client.create_secret(
                        name='backend_hidden',
                        comment='secret for top backend secret service',
                    )
                    self.client.create_secret_version(
                        self.hidden_secret,
                        value={'test': 'ololo'},
                    )
                    self.client.update_secret(self.hidden_secret, state='hidden')

                    self.client.create_secret(
                        name='redis',
                        comment='redis in the sky (backend)',
                    )
                    self.client.create_secret(
                        name='password',
                        comment='my yandex password',
                    )
                    self.secret_2 = self.client.create_secret(
                        name='secret_and_version',
                        comment='secret with version',
                    )
                    self.version_2 = self.client.create_secret_version(
                        self.secret_2,
                        value={'test': 'ololo'},
                    )
                with PermissionsMock(uid=100):
                    self.secret_3 = self.client.create_secret(
                        name='lol-secret',
                        comment=u'secret for секретный service',
                    )
                    self.secret_4 = self.client.create_secret(
                        name='lol-secret-1',
                        comment=u'secret for секретный service',
                    )
                    self.client.add_user_role_to_secret(self.secret_3, role='reader', uid=1120000000038274)

    def assertSearchResponseOk(self, response, expected):
        self.assertListEqual(
            sorted(map(lambda x: x['name'], response)),
            sorted(expected),
        )

    def test_default_search(self):
        self._build_secrets()

        with PermissionsMock(uid=self.DEFAULT_UID):
            self.assertSearchResponseOk(
                self.client.list_secrets(),
                ['lol-secret', 'secret_and_version', 'password', 'redis', 'backend'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='back'),
                ['redis', 'backend'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='back', with_hidden_secrets=True),
                ['redis', 'backend', 'backend_hidden'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='end'),
                ['redis', 'backend'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='redis'),
                ['redis'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query=u'секретный'),
                ['lol-secret'],
            )

            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format(self.secret_2)),
                ['secret_and_version'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format(self.version_2)),
                ['secret_and_version'],
            )

            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format(self.secret_2[4:])),
                ['secret_and_version'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format(self.version_2[4:])),
                ['secret_and_version'],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format(self.version_2[3:])),
                ['secret_and_version'],
            )

            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format('sec-1234567890')),
                [],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format('ver-1234567890')),
                [],
            )
            self.assertSearchResponseOk(
                self.client.list_secrets(query='  {}  '.format(self.secret_4)),
                [],
            )

    def test_exact_search(self):
        self._build_secrets()

        with PermissionsMock(uid=self.DEFAULT_UID):
            self.assertSearchResponseOk(
                self.client.list_secrets(query='backend', query_type='exact'),
                ['backend'],
            )

            self.assertSearchResponseOk(
                self.client.list_secrets(query='secret with version', query_type='exact'),
                ['secret_and_version'],
            )

    def test_prefix_search(self):
        self._build_secrets()

        with PermissionsMock(uid=self.DEFAULT_UID):
            self.assertSearchResponseOk(
                self.client.list_secrets(query='backend', query_type='prefix', with_hidden_secrets=True),
                ['backend', 'backend_hidden'],
            )

            self.assertSearchResponseOk(
                self.client.list_secrets(query='secret', query_type='prefix'),
                ['backend', 'lol-secret', 'secret_and_version'],
            )

    def test_search_with_empty_query(self):
        self._build_secrets()

        with PermissionsMock(uid=self.DEFAULT_UID):
            self.assertSearchResponseOk(
                self.client.list_secrets(query='', with_hidden_secrets=True),
                [
                    'backend',
                    'backend_hidden',
                    'lol-secret',
                    'password',
                    'redis',
                    'secret_and_version',
                ],
            )

    def test_search_logging(self):
        with PermissionsMock(uid=100):
            with LoggingMock() as logging_mock:
                self.client.list_secrets(
                    query='text',
                    yours='true',
                    role='READER',
                    tags='one, two, three',
                )
                self.assertListEqual(
                    logging_mock.getLogger('statbox').entries,
                    [({'action': 'enter',
                       'auth_type': 'user_ticket',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 1,
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'mode': 'list_secrets',
                       'tvm_grants': 'granted',
                       'auth_uid': 100},
                      'INFO', None, None,),
                     ({'action': 'success',
                       'auth_type': 'user_ticket',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 1,
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'form_asc': False,
                       'form_order_by': 'created_at',
                       'form_page': 0,
                       'form_page_size': 50,
                       'form_query': u'text',
                       'form_query_type': 'infix',
                       'form_role': u'READER',
                       'form_tags': [u'one', u'two', u'three'],
                       'form_with_hidden_secrets': False,
                       'form_with_tvm_apps': False,
                       'form_without': '',
                       'form_yours': True,
                       'mode': 'list_secrets',
                       'results_count': 0,
                       'tvm_grants': 'granted',
                       'auth_uid': 100},
                      'INFO', None, None,),
                     ({'action': 'exit',
                       'auth_type': 'user_ticket',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 1,
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'mode': 'list_secrets',
                       'tvm_grants': 'granted',
                       'auth_uid': 100},
                      'INFO', None, None,)]
                )


class TestMutableSecretsView(BaseTestClass):
    fill_database = False
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestMutableSecretsView, self).setUp()
        self.fixture.add_user(uid=200)

    def test_correct_name(self):
        with PermissionsMock(uid=200):
            with TimeMock(incrementing=True):
                with UuidMock():
                    r = self.client.create_secret('ABC-abc-1_2', return_raw=True)

            self.assertResponseEqual(r, {
                'uuid': 'sec-0000000000000000000000ygj0',
                'status': 'ok',
            })

    def test_diff_secret(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')

                with LoggingMock() as logging_mock:
                    version_1 = self.client.create_secret_version(
                        secret,
                        value={
                            'password': '123456',
                            'pazzword': '654321',
                        },
                    )
                    self.assertListEqual(
                        logging_mock.getLogger('statbox').entries,
                        [({'action': 'enter',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'mode': 'create_secret_version',
                           'tvm_grants': 'granted',
                           'auth_uid': 200},
                          'INFO', None, None,),
                         ({'action': 'success',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'expired_at': None,
                           'mode': 'create_secret_version',
                           'tvm_grants': 'granted',
                           'auth_uid': 200,
                           'version_uuid': version_1},
                          'INFO', None, None,),
                         ({'action': 'exit',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'tvm_grants': 'granted',
                           'mode': 'create_secret_version',
                           'auth_uid': 200},
                          'INFO', None, None,)]
                    )

                with LoggingMock() as logging_mock:
                    response = self.client.create_diff_version(
                        version_1,
                        [{
                            'key': 'login',
                            'value': 'pasha',
                        }, {
                            'key': 'pazzword',
                        }],
                        comment='fix some fields',
                        return_raw=True,
                    ).json()

                version_2 = response.get('version')
                self.assertListEqual(
                    logging_mock.getLogger('statbox').entries,
                    [({'action': 'enter',
                       'auth_type': 'user_ticket',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 1,
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'mode': 'create_diff_version',
                       'tvm_grants': 'granted',
                       'auth_uid': 200},
                      'INFO', None, None,),
                     ({'action': 'success',
                       'auth_type': 'user_ticket',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 1,
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'expired_at': None,
                       'mode': 'create_diff_version',
                       'parent_version_uuid': version_1,
                       'tvm_grants': 'granted',
                       'auth_uid': 200,
                       'version_uuid': version_2},
                      'INFO', None, None,),
                     ({'action': 'exit',
                       'auth_type': 'user_ticket',
                       'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                       'auth_tvm_app_id': 1,
                       'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                       'mode': 'create_diff_version',
                       'tvm_grants': 'granted',
                       'auth_uid': 200},
                      'INFO', None, None,)]
                )

                self.assertDictEqual(
                    response,
                    {
                        'status': 'ok',
                        'parent_diff_keys': {
                            'added': ['login'],
                            'changed': [],
                            'removed': ['pazzword'],
                        },
                        'parent_version_uuid': version_1,
                        'secret_uuid': secret,
                        'version': version_2,
                    },
                )
                self.assertDictEqual(
                    self.client.get_version(version_2),
                    {
                        'comment': 'fix some fields',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret',
                        'secret_uuid': secret,
                        'value': {
                            'login': 'pasha',
                            'password': '123456',
                        },
                        'version': version_2,
                        'parent_version_uuid': version_1,
                    },
                )

    def test_diff_secret_delete_nonexistent_key_error(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')
                version_1 = self.client.create_secret_version(
                    secret,
                    value={
                        'password': '123456',
                        'pazzword': '654321',
                    },
                )
                response = self.client.create_diff_version(
                    version_1,
                    [{
                        'key': 'login',
                        'value': 'pasha',
                    }, {
                        'key': 'paZZword',
                    }],
                    comment='fix some fields',
                    return_raw=True,
                )
                self.assertResponseError(
                    response,
                    errors.ValidationError({
                        'diff': [{'index': 1, 'paZZword': ['not_exists']}],
                    }),
                )

    def test_diff_secret_delete_all_keys_error(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')
                version_1 = self.client.create_secret_version(
                    secret,
                    value={
                        'password': '123456',
                        'pazzword': '654321',
                    },
                )
                self.assertResponseError(
                    self.client.create_diff_version(
                        version_1,
                        [{
                            'key': 'password',
                        }, {
                            'key': 'pazzword',
                        }],
                        comment='fix some fields',
                        return_raw=True,
                    ),
                    errors.EmptyDiffSecretVersionError(),
                )

    def test_create_version_with_empty_value(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret')
                    self.client.create_secret_version(
                        secret,
                        value=[
                            {
                                'key': 'login',
                                'value': b64encode('pasha'),
                                'encoding': 'base64',
                            }, {
                                'key': 'password',
                                'value': '',
                                'encoding': '',
                            },
                        ],
                    )
                    self.assertDictEqual(
                        self.client.get_version(secret, packed_value=False),
                        {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'secret_name': 'ololo-secret',
                            'secret_uuid': 'sec-0000000000000000000001x140',
                            'value': [{
                                'encoding': 'base64',
                                'key': 'login',
                                'value': b64encode('pasha'),
                            }, {
                                'key': 'password',
                                'value': '',
                            }],
                            'version': 'ver-0000000000000000000001x142',
                        },
                    )

    def test_create_version_with_encoding_ok(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret')
                    self.client.create_secret_version(
                        secret,
                        value=[
                            {
                                'key': 'login',
                                'value': b64encode('pasha'),
                                'encoding': 'base64',
                            }, {
                                'key': 'comment',
                                'value': '',
                                'encoding': 'base64',
                            }, {
                                'key': 'password',
                                'value': '123456',
                                'encoding': '',
                            },
                        ],
                    )
                    self.assertDictEqual(
                        self.client.get_version(secret, packed_value=False),
                        {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'secret_name': 'ololo-secret',
                            'secret_uuid': 'sec-0000000000000000000001x140',
                            'value': [
                                {'encoding': 'base64', 'key': 'login', 'value': b64encode('pasha')},
                                {'encoding': 'base64', 'key': 'comment', 'value': ''},
                                {'key': 'password', 'value': '123456'},
                            ],
                            'version': 'ver-0000000000000000000001x142',
                        },
                    )

    def test_create_version_with_encoding_fail(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret')
                    self.assertResponseError(
                        self.client.create_secret_version(
                            secret,
                            value=[
                                {'key': 'login', 'value': 'pasha'},
                                {'key': 'password', 'value': '123456', 'encoding': 'base64'},
                            ],
                            return_raw=True,
                        ),
                        errors.ValidationError({
                            u'value': [{u'index': 1, u'password': [u'invalid_base64']}],
                        }),
                    )
                    self.assertResponseError(
                        self.client.create_secret_version(
                            secret,
                            value=[
                                {'key': 'login', 'value': 'pasha'},
                                {'key': 'password', 'value': b64encode('Padded val').strip('='), 'encoding': 'base64'},
                            ],
                            return_raw=True,
                        ),
                        errors.ValidationError({
                            u'value': [{u'index': 1, u'password': [u'invalid_base64']}],
                        }),
                    )

    def test_create_diff_version_with_encoding_ok(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')
                version_1 = self.client.create_secret_version(
                    secret,
                    value=[
                        {'key': 'password', 'value': b64encode('123456'), 'encoding': 'base64'},
                        {'key': 'pazzword', 'value': '654321'},
                        {'key': 'hostname', 'value': b64encode('yandex-team.ru'), 'encoding': 'base64'},
                    ],
                )
                response = self.client.create_diff_version(
                    version_1,
                    [{
                        'key': 'login',
                        'value': b64encode('pasha'),
                        'encoding': 'base64',
                    }, {
                        'key': 'pazzword',
                        'encoding': 'base64',
                    }, {
                        'key': 'hostname',
                        'value': 'yandex-team.ru',
                    }],
                    comment='fix some fields',
                    return_raw=True,
                ).json()
                version_2 = response.get('version')
                self.assertDictEqual(
                    self.client.get_version(version_2, packed_value=False),
                    {
                        'comment': 'fix some fields',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret',
                        'secret_uuid': secret,
                        'value': [
                            {'encoding': 'base64', 'key': 'login', 'value': b64encode('pasha')},
                            {'encoding': 'base64', 'key': 'password', 'value': b64encode('123456')},
                            {'key': 'hostname', 'value': 'yandex-team.ru'},
                        ],
                        'version': version_2,
                        'parent_version_uuid': version_1,
                    },
                )

    def test_create_diff_version_with_encoding_fail(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')
                version_1 = self.client.create_secret_version(
                    secret,
                    value=[
                        {'key': 'password', 'value': b64encode('123456'), 'encoding': 'base64'},
                        {'key': 'pazzword', 'value': '654321'},
                        {'key': 'hostname', 'value': b64encode('yandex-team.ru'), 'encoding': 'base64'},
                    ],
                )
                self.assertResponseError(
                    self.client.create_diff_version(
                        version_1,
                        [{
                            'key': 'hostname',
                            'value': 'yandex-team.ru',
                        }, {
                            'key': 'password',
                            'value': '54321',
                            'encoding': 'base64',
                        }, ],
                        return_raw=True,
                    ),
                    errors.ValidationError(
                        errors={u'diff': [{u'index': 1, u'password': [u'invalid_base64']}]},
                    ),
                )

    def test_create_diff_version_with_check_head(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret = self.client.create_secret('ololo-secret')
                version_1 = self.client.create_secret_version(
                    secret,
                    value={'password': '12345'},
                )

                self.client.update_version(version_1, state='hidden')
                self.assertResponseError(
                    self.client.create_diff_version(
                        version_1,
                        diff=[{'key': 'login', 'value': 'pasha'}],
                        check_head=True,
                        return_raw=True,
                    ),
                    errors.HeadVersionNotFoundError(),
                )
                self.client.update_version(version_1, state='normal')

                self.client.update_version(version_1, ttl=10)
                with TimeMock(offset=100):
                    self.assertResponseError(
                        self.client.create_diff_version(
                            version_1,
                            diff=[{'key': 'login', 'value': 'pasha'}],
                            check_head=True,
                            return_raw=True,
                        ),
                        errors.HeadVersionNotFoundError(),
                    )
                self.client.update_version(version_1, ttl=0)

                version_2 = self.client.create_secret_version(secret, {'password': '654321'})
                self.assertResponseError(
                    self.client.create_diff_version(
                        version_1,
                        diff=[{'key': 'login', 'value': 'pasha'}],
                        check_head=True,
                        return_raw=True,
                    ),
                    errors.SecretHasNewHeadVersionError(),
                )

                self.client.create_secret_version(secret, {'password': '654321'}, ttl=1)
                hidden_version = self.client.create_secret_version(secret, {'password': '654321'})
                self.client.update_version(hidden_version, state='hidden')

                with TimeMock(offset=100):
                    with UuidMock(base_value=450000):
                        self.assertResponseEqual(
                            self.client.create_diff_version(
                                version_2,
                                diff=[{'key': 'login', 'value': 'pasha'}],
                                check_head=True,
                                return_raw=True,
                            ),
                            {
                                'parent_diff_keys': {'added': ['login'], 'changed': [], 'removed': []},
                                'parent_version_uuid': version_2,
                                'secret_uuid': secret,
                                'status': 'ok',
                                'version': 'ver-0000000000000000000000dqeg',
                            },
                        )

    def test_create_secret_with_invalid_encoding_error(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret = self.client.create_secret('ololo-secret')
                    self.assertResponseError(
                        self.client.create_secret_version(
                            secret,
                            return_raw=True,
                            value=[
                                {
                                    'key': 'login',
                                    'value': 'pasha',
                                    'encoding': 'base32',
                                }, {
                                    'key': 'password',
                                    'value': '123456',
                                },
                            ],
                        ),
                        errors.ValidationError({
                            'value': [{'encoding': ["any_of: ['base64']"], 'index': 0}],
                        }),
                    )

    def test_hide_secret(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': 1})
                    self.client.update_secret(secret_1, state='hidden')
                    self.assertListEqual(self.client.list_secrets(), [])
                    self.assertEqual(
                        self.client.get_secret(secret_1, return_raw=True).json()['status'],
                        'warning',
                    )
                    self.assertEqual(
                        self.client.get_version(version_1, return_raw=True).json()['status'],
                        'warning',
                    )
                    self.client.update_secret(secret_1, state='normal')
                    self.assertListEqual(self.client.list_secrets(), [{
                        'acl': [{
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'effective_role': 'OWNER',
                        'last_secret_version': {'version': version_1},
                        'name': 'ololo-secret-1',
                        'secret_roles': [{
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'tokens_count': 0,
                        'updated_at': 1445385615.0,
                        'updated_by': 200,
                        'uuid': secret_1,
                        'versions_count': 1,
                    }])

    def test_hide_version(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': 1})
                    version_2 = self.client.create_secret_version(secret_1, {'b': 1})
                    self.assertEqual(
                        len(self.client.get_secret(secret_1)['secret_versions']),
                        2,
                    )
                    self.client.update_version(version_2, state='hidden')
                    self.assertEqual(
                        len(self.client.get_secret(secret_1)['secret_versions']),
                        1,
                    )
                    self.assertEqual(
                        self.client.list_secrets()[0]['last_secret_version']['version'],
                        version_1,
                    )
                    self.assertEqual(
                        self.client.get_version(version_2, return_raw=True).json()['status'],
                        'warning',
                    )
                    self.client.update_version(version_2, state='normal')
                    self.assertEqual(
                        len(self.client.get_secret(secret_1)['secret_versions']),
                        2,
                    )

                    with LoggingMock() as logging_mock:
                        self.client.update_version(secret_1, state='hidden')
                        self.assertListEqual(
                            logging_mock.getLogger('statbox').entries,
                            [({'action': 'enter',
                               'auth_type': 'user_ticket',
                               'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                               'auth_tvm_app_id': 1,
                               'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                               'mode': 'update_version',
                               'tvm_grants': 'granted',
                               'auth_uid': 200},
                              'INFO', None, None,),
                             ({'action': 'get',
                               'auth_type': 'user_ticket',
                               'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                               'auth_tvm_app_id': 1,
                               'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                               'expired_at': None,
                               'mode': 'update_version',
                               'state': 'normal',
                               'tvm_grants': 'granted',
                               'auth_uid': 200,
                               'version_prefix': u'sec',
                               'version_uuid': secret_1},
                              'INFO', None, None,),
                             ({'action': 'success',
                               'auth_type': 'user_ticket',
                               'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                               'auth_tvm_app_id': 1,
                               'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                               'comment': None,
                               'expired_at': None,
                               'mode': 'update_version',
                               'state': 'hidden',
                               'tvm_grants': 'granted',
                               'auth_uid': 200,
                               'version_uuid': version_2},
                              'INFO', None, None,),
                             ({'action': 'exit',
                               'auth_type': 'user_ticket',
                               'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                               'auth_tvm_app_id': 1,
                               'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                               'mode': 'update_version',
                               'tvm_grants': 'granted',
                               'auth_uid': 200},
                              'INFO', None, None,)]

                        )

                    self.assertEqual(
                        len(self.client.get_secret(secret_1)['secret_versions']),
                        1,
                    )

                    self.assertEqual(
                        self.client.list_secrets()[0]['last_secret_version']['version'],
                        version_1,
                    )
                    self.client.update_secret(secret_1, state='hidden')
                    self.assertEqual(
                        self.client.get_version(version_1, return_raw=True).json()['status'],
                        'warning',
                    )

    def test_get_head_version(self):
        with PermissionsMock(uid=200):
            with TimeMock() as time_mock:
                secret = self.client.create_secret(
                    name='ololo.secret',
                )
                version_1 = self.client.create_secret_version(
                    secret_uuid=secret,
                    value={'password.1': '123456'},
                )
                time_mock.tick()
                version_2 = self.client.create_diff_version(
                    parent_version_uuid=version_1,
                    diff=[{'key': 'username', 'value': 'pasha'}],
                )
                head = self.client.get_version(
                    version=secret,
                )
                self.assertDictEqual(head, {
                    'created_at': 1445385601.0,
                    'created_by': 200,
                    'secret_name': 'ololo.secret',
                    'value': {'password.1': '123456', 'username': 'pasha'},
                    'version': version_2,
                    'secret_uuid': secret,
                    'parent_version_uuid': version_1,
                })

    def test_incorrect_name(self):
        with PermissionsMock(uid=200):
            with TimeMock(incrementing=True):
                with UuidMock():
                    r1 = self.client.create_secret('secret@111)(', return_raw=True)

            self.assertResponseError(
                r1,
                errors.ValidationError({
                    'name': ['regexp: ^[a-zA-Z0-9_\\-\\.]+$'],
                }),
            )
            r2 = self.client.list_secrets()
            self.assertListEqual(r2, [])

    def test_incorrect_keys(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                secret_uuid = self.client.create_secret('secret-1')
                r = self.client.create_secret_version(
                    secret_uuid=secret_uuid,
                    value={'@d*.': '123'},
                    return_raw=True,
                )
                self.assertResponseError(
                    r,
                    errors.ValidationError({
                        'value': [{
                            'key': ['regexp: ^[a-zA-Z0-9_\\-\\.]+$'],
                            'index': 0,
                        }],
                    }),
                )
                r = self.client.create_secret_version(
                    secret_uuid=secret_uuid,
                    value={'a@@': '123', '': '567', 'key1,key2': '90'},
                    return_raw=True,
                )
                self.assertResponseError(
                    r,
                    errors.ValidationError({
                        'value': [{
                            'key': ['required'],
                            'index': 0,
                        }, {
                            'key': ['regexp: ^[a-zA-Z0-9_\\-\\.]+$'],
                            'index': 1,
                        }, {
                            'key': ['regexp: ^[a-zA-Z0-9_\\-\\.]+$'],
                            'index': 2,
                        }],
                    }),
                )
                secret_version = self.client.create_secret_version(
                    secret_uuid=secret_uuid,
                    value={'login': 'pepe'},
                )
                r = self.client.create_diff_version(
                    parent_version_uuid=secret_version,
                    diff=[{'key': 'login'}, {'key': 'key1,key2', 'value': 'vvvvv'}],
                    return_raw=True,
                )
                self.assertResponseError(
                    r,
                    errors.ValidationError({
                        'diff': [{
                            'key': ['regexp: ^[a-zA-Z0-9_\\-\\.]+$'],
                            'index': 1,
                        }],
                    }),
                )
                r = self.client.create_secret_version(
                    secret_uuid=secret_uuid,
                    value=[{'key': '123'}],
                    return_raw=True,
                )
                self.assertResponseError(
                    r,
                    errors.ValidationError({
                        'value': [{
                            'value': ['required'],
                            'index': 0,
                        }],
                    }),
                )

    def test_incorrect_name_in_update(self):
        with PermissionsMock(uid=200):
            with TimeMock() as time_mock:
                with UuidMock():
                    uuid = self.client.create_secret('secret')
                    time_mock.tick()
                    r1 = self.client.update_secret(uuid, name='secret@111)(', return_raw=True)
                    time_mock.tick()

            self.assertResponseError(
                r1,
                errors.ValidationError({
                    'name': ['regexp: ^[a-zA-Z0-9_\\-\\.]+$'],
                }),
            )
            r2 = self.client.list_secrets()
            self.assertListEqual(r2, [{
                'acl': [{
                    'role_slug': 'OWNER',
                    'uid': 200,
                    'created_at': 1445385600,
                    'created_by': 200,
                }],
                'effective_role': 'OWNER',
                'created_at': 1445385600,
                'created_by': 200,
                'name': 'secret',
                'secret_roles': [{
                    'role_slug': 'OWNER',
                    'uid': 200,
                    'created_at': 1445385600,
                    'created_by': 200,
                }],
                'updated_at': 1445385600,
                'updated_by': 200,
                'uuid': 'sec-0000000000000000000000ygj0',
                'versions_count': 0,
                'tokens_count': 0,
            }])

    def test_create_secret_version_errors(self):
        with PermissionsMock(uid=200):
            nonexistent_secret_uuid = '00000000000000000000000000'
            r = self.client.create_secret_version(
                nonexistent_secret_uuid,
                {'password': 'keke'},
                return_raw=True,
            )
            self.assertResponseError(r, errors.AccessError)

    def test_update_secret(self):
        with PermissionsMock(uid=200):
            with TimeMock() as time_mock:
                with UuidMock():
                    secret_uuid = self.client.create_secret(
                        name='lol-secret',
                        comment='secret for top secret service',
                    )
                    time_mock.tick()

                r1 = self.client.get_secret(secret_uuid)
                self.assertDictEqual(r1, {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 200,
                        'created_at': 1445385600,
                        'created_by': 200,
                    }],
                    'effective_role': 'OWNER',
                    'comment': 'secret for top secret service',
                    'created_at': 1445385600,
                    'created_by': 200,
                    'name': 'lol-secret',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 200,
                        'created_at': 1445385600,
                        'created_by': 200,
                    }],
                    'secret_versions': [],
                    'tokens': [],
                    'updated_at': 1445385600,
                    'updated_by': 200,
                    'uuid': 'sec-0000000000000000000000ygj0',
                })

                with LoggingMock() as logging_mock:
                    self.client.update_secret(secret_uuid, name='lol-secret-1')
                    self.assertListEqual(
                        logging_mock.getLogger('statbox').entries,
                        [({'action': 'enter',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'mode': 'update_secret',
                           'tvm_grants': 'granted',
                           'auth_uid': 200},
                          'INFO', None, None,),
                         ({'action': 'success',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'created_by': 200,
                           'mode': 'update_secret',
                           'name': u'lol-secret-1',
                           'secret_uuid': 'sec-0000000000000000000000ygj0',
                           'state': 'normal',
                           'tvm_grants': 'granted',
                           'auth_uid': 200},
                          'INFO', None, None,),
                         ({'action': 'exit',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'mode': 'update_secret',
                           'tvm_grants': 'granted',
                           'auth_uid': 200},
                          'INFO', None, None,)],
                    )

                time_mock.tick()
                r2 = self.client.get_secret(secret_uuid)
                self.assertDictEqual(r2, {
                    'acl': [{
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'role_slug': 'OWNER',
                        'uid': 200,
                    }],
                    'effective_role': 'OWNER',
                    'comment': 'secret for top secret service',
                    'created_at': 1445385600,
                    'created_by': 200,
                    'name': 'lol-secret-1',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 200,
                        'created_at': 1445385600,
                        'created_by': 200,
                    }],
                    'secret_versions': [],
                    'tokens': [],
                    'updated_at': 1445385601,
                    'updated_by': 200,
                    'uuid': 'sec-0000000000000000000000ygj0',
                })
                self.client.update_secret(
                    secret_uuid,
                    comment='secret for not so top secret service',
                )
                time_mock.tick()
                r3 = self.client.get_secret(secret_uuid)
                self.assertDictEqual(r3, {
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 200,
                        'created_at': 1445385600,
                        'created_by': 200,
                    }],
                    'effective_role': 'OWNER',
                    'comment': 'secret for not so top secret service',
                    'created_at': 1445385600,
                    'created_by': 200,
                    'name': 'lol-secret-1',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 200,
                        'created_at': 1445385600,
                        'created_by': 200,
                    }],
                    'secret_versions': [],
                    'tokens': [],
                    'updated_at': 1445385602,
                    'updated_by': 200,
                    'uuid': 'sec-0000000000000000000000ygj0',
                })

    def test_delete_secret_comment(self):
        with PermissionsMock(uid=200):
            with TimeMock() as time_mock:
                with UuidMock():
                    secret_uuid = self.client.create_secret(
                        name='lol-secret',
                        comment='secret for top secret service',
                    )
                    time_mock.tick()

                r1 = self.client.get_secret(secret_uuid)
                self.assertDictEqual(r1, {
                    'acl': [{
                        'role_slug': 'OWNER', 'uid': 200,
                        'created_at': 1445385600, 'created_by': 200,
                    }],
                    'effective_role': 'OWNER',
                    'comment': 'secret for top secret service',
                    'created_at': 1445385600,
                    'created_by': 200,
                    'name': 'lol-secret',
                    'secret_roles': [{
                        'role_slug': 'OWNER', 'uid': 200,
                        'created_at': 1445385600, 'created_by': 200,
                    }],
                    'secret_versions': [],
                    'tokens': [],
                    'updated_at': 1445385600,
                    'updated_by': 200,
                    'uuid': 'sec-0000000000000000000000ygj0',
                })
                self.client.update_secret(secret_uuid, comment='')
                time_mock.tick()
                r2 = self.client.get_secret(secret_uuid)
                self.assertDictEqual(r2, {
                    'acl': [{
                        'role_slug': 'OWNER', 'uid': 200,
                        'created_at': 1445385600, 'created_by': 200,
                    }],
                    'effective_role': 'OWNER',
                    'comment': '',
                    'created_at': 1445385600,
                    'created_by': 200,
                    'name': 'lol-secret',
                    'secret_roles': [{
                        'role_slug': 'OWNER', 'uid': 200,
                        'created_at': 1445385600, 'created_by': 200,
                    }],
                    'secret_versions': [],
                    'tokens': [],
                    'updated_at': 1445385601,
                    'updated_by': 200,
                    'uuid': 'sec-0000000000000000000000ygj0',
                })

    def test_create_version_with_ttl(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': 1}, ttl=30)
                    self.assertDictEqual(
                        self.client.get_version(version_1),
                        {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'expired_at': 1445385645.0,
                            'expired': False,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret_1,
                            'value': {'a': '1'},
                            'version': version_1,
                        },
                    )

    def test_create_diff_version_with_ttl(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': 1})
                    version_2 = self.client.create_diff_version(version_1, [{'key': 'b', 'value': 2}], ttl=30)
                    self.assertDictEqual(
                        self.client.get_version(version_2),
                        {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'expired_at': 1445385645.0,
                            'expired': False,
                            'parent_version_uuid': version_1,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret_1,
                            'value': {'a': '1', 'b': '2'},
                            'version': version_2,
                        },
                    )

    def test_change_version_ttl(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': '1'})

                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )

                self.client.update_version(version_1, ttl=30)
                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'expired': False,
                        'expired_at': 1445385645.0,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'updated_at': 1445385615.0,
                        'updated_by': 200,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )

            with PermissionsMock(uid=200):
                with TimeMock(offset=100):
                    self.client.update_version(version_1, ttl=30)
                    self.assertDictEqual(
                        self.client.get_version(version_1),
                        {
                            'created_at': 1445385615.0,
                            'created_by': 200,
                            'expired': False,
                            'expired_at': 1445385730.0,
                            'secret_name': 'ololo-secret-1',
                            'secret_uuid': secret_1,
                            'updated_at': 1445385700.0,
                            'updated_by': 200,
                            'value': {'a': '1'},
                            'version': version_1,
                        },
                    )

    def test_reset_version_ttl(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(secret_1, {'a': '1'}, ttl=30)
                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'expired': False,
                        'expired_at': 1445385645.0,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )
                self.client.update_version(version_1, ttl=0)
                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'updated_at': 1445385615.0,
                        'updated_by': 200,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )

    def test_change_version_comment(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(
                        secret_1,
                        {'a': '1'},
                        comment='Version comment',
                    )

                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'comment': 'Version comment',
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )

                self.client.update_version(version_1, comment='New version comment')
                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'comment': 'New version comment',
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'updated_at': 1445385615.0,
                        'updated_by': 200,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )

    def test_set_empty_version_comment(self):
        with PermissionsMock(uid=200):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    version_1 = self.client.create_secret_version(
                        secret_1,
                        {'a': '1'},
                        comment='Version comment',
                    )

                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'comment': 'Version comment',
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )

                self.client.update_version(version_1, comment='')
                self.assertDictEqual(
                    self.client.get_version(version_1),
                    {
                        'created_at': 1445385615.0,
                        'created_by': 200,
                        'secret_name': 'ololo-secret-1',
                        'secret_uuid': secret_1,
                        'updated_at': 1445385615.0,
                        'updated_by': 200,
                        'value': {'a': '1'},
                        'version': version_1,
                    },
                )


class TestTaggedSecretsView(BaseTestClass):
    fill_database = False
    fill_staff = True
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestTaggedSecretsView, self).setUp()
        self.fixture.add_user(uid=200)

    def fill_db(self):
        with PermissionsMock(uid=100):
            with TimeMock() as time_mock:
                with UuidMock():
                    self.client.create_secret(
                        'secret_untagged',
                        return_raw=True,
                    )
                    time_mock.tick()
                    self.client.create_secret(
                        'secret_tags_01',
                        tags=u'one, two, three, навохудоноср',
                        return_raw=True,
                    )
                    time_mock.tick()
                    self.client.create_secret(
                        'secret_tags_02',
                        tags='two, three, four, six',
                        return_raw=True,
                    )
                    time_mock.tick()
                    self.client.create_secret(
                        'secret_tags_03',
                        tags='five, seven, nine',
                        return_raw=True,
                    )

    def test_get_secrets_with_tags(self):
        self.fill_db()

        with PermissionsMock(uid=100):
            r = self.client.list_secrets(
                tags='one',
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385601.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_tags_01',
                    'secret_roles': [{
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'tags': ['one', 'three', 'two', u'навохудоноср'],
                    'updated_at': 1445385601.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj2',
                    'versions_count': 0,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })
            r = self.client.list_secrets(
                tags='one, two, three',
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385601.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_tags_01',
                    'secret_roles': [{
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'tags': ['one', 'three', 'two', u'навохудоноср'],
                    'updated_at': 1445385601.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj2',
                    'versions_count': 0,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

            r = self.client.list_secrets(
                tags='one, two, three, four, five',
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [],
                'status': 'ok',
            })

            r = self.client.list_secrets(
                tags='two, three',
                return_raw=True,
            )
            self.assertResponseEqual(r, {
                'page': 0,
                'page_size': 50,
                'secrets': [{
                    'acl': [{
                        'created_at': 1445385602.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385602.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_tags_02',
                    'secret_roles': [{
                        'created_at': 1445385602.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'tags': ['four', 'six', 'three', 'two'],
                    'updated_at': 1445385602.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj8',
                    'versions_count': 0,
                    'tokens_count': 0,
                }, {
                    'acl': [{
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385601.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'name': 'secret_tags_01',
                    'secret_roles': [{
                        'created_at': 1445385601.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'login': 'vault-test-100',
                        'role_slug': 'OWNER',
                        'uid': 100,
                    }],
                    'tags': ['one', 'three', 'two', u'навохудоноср'],
                    'updated_at': 1445385601.0,
                    'updated_by': 100,
                    'uuid': 'sec-0000000000000000000000ygj2',
                    'versions_count': 0,
                    'tokens_count': 0,
                }],
                'status': 'ok',
            })

    def test_get_secrets_with_tags_by_full_tag_tile(self):
        """
        Фиксируем, что поск по тегам должен срабатывать только по полным тегам.
        Если искать по части, то мы сломаем внешние утилиты, которые фильтруют
        секреты по тегам при поиске.
        """
        self.fill_db()

        with PermissionsMock(uid=100):
            r = self.client.list_secrets(
                tags='худ',
                return_raw=True,
            )
            self.assertResponseEqual(
                r,
                {u'page': 0, u'page_size': 50, u'secrets': [], u'status': u'ok'}
            )

            r = self.client.list_secrets(
                tags='on',
                return_raw=True,
            )
            self.assertResponseEqual(
                r,
                {u'page': 0, u'page_size': 50, u'secrets': [], u'status': u'ok'}
            )

            r = self.client.list_secrets(
                tags='ne',
                return_raw=True,
            )
            self.assertResponseEqual(
                r,
                {u'page': 0, u'page_size': 50, u'secrets': [], u'status': u'ok'}
            )

    def test_create_secret_with_tags(self):
        with PermissionsMock(uid=200):
            with TimeMock():
                with UuidMock():
                    r1 = self.client.create_secret(
                        'ABC-abc-1_2',
                        tags='one, two, three, one, two words,without space',
                        return_raw=True,
                    )

            self.assertResponseEqual(r1, {
                'uuid': 'sec-0000000000000000000000ygj0',
                'status': 'ok',
            })

            r2 = self.client.get_secret(
                '0000000000000000000000ygj0',
                return_raw=True,
            )
            self.assertResponseEqual(r2, {
                'page': 0,
                'page_size': 50,
                'secret': {
                    'acl': [{
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'role_slug': 'OWNER',
                        'uid': 200,
                    }],
                    'effective_role': 'OWNER',
                    'created_at': 1445385600.0,
                    'created_by': 200,
                    'name': 'ABC-abc-1_2',
                    'secret_roles': [{
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'role_slug': 'OWNER',
                        'uid': 200,
                    }],
                    'secret_versions': [],
                    'tags': [
                        'one',
                        'three',
                        'two',
                        'two words',
                        'without space',
                    ],
                    'tokens': [],
                    'updated_at': 1445385600.0,
                    'updated_by': 200,
                    'uuid': 'sec-0000000000000000000000ygj0',
                },
                'status': 'ok',
            })

    def test_update_secret_with_tags(self):
        with PermissionsMock(uid=200):
            with TimeMock() as time_mock:
                with UuidMock():
                    r1 = self.client.create_secret(
                        'ABC-abc-1_2',
                        tags='one, two, three, one, two words,without space',
                        return_raw=True,
                    )

                self.assertResponseEqual(r1, {
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'status': 'ok',
                })
                time_mock.tick()
                r2 = self.client.update_secret(
                    '0000000000000000000000ygj0',
                    tags='one, two, three, five, more',
                    return_raw=True,
                )
                self.assertResponseEqual(r2, {
                    'status': 'ok',
                })

                r3 = self.client.get_secret(
                    '0000000000000000000000ygj0',
                    return_raw=True,
                )
                self.assertResponseEqual(r3, {
                    'page': 0,
                    'page_size': 50,
                    'secret': {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'effective_role': 'OWNER',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'ABC-abc-1_2',
                        'secret_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'secret_versions': [],
                        'tags': [
                            'five',
                            'more',
                            'one',
                            'three',
                            'two',
                        ],
                        'tokens': [],
                        'updated_at': 1445385601.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    },
                    'status': 'ok',
                })

    def test_delete_tags(self):
        with PermissionsMock(uid=200):
            with TimeMock() as time_mock:
                with UuidMock():
                    r1 = self.client.create_secret(
                        'ABC-abc-1_2',
                        tags='one, two, three, one, two words,without space',
                        return_raw=True,
                    )

                self.assertResponseEqual(r1, {
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'status': 'ok',
                })

                r2 = self.client.get_secret(
                    '0000000000000000000000ygj0',
                    return_raw=True,
                )
                self.assertResponseEqual(r2, {
                    'page': 0,
                    'page_size': 50,
                    'secret': {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'effective_role': 'OWNER',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'ABC-abc-1_2',
                        'secret_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'secret_versions': [],
                        'tags': [
                            'one',
                            'three',
                            'two',
                            'two words',
                            'without space',
                        ],
                        'tokens': [],
                        'updated_at': 1445385600.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    },
                    'status': 'ok',
                })
                time_mock.tick()
                r3 = self.client.update_secret(
                    '0000000000000000000000ygj0',
                    tags='',
                    return_raw=True,
                )
                self.assertResponseEqual(r3, {
                    'status': 'ok',
                })

                r4 = self.client.get_secret(
                    '0000000000000000000000ygj0',
                    return_raw=True,
                )
                self.assertResponseEqual(r4, {
                    'page': 0,
                    'page_size': 50,
                    'secret': {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'effective_role': 'OWNER',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'ABC-abc-1_2',
                        'secret_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'secret_versions': [],
                        'tokens': [],
                        'updated_at': 1445385601.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    },
                    'status': 'ok',
                })

    def test_update_secret_without_touch_tags(self):
        with PermissionsMock(uid=200):
            with TimeMock() as time_mock:
                with UuidMock():
                    r1 = self.client.create_secret(
                        'ABC-abc-1_2',
                        tags='one, two, three, one, two words,without space',
                        return_raw=True,
                    )

                self.assertResponseEqual(r1, {
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'status': 'ok',
                })

                time_mock.tick()
                r2 = self.client.update_secret(
                    'sec-0000000000000000000000ygj0',
                    name='STAFF-staff-1_2',
                    comment='Test ticket',
                    return_raw=True,
                )
                self.assertResponseEqual(r2, {
                    'status': 'ok',
                })

                r3 = self.client.get_secret(
                    '0000000000000000000000ygj0',
                    return_raw=True,
                )
                self.assertResponseEqual(r3, {
                    'page': 0,
                    'page_size': 50,
                    'secret': {
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'effective_role': 'OWNER',
                        'comment': 'Test ticket',
                        'created_at': 1445385600.0,
                        'created_by': 200,
                        'name': 'STAFF-staff-1_2',
                        'secret_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 200,
                            'role_slug': 'OWNER',
                            'uid': 200,
                        }],
                        'secret_versions': [],
                        'tags': [
                            'one',
                            'three',
                            'two',
                            'two words',
                            'without space',
                        ],
                        'tokens': [],
                        'updated_at': 1445385601.0,
                        'updated_by': 200,
                        'uuid': 'sec-0000000000000000000000ygj0',
                    },
                    'status': 'ok',
                })


class TestInvalidUUID(BaseTestClass):
    fill_database = True
    send_user_ticket = True

    def test_invalid_uuid(self):
        with PermissionsMock(uid=100):
            r = self.client.get_secret(
                'sec-00000000000000000000',
                return_raw=True,
            )
            self.assertResponseError(
                r,
                InvalidUUIDValue('u\'00000000000000000000\' is an invalid UUID value'),
            )

    def test_invalid_prefix(self):
        with PermissionsMock(uid=100):
            r = self.client.get_version(
                'ooo-0000000000000000000000ygj0',
                return_raw=True,
            )
            self.assertResponseError(
                r,
                InvalidUUIDPrefix(
                    version_prefix='ooo',
                ),
            )


class TestForms(BaseTestClass):
    fill_database = True
    send_user_ticket = True

    def test_stripped_comments(self):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret = self.client.create_secret('tro-lo-lo', comment='  Secret comment   ')
                version = self.client.create_secret_version(secret, value={'key': 'value'}, comment='   ')
                _, token_uuid = self.client.create_token(secret, comment='   Secret token   ')

                self.assertDictEqual(
                    self.client.get_secret(secret),
                    {u'acl': [{u'created_at': 1445385600.0,
                               u'created_by': 100,
                               u'creator_login': u'vault-test-100',
                               u'login': u'vault-test-100',
                               u'role_slug': u'OWNER',
                               u'uid': 100}],
                     u'comment': u'Secret comment',
                     u'created_at': 1445385600.0,
                     u'created_by': 100,
                     u'creator_login': u'vault-test-100',
                     u'effective_role': u'OWNER',
                     u'name': u'tro-lo-lo',
                     u'secret_roles': [{u'created_at': 1445385600.0,
                                        u'created_by': 100,
                                        u'creator_login': u'vault-test-100',
                                        u'login': u'vault-test-100',
                                        u'role_slug': u'OWNER',
                                        u'uid': 100}],
                     u'secret_versions': [{u'comment': u'',
                                           u'created_at': 1445385600.0,
                                           u'created_by': 100,
                                           u'creator_login': u'vault-test-100',
                                           u'keys': [u'key'],
                                           u'version': version}],
                     u'tokens': [{u'comment': u'Secret token',
                                  u'created_at': 1445385600.0,
                                  u'created_by': 100,
                                  u'creator_login': u'vault-test-100',
                                  u'secret_uuid': secret,
                                  u'state_name': u'normal',
                                  u'token_uuid': token_uuid}],
                     u'updated_at': 1445385600.0,
                     u'updated_by': 100,
                     u'uuid': secret},
                )

    def test_invalid_paging_options(self):
        with PermissionsMock(uid=100):
            with self.assertRaises(ClientError) as cm:
                self.client.list_secrets(page=-99999, page_size=-99999)
            self.assertDictEqual(
                cm.exception.kwargs['errors'],
                {
                    u'page': [u'The field must be equal or great then zero'],
                    u'page_size': [u'The field must be equal or great then zero'],
                },
            )
