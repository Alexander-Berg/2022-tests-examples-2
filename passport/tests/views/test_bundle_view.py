# -*- coding: utf-8 -*-

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api import errors
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.test.uuid_mock import UuidMock


class TestBundlesView(BaseTestClass):
    fill_database = False
    fill_grants = True
    send_user_ticket = True

    def setUp(self):
        super(TestBundlesView, self).setUp()
        self.fixture.create_tables()
        self.fixture.fill_staff()
        self.fixture.add_user(uid=200)

    def tearDown(self):
        self.fixture.drop_tables()

    def test_create_bundle(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock():
                    bundle_uuid = self.client.create_bundle(
                        name='passport-bundle',
                        comment='all passport secrets',
                    )
                    bundle = self.client.get_bundle(bundle_uuid=bundle_uuid)
        self.assertDictEqual(bundle, {
            'bundle_roles': [{
                'created_at': 1445385600.0,
                'created_by': 100,
                'role_slug': 'OWNER',
                'uid': 100,
                'login': 'vault-test-100',
                'creator_login': 'vault-test-100',
            }],
            'bundle_versions': [],
            'comment': 'all passport secrets',
            'created_at': 1445385600.000,
            'created_by': 100,
            'creator_login': 'vault-test-100',
            'name': 'passport-bundle',
            'updated_at': 1445385600.000,
            'updated_by': 100,
            'uuid': 'bun-0000000000000000000000ygj0',
        })

    def test_update_bundle(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock() as time_mock:
                    bundle_uuid = self.client.create_bundle(
                        name='passport-bundle',
                        comment='all passport secrets',
                    )
                    bundle = self.client.get_bundle(
                        bundle_uuid=bundle_uuid,
                    )
                    self.assertDictEqual(bundle, {
                        'bundle_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'role_slug': 'OWNER',
                            'uid': 100,
                            'login': 'vault-test-100',
                            'creator_login': 'vault-test-100',
                        }],
                        'bundle_versions': [],
                        'comment': 'all passport secrets',
                        'created_at': 1445385600.000,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'name': 'passport-bundle',
                        'updated_at': 1445385600.000,
                        'updated_by': 100,
                        'uuid': 'bun-0000000000000000000000ygj0',
                    })

                    time_mock.tick()
                    r2 = self.client.update_bundle(
                        bundle_uuid=bundle_uuid,
                        name='passport-bundle-1',
                        comment='only one passport secret',
                    )
                    self.assertTrue(r2)

                    r3 = self.client.get_bundle(
                        bundle_uuid=bundle_uuid,
                    )
                    self.assertDictEqual(r3, {
                        'bundle_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'login': 'vault-test-100',
                            'role_slug': 'OWNER',
                            'uid': 100,
                        }],
                        'bundle_versions': [],
                        'comment': 'only one passport secret',
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'name': 'passport-bundle-1',
                        'updated_at': 1445385601.0,
                        'updated_by': 100,
                        'uuid': 'bun-0000000000000000000000ygj0',
                    })

    def test_delete_bundle_comment(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock() as time_mock:
                    bundle_uuid = self.client.create_bundle(
                        name='passport-bundle',
                        comment='all passport secrets',
                    )
                    bundle = self.client.get_bundle(
                        bundle_uuid=bundle_uuid,
                    )
                    self.assertDictEqual(bundle, {
                        'bundle_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'role_slug': 'OWNER',
                            'uid': 100,
                            'login': 'vault-test-100',
                            'creator_login': 'vault-test-100',
                        }],
                        'bundle_versions': [],
                        'comment': 'all passport secrets',
                        'created_at': 1445385600.000,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'name': 'passport-bundle',
                        'updated_at': 1445385600.000,
                        'updated_by': 100,
                        'uuid': 'bun-0000000000000000000000ygj0',
                    })

                    time_mock.tick()
                    self.client.update_bundle(
                        bundle_uuid=bundle_uuid,
                        comment='',
                    )

                    time_mock.tick()
                    r3 = self.client.get_bundle(
                        bundle_uuid=bundle_uuid,
                    )
                    self.assertDictEqual(r3, {
                        'bundle_roles': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'role_slug': 'OWNER',
                            'uid': 100,
                            'login': 'vault-test-100',
                            'creator_login': 'vault-test-100',
                        }],
                        'bundle_versions': [],
                        'comment': '',
                        'created_at': 1445385600.000,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'name': 'passport-bundle',
                        'updated_at': 1445385601.000,
                        'updated_by': 100,
                        'uuid': 'bun-0000000000000000000000ygj0',
                    })

    def test_bundle_with_same_name(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock():
                    self.client.create_bundle(
                        name='passport-bundle',
                        comment='all passport secrets',
                    )
                    self.client.create_bundle(
                        name='passport-bundle',
                        comment='all passport secrets',
                    )
                    bundles = self.client.list_bundles(order_by='uuid')
                    self.assertListEqual(bundles, [
                        {
                            'acl': [{
                                'created_at': 1445385600.0,
                                'created_by': 100,
                                'role_slug': 'OWNER',
                                'uid': 100,
                                'login': 'vault-test-100',
                                'creator_login': 'vault-test-100',
                            }],
                            'bundle_roles': [{
                                'created_at': 1445385600.0,
                                'created_by': 100,
                                'role_slug': 'OWNER',
                                'uid': 100,
                                'login': 'vault-test-100',
                                'creator_login': 'vault-test-100',
                            }],
                            'comment': 'all passport secrets',
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'name': 'passport-bundle',
                            'updated_at': 1445385600.0,
                            'updated_by': 100,
                            'uuid': 'bun-0000000000000000000000ygj2',
                        }, {
                            'acl': [{
                                'created_at': 1445385600.0,
                                'created_by': 100,
                                'role_slug': 'OWNER',
                                'uid': 100,
                                'login': 'vault-test-100',
                                'creator_login': 'vault-test-100',
                            }],
                            'bundle_roles': [{
                                'created_at': 1445385600.0,
                                'created_by': 100,
                                'role_slug': 'OWNER',
                                'uid': 100,
                                'login': 'vault-test-100',
                                'creator_login': 'vault-test-100',
                            }],
                            'comment': 'all passport secrets',
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'name': 'passport-bundle',
                            'updated_at': 1445385600.0,
                            'updated_by': 100,
                            'uuid': 'bun-0000000000000000000000ygj0',
                        }
                    ])

    def test_create_bundle_version(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock():
                    secret_uuid = self.client.create_secret('passport-secret')
                    secret_version = self.client.create_secret_version(
                        secret_uuid,
                        value={'password': '123456'},
                    )
                    bundle_uuid = self.client.create_bundle(
                        name='passport-bundle',
                        comment='all passport secrets',
                    )
                    bundle_version = self.client.create_bundle_version(
                        bundle_uuid=bundle_uuid,
                        secret_versions=[secret_version],
                    )
                    secrets = self.client.get_version(bundle_version)
                    self.assertEqual(secrets, {
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'secret_versions': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'creator_login': 'vault-test-100',
                            'secret_name': 'passport-secret',
                            'value': {'password': '123456'},
                            'version': 'ver-0000000000000000000000ygj2',
                            'secret_uuid': 'sec-0000000000000000000000ygj0',
                        }],
                        'version': 'bve-0000000000000000000000ygj5',
                    })

    def test_hide_bundle(self):
        with PermissionsMock(uid=200):
            with UuidMock():
                with TimeMock():
                    bundle_1 = self.client.create_bundle('ololo-bundle-1')
                    self.client.update_bundle(bundle_1, state='hidden')
                    self.assertListEqual(self.client.list_bundles(), [])
                    self.assertEqual(
                        self.client.get_bundle(bundle_1, return_raw=True).json()['status'],
                        'warning',
                    )
                    self.client.update_bundle(bundle_1, state='normal')
                    self.assertEqual(len(self.client.list_bundles()), 1)

    def test_hide_version(self):
        with PermissionsMock(uid=200):
            with UuidMock():
                with TimeMock():
                    secret_1 = self.client.create_secret('ololo-secret-1')
                    secret_version_1 = self.client.create_secret_version(secret_1, {'a': 1})
                    bundle_1 = self.client.create_bundle('ololo-bundle-1')
                    version_1 = self.client.create_bundle_version(bundle_1, secret_versions=[secret_version_1])
                    version_2 = self.client.create_bundle_version(bundle_1, secret_versions=[secret_version_1])
                    self.assertEqual(
                        len(self.client.get_bundle(bundle_1)['bundle_versions']),
                        2,
                    )
                    self.client.update_version(version_2, state='hidden')
                    self.assertEqual(
                        len(self.client.get_bundle(bundle_1)['bundle_versions']),
                        1,
                    )
                    self.assertEqual(
                        self.client.get_version(version_2, return_raw=True).json()['status'],
                        'warning',
                    )
                    self.client.update_version(version_2, state='normal')
                    self.assertEqual(
                        len(self.client.get_bundle(bundle_1)['bundle_versions']),
                        2,
                    )
                    self.client.update_version(bundle_1, state='hidden')
                    self.assertEqual(
                        len(self.client.get_bundle(bundle_1)['bundle_versions']),
                        1,
                    )
                    self.client.update_bundle(bundle_1, state='hidden')
                    self.assertEqual(
                        self.client.get_version(version_1, return_raw=True).json()['status'],
                        'warning',
                    )

    def test_get_removed_bundle(self):
        with PermissionsMock(uid=100):
            with UuidMock():
                with TimeMock(offset=15):
                    secret = self.client.create_secret('ololo')
                    secret_version = self.client.create_secret_version(secret, {'a': 1})
                    bundle = self.client.create_bundle('ololo-bundle-1')
                    version = self.client.create_bundle_version(bundle, secret_versions=[secret_version])
                    self.client.update_bundle(bundle, state='hidden')

                    r = self.client.get_bundle(bundle, return_raw=True)
                    self.assertResponseEqual(
                        r,
                        {
                            'bundle': {
                                'bundle_roles': [{
                                    'created_at': 1445385615.0,
                                    'created_by': 100,
                                    'creator_login': 'vault-test-100',
                                    'login': 'vault-test-100',
                                    'role_slug': 'OWNER',
                                    'uid': 100,
                                }],
                                'bundle_versions': [{
                                    'created_at': 1445385615.0,
                                    'created_by': 100,
                                    'creator_login': 'vault-test-100',
                                    'secret_versions': [{
                                        'created_at': 1445385615.0,
                                        'created_by': 100,
                                        'creator_login': 'vault-test-100',
                                        'keys': ['a'],
                                        'secret_name': 'ololo',
                                        'value': [{'key': 'a', 'value': '1'}],
                                        'version': secret_version,
                                    }],
                                    'version': version,
                                }],
                                'created_at': 1445385615.0,
                                'created_by': 100,
                                'creator_login': 'vault-test-100',
                                'name': 'ololo-bundle-1',
                                'state_name': 'hidden',
                                'updated_at': 1445385615.0,
                                'updated_by': 100,
                                'uuid': bundle,
                            },
                            'page': 0,
                            'page_size': 50,
                            'status': 'warning',
                            'warning_message': 'version is hidden',
                        },
                    )

    def test_get_unaccesed_removed_bundle(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            secret_version = self.client.create_secret_version(secret, {'a': 1})
            bundle = self.client.create_bundle('ololo-bundle-1')
            self.client.create_bundle_version(bundle, secret_versions=[secret_version])
            self.client.update_bundle(bundle, state='hidden')

        with PermissionsMock(uid=101):
            r = self.client.get_bundle(bundle, return_raw=True)
            self.assertResponseError(
                r,
                errors.AccessError(bundle_state_name='hidden'),
            )
