# -*- coding: utf-8 -*-

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.test.uuid_mock import UuidMock


class TestWebView(BaseTestClass):
    fill_database = False
    fill_staff = True
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestWebView, self).setUp()
        self.fixture.add_user(uid=200)

    def test_create_complete_secret(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock():
                    r = self.client.create_complete_secret(
                        'secret_password',
                        comment='secret comment',
                        secret_version={
                            'comment': 'secret version comment',
                            'value': {
                                'username': 'pasha',
                                'password': '123',
                            },
                        },
                        roles=[{'uid': 101, 'role': 'OWNER'}],
                    )
            self.assertDictEqual(r, {
                'secret_version': 'ver-0000000000000000000000ygj1',
                'status': 'ok',
                'uuid': 'sec-0000000000000000000000ygj0',
            })
            self.assertDictEqual(self.client.get_secret(r['uuid']), {
                'acl': [{
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'role_slug': 'OWNER',
                    'uid': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                }],
                'effective_role': 'OWNER',
                'comment': 'secret comment',
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'name': 'secret_password',
                'secret_roles': [{
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'role_slug': 'OWNER',
                    'uid': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                }, {
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'role_slug': 'OWNER',
                    'uid': 101,
                    'login': 'vault-test-101',
                    'creator_login': 'vault-test-100',
                }],
                'secret_versions': [{
                    'comment': 'secret version comment',
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'keys': ['password', 'username'],
                    'version': 'ver-0000000000000000000000ygj1',
                }],
                'tokens': [],
                'updated_at': 1445385600.0,
                'updated_by': 100,
                'uuid': 'sec-0000000000000000000000ygj0',
            })

    def test_create_secret_without_secret_version(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock():
                    r = self.client.create_complete_secret(
                        'secret_password',
                        comment='secret comment',
                    )
            self.assertDictEqual(r, {
                'status': 'ok',
                'uuid': 'sec-0000000000000000000000ygj0',
            })
            self.assertDictEqual(self.client.get_secret(r['uuid']), {
                'acl': [{
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                    'role_slug': 'OWNER',
                    'uid': 100,
                }],
                'comment': 'secret comment',
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'name': 'secret_password',
                'secret_roles': [{
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                    'role_slug': 'OWNER',
                    'uid': 100,
                }],
                'effective_role': 'OWNER',
                'secret_versions': [],
                'tokens': [],
                'updated_at': 1445385600.0,
                'updated_by': 100,
                'uuid': 'sec-0000000000000000000000ygj0',
            })

    def test_create_secret_with_same_roles(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock():
                    r = self.client.create_complete_secret(
                        'secret_password',
                        comment='secret comment',
                        roles=[{'uid': 200, 'role': 'OWNER'}, {'uid': 200, 'role': 'OWNER'}]
                    )
            self.assertDictEqual(r, {
                'status': 'ok',
                'uuid': 'sec-0000000000000000000000ygj0',
            })
            self.assertDictEqual(self.client.get_secret(r['uuid']), {
                'acl': [{
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                    'role_slug': 'OWNER',
                    'uid': 100,
                }],
                'comment': 'secret comment',
                'created_at': 1445385600.0,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'effective_role': 'OWNER',
                'name': 'secret_password',
                'secret_roles': [{
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                    'role_slug': 'OWNER',
                    'uid': 100,
                }, {
                    'created_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'role_slug': 'OWNER',
                    'uid': 200,
                }],
                'secret_versions': [],
                'tokens': [],
                'updated_at': 1445385600.0,
                'updated_by': 100,
                'uuid': 'sec-0000000000000000000000ygj0'
            })
