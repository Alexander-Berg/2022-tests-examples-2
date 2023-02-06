# -*- coding: utf-8 -*-

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api import errors
from passport.backend.vault.api.models import (
    AbcScope,
    Roles,
    UserRole,
)
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.logging_mock import LoggingMock
from passport.backend.vault.api.test.permissions_mock import (
    PermissionsMock,
    VALID_SERVICE_TICKET_SINGLESS_1,
    VALID_USER_TICKET_SIGNLESS_1,
)


class TestRolesView(BaseTestClass):
    send_user_ticket = True

    def test_add_multiple_ids_roles(self):
        with PermissionsMock(uid=100):
            r = self.client.add_user_role_to_secret(
                'sec-0000000000000000000000ygj0', Roles.READER.name, uid=100, staff_id=100,
                return_raw=True,
            )
            self.assertResponseError(
                r,
                errors.ValidationError({
                    'abc_id': 'Only one parameter must be set among abc_id, login, staff_id, uid',
                    'login': 'Only one parameter must be set among abc_id, login, staff_id, uid',
                    'staff_id': 'Only one parameter must be set among abc_id, login, staff_id, uid',
                    'uid': 'Only one parameter must be set among abc_id, login, staff_id, uid',
                }),
            )

    def test_add_and_remove_role(self):
        with TimeMock():
            with PermissionsMock(uid=100):
                with LoggingMock() as logging_mock:
                    r = self.client.add_user_role_to_secret(
                        'sec-0000000000000000000000ygj0', Roles.OWNER.name, uid=102,
                        return_raw=True,
                    )
                    self.assertResponseOk(r, code=201)

                    self.assertListEqual(
                        logging_mock.getLogger('statbox').entries,
                        [({'action': 'enter',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'mode': 'create_secret_user_role',
                           'tvm_grants': 'granted',
                           'auth_uid': 100},
                          'INFO', None, None,),
                         ({'action': 'success',
                           'added': True,
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'deleted_by': 100,
                           'mode': 'create_secret_user_role',
                           'role': 'OWNER',
                           'secret_uuid': 'sec-0000000000000000000000ygj0',
                           'tvm_grants': 'granted',
                           'auth_uid': 100,
                           'uid': 102},
                          'INFO', None, None,),
                         ({'action': 'exit',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'mode': 'create_secret_user_role',
                           'tvm_grants': 'granted',
                           'auth_uid': 100},
                          'INFO', None, None,)]
                    )

            with PermissionsMock(uid=102):
                r = self.client.list_secrets()
                self.assertListEqual(r, [{
                    'uuid': 'sec-0000000000000000000000ygj0',
                    'name': 'secret_1',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                    'created_at': 1445385600.0,
                    'updated_at': 1445385600.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 102,
                        'login': 'vault-test-102',
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }, {
                        'role_slug': 'OWNER',
                        'uid': 102,
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'login': 'vault-test-102',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_by': 100,
                    'versions_count': 3,
                    'tokens_count': 0,
                }])

                with LoggingMock() as logging_mock:
                    self.client.delete_user_role_from_secret(
                        'sec-0000000000000000000000ygj0',
                        Roles.OWNER.name,
                        uid=100,
                    )
                    self.assertListEqual(
                        logging_mock.getLogger('statbox').entries,
                        [({'action': 'enter',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'mode': 'delete_secret_user_role',
                           'tvm_grants': 'granted',
                           'auth_uid': 102},
                          'INFO', None, None,),
                         ({'action': 'success',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'deleted_by': 102,
                           'mode': 'delete_secret_user_role',
                           'role': 'OWNER',
                           'secret_uuid': 'sec-0000000000000000000000ygj0',
                           'tvm_grants': 'granted',
                           'auth_uid': 102,
                           'uid': 100},
                          'INFO', None, None,),
                         ({'action': 'exit',
                           'auth_type': 'user_ticket',
                           'auth_service_ticket': VALID_SERVICE_TICKET_SINGLESS_1,
                           'auth_tvm_app_id': 1,
                           'auth_user_ticket': VALID_USER_TICKET_SIGNLESS_1,
                           'mode': 'delete_secret_user_role',
                           'tvm_grants': 'granted',
                           'auth_uid': 102},
                          'INFO', None, None,)],
                    )

            with PermissionsMock(uid=100):
                r = self.client.list_secrets()
                self.assertListEqual(r, [{
                    'uuid': 'sec-0000000000000000000000ygj5',
                    'name': 'secret_2',
                    'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                    'created_at': 1445385604.0,
                    'updated_at': 1445385608.0,
                    'created_by': 100,
                    'creator_login': 'vault-test-100',
                    'acl': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'effective_role': 'OWNER',
                    'secret_roles': [{
                        'role_slug': 'OWNER',
                        'uid': 100,
                        'created_at': 1445385604.0,
                        'created_by': 100,
                        'login': 'vault-test-100',
                        'creator_login': 'vault-test-100',
                    }],
                    'updated_by': 100,
                    'versions_count': 4,
                    'tokens_count': 0,
                }])

    def test_exists_role(self):
        with TimeMock():
            with PermissionsMock(uid=100):
                r = self.client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    Roles.OWNER.name,
                    uid=102,
                    return_raw=True,
                )
                self.assertResponseOk(r, code=201)

                r = self.client.add_user_role_to_secret(
                    'sec-0000000000000000000000ygj0',
                    Roles.OWNER.name,
                    uid=102,
                    return_raw=True,
                )
                self.assertResponseOk(r, code=200)

            with PermissionsMock(uid=102):
                r = self.client.list_secrets()
                self.assertListEqual(
                    r,
                    [{
                        'acl': [{
                            'created_at': 1445385600.0,
                            'created_by': 100,
                            'role_slug': 'OWNER',
                            'uid': 102,
                            'login': 'vault-test-102',
                            'creator_login': 'vault-test-100',
                        }],
                        'effective_role': 'OWNER',
                        'created_at': 1445385600.0,
                        'created_by': 100,
                        'creator_login': 'vault-test-100',
                        'name': 'secret_1',
                        'last_secret_version': {'version': 'ver-0000000000000000000000ygj4'},
                        'secret_roles': [
                            {
                                'created_at': 1445385600.0,
                                'created_by': 100,
                                'role_slug': 'OWNER',
                                'uid': 100,
                                'login': 'vault-test-100',
                                'creator_login': 'vault-test-100',
                            },
                            {
                                'created_at': 1445385600.0,
                                'created_by': 100,
                                'role_slug': 'OWNER',
                                'uid': 102,
                                'login': 'vault-test-102',
                                'creator_login': 'vault-test-100',
                            },
                        ],
                        'updated_at': 1445385600.0,
                        'updated_by': 100,
                        'uuid': 'sec-0000000000000000000000ygj0',
                        'versions_count': 3,
                        'tokens_count': 0,
                    }],
                )

    def test_remove_nonexistant_role(self):
        with PermissionsMock(uid=100):
            r = self.client.delete_user_role_from_secret(
                'sec-0000000000000000000000ygj0', Roles.READER.name, uid=102,
                return_raw=True,
            )
            self.assertResponseOk(r, code=204)

    def test_last_owner(self):
        with PermissionsMock(uid=100):
            r = self.client.delete_user_role_from_secret(
                'sec-0000000000000000000000ygj0', Roles.OWNER.name, uid=100,
                return_raw=True,
            )
            self.assertResponseError(r, errors.LastOwnerError)

    def test_add_role_by_login(self):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret = self.client.create_secret('ololo')
                r = self.client.add_user_role_to_secret(
                    secret,
                    Roles.OWNER.name,
                    login='vault-test-101',
                    return_raw=True,
                )
                self.assertResponseOk(r, code=201)

            self.assertListEqual(
                self.client.get_secret(secret)['secret_roles'],
                [{u'created_at': 1445385600.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'login': u'vault-test-100',
                  u'role_slug': u'OWNER',
                  u'uid': 100},
                 {u'created_at': 1445385600.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'login': u'vault-test-101',
                  u'role_slug': u'OWNER',
                  u'uid': 101}]
            )

    def test_add_and_remove_role_for_abc_service(self):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret = self.client.create_secret('ololo')
                r = self.client.add_user_role_to_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    return_raw=True,
                )
                self.assertResponseOk(r, code=201)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [{u'created_at': 1445385600.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'uid': 100},
                     {u'abc_id': 14,
                      u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                      u'abc_scope': u'development',
                      u'abc_scope_id': 5,
                      u'abc_scope_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                      u'abc_slug': u'passp',
                      u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                      u'created_at': 1445385600.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'role_slug': u'OWNER'}],
                )

                r = self.client.delete_user_role_from_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    return_raw=True,
                )
                self.assertResponseOk(r)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [{u'created_at': 1445385600.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'uid': 100}],
                )

    def test_add_and_remove_role_for_abc_scope(self):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret = self.client.create_secret('ololo')
                r = self.client.add_user_role_to_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    abc_scope='tvm_management',
                    return_raw=True,
                )
                self.assertResponseOk(r, code=201)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [
                        {u'created_at': 1445385600.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 100},
                        {u'abc_id': 14,
                         u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                         u'abc_scope': u'tvm_management',
                         u'abc_scope_id': 17,
                         u'abc_scope_name': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 TVM',
                         u'abc_slug': u'passp',
                         u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                         u'created_at': 1445385600.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'role_slug': u'OWNER'},
                    ],
                )

                r = self.client.delete_user_role_from_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    abc_scope='tvm_management',
                    return_raw=True,
                )
                self.assertResponseOk(r)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [{u'created_at': 1445385600.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'uid': 100}],
                )

    def test_add_and_remove_role_to_abc_role(self):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret = self.client.create_secret('ololo')
                r = self.client.add_user_role_to_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    abc_role_id=630,
                    return_raw=True,
                )
                self.assertResponseOk(r, code=201)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [
                        {u'created_at': 1445385600.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 100},
                        {u'abc_id': 14,
                         u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                         u'abc_role': 630,
                         u'abc_role_name': u'TVM \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440',
                         u'abc_slug': u'passp',
                         u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                         u'created_at': 1445385600.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'role_slug': u'OWNER'},
                    ],
                )

                r = self.client.delete_user_role_from_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    abc_role_id=630,
                    return_raw=True,
                )
                self.assertResponseOk(r)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [
                        {u'created_at': 1445385600.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'login': u'vault-test-100',
                         u'role_slug': u'OWNER',
                         u'uid': 100},
                    ],
                )

    def test_add_and_remove_role_for_staff_group(self):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret = self.client.create_secret('ololo')
                r = self.client.add_user_role_to_secret(
                    secret,
                    Roles.OWNER.name,
                    staff_id='38098',
                    return_raw=True,
                )
                self.assertResponseOk(r, code=201)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [{u'created_at': 1445385600.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'uid': 100},
                     {u'created_at': 1445385600.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'staff_id': 38098,
                      u'staff_name': u'\u0421\u043b\u0443\u0436\u0431\u0430 '
                                      u'\u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 \u0438 '
                                      u'\u043a\u043e\u043d\u0432\u0435\u0439\u0435\u0440\u0438\u0437\u0430\u0446\u0438\u0438',
                      u'staff_slug': u'yandex_search_tech_sq_analysis',
                      u'staff_url': u'https://staff.yandex-team.ru/departments/yandex_search_tech_sq_analysis/'}]
                )

                r = self.client.delete_user_role_from_secret(
                    secret,
                    Roles.OWNER.name,
                    staff_id='38098',
                    return_raw=True,
                )
                self.assertResponseOk(r)

                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [{u'created_at': 1445385600.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'uid': 100}],
                )

    def test_unknown_abc_service(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                abc_id=999999999,
                return_raw=True,
            )
            self.assertResponseError(r, errors.AbcServiceNotFoundError)

    def test_unknown_abc_scope(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                abc_id=14,
                abc_scope='unknown_abc_scope',
                return_raw=True,
            )
            self.assertResponseError(r, errors.AbcScopeNotFoundError)

    def test_unknown_abc_role(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                abc_id=14,
                abc_role_id='99999999',
                return_raw=True,
            )
            self.assertResponseError(r, errors.AbcRoleNotFoundError)

    def test_abc_scope_missing_in_service(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                abc_id=50,
                abc_scope='tvm_management',
                return_raw=True,
            )
            self.assertResponseError(r, errors.AbcScopeNotFoundError)

    def test_abc_role_missing_in_service(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                abc_id=50,
                abc_role_id='630',
                return_raw=True,
            )
            self.assertResponseError(r, errors.AbcRoleNotFoundError)

    def test_try_get_role_for_abc_ecope_and_role_at_same_time(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                abc_id=14,
                abc_scope='development',
                abc_role_id='630',
                return_raw=True,
            )
            self.assertResponseError(
                r,
                errors.ValidationError({
                    u'abc_role_id': u'Only one parameter must be set among abc_scope, abc_role_id',
                    u'abc_scope': u'Only one parameter must be set among abc_scope, abc_role_id',
                }),
            )

    def test_unknown_staff_group(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                staff_id=9999999,
                return_raw=True,
            )
            self.assertResponseError(r, errors.StaffGroupNotFoundError)

    def test_unknown_uid(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            r = self.client.add_user_role_to_secret(
                secret,
                Roles.OWNER.name,
                uid=999999999999,
                return_raw=True,
            )
            self.assertResponseError(r, errors.UserNotFoundError)

    def test_validate_uid_on_secret_creation(self):
        with PermissionsMock(uid=999999999999):
            self.assertResponseError(
                self.client.create_secret('ololo', return_raw=True),
                errors.UserNotFoundError,
            )

    def test_skip_validate_uid_on_secret_creation(self):
        with PermissionsMock(uid=999999999999):
            old_config_value = self.config['application']['validate_uid_on_secret_creation']
            self.config['application']['validate_uid_on_secret_creation'] = False

            try:
                self.assertResponseOk(
                    self.client.create_secret('ololo', return_raw=True),
                )
            finally:
                self.config['application']['validate_uid_on_secret_creation'] = old_config_value

    def test_remove_role_with_nonexistant_service_scope(self):
        with PermissionsMock(uid=100):
            with TimeMock():
                secret = self.client.create_secret('ololo')
                with self.app.app_context():
                    scope = AbcScope.get_by_name('administration')
                    self.fixture.db.session.add(
                        UserRole(
                            secret_uuid=secret,
                            external_type='abc',
                            role_id=Roles.OWNER,
                            abc_id=14,
                            abc_scope_id=scope.id,
                            created_by=100,
                        ),
                    )
                    self.fixture.db.session.commit()

            self.assertListEqual(
                self.client.get_secret(secret)['secret_roles'],
                [{u'created_at': 1445385600.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'login': u'vault-test-100',
                  u'role_slug': u'OWNER',
                  u'uid': 100},
                 {u'abc_id': 14,
                  u'abc_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                  u'abc_scope': u'administration',
                  u'abc_scope_id': 8,
                  u'abc_scope_name': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435',
                  u'abc_slug': u'passp',
                  u'abc_url': u'https://abc.yandex-team.ru/services/passp/',
                  u'created_at': 1445385600.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'role_slug': u'OWNER'}],
            )

            self.assertResponseOk(
                self.client.delete_user_role_from_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    abc_scope='administration',
                    return_raw=True,
                ),
            )

            self.assertListEqual(
                self.client.get_secret(secret)['secret_roles'],
                [{u'created_at': 1445385600.0,
                  u'created_by': 100,
                  u'creator_login': u'vault-test-100',
                  u'login': u'vault-test-100',
                  u'role_slug': u'OWNER',
                  u'uid': 100}],
            )

    def test_try_to_remove_role_with_unknown_service_scope(self):
        with PermissionsMock(uid=100):
            secret = self.client.create_secret('ololo')
            self.client.add_user_role_to_secret(secret, Roles.OWNER.name, uid=101)
            self.assertResponseError(
                self.client.delete_user_role_from_secret(
                    secret,
                    Roles.OWNER.name,
                    abc_id=14,
                    abc_scope='unknown',
                    return_raw=True,
                ),
                errors.AbcScopeNotFoundError(None, 'unknown'),
            )
