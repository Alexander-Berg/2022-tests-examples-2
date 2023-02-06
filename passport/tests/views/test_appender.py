# coding: utf-8

from base64 import b64encode

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.errors import AccessError
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock


class TestAppenderRole(BaseTestClass):
    """
    Тестами фиксируем что может APPENDER, а что нет
    """
    send_user_ticket = True

    def setUp(self):
        super(TestAppenderRole, self).setUp()
        self.fixture.add_user(uid=200)

    def test_workflow_ok(self):
        """
        Проверяем сценарий:
        — создать секрет
        — выдать роль OWNER другому пользователю
        — выдать себе роль APPENDER
        — отозвать у себя роль OWNER
        — создать версию от своего имени
        — получить ошибку при попытке прочитать версию
        — создать diff-версию от секрета с новым значением
        — получить ошибку при попытке прочитать новую версию
        — прочитать версии пользователем с ролью OWNER
        """
        with PermissionsMock(uid=100):
            with TimeMock(offset=100) as tm:
                secret = self.client.create_secret('new_cert')
                self.assertResponseOk(
                    self.client.add_user_role_to_secret(secret, 'OWNER', uid=200, return_raw=True),
                    code=201,
                )
                self.assertResponseOk(
                    self.client.add_user_role_to_secret(secret, 'APPENDER', uid=100, return_raw=True),
                    code=201,
                )
                self.assertResponseOk(
                    self.client.delete_user_role_from_secret(secret, 'OWNER', uid=100, return_raw=True),
                    code=200,
                )
                version_1 = self.client.create_secret_version(
                    secret,
                    comment='The first SSL certificate for passport.yandex.ru',
                    value=[
                        {'key': 'domain', 'value': 'passport.yandex.ru'},
                        {'key': 'cert.crt', 'value': b64encode('Certificate'), 'encoding': 'base64'},
                        {'key': 'cert.key', 'value': b64encode('Key'), 'encoding': 'base64'},
                    ],
                )
                tm.tick()
                self.assertResponseError(
                    self.client.get_version(version_1, return_raw=True),
                    AccessError,
                )
                version_2 = self.client.create_diff_version(
                    version_1,
                    comment='The new SSL certificate for passport.yandex.ru',
                    diff=[
                        {'key': 'cert.crt', 'value': b64encode('Certificate 2'), 'encoding': 'base64'},
                        {'key': 'cert.key', 'value': b64encode('Key 2'), 'encoding': 'base64'},
                    ],
                )
                self.assertResponseError(
                    self.client.get_version(version_2, return_raw=True),
                    AccessError,
                )

                self.assertResponseEqual(
                    self.client.get_secret(secret, return_raw=True),
                    {u'page': 0,
                     u'page_size': 50,
                     u'secret': {u'acl': [{u'created_at': 1445385700.0,
                                           u'created_by': 100,
                                           u'creator_login': u'vault-test-100',
                                           u'login': u'vault-test-100',
                                           u'role_slug': u'APPENDER',
                                           u'uid': 100}],
                                 u'created_at': 1445385700.0,
                                 u'created_by': 100,
                                 u'creator_login': u'vault-test-100',
                                 u'effective_role': u'APPENDER',
                                 u'name': u'new_cert',
                                 u'secret_roles': [{u'created_at': 1445385700.0,
                                                    u'created_by': 100,
                                                    u'creator_login': u'vault-test-100',
                                                    u'role_slug': u'OWNER',
                                                    u'uid': 200},
                                                   {u'created_at': 1445385700.0,
                                                    u'created_by': 100,
                                                    u'creator_login': u'vault-test-100',
                                                    u'login': u'vault-test-100',
                                                    u'role_slug': u'APPENDER',
                                                    u'uid': 100}],
                                 u'secret_versions': [{u'comment': u'The new SSL certificate for passport.yandex.ru',
                                                       u'created_at': 1445385701.0,
                                                       u'created_by': 100,
                                                       u'creator_login': u'vault-test-100',
                                                       u'keys': [u'cert.crt',
                                                                 u'cert.key',
                                                                 u'domain'],
                                                       u'parent_diff_keys': {u'added': [],
                                                                             u'changed': [u'cert.crt',
                                                                                          u'cert.key'],
                                                                             u'removed': []},
                                                       u'parent_version_uuid': version_1,
                                                       u'version': version_2},
                                                      {u'comment': u'The first SSL certificate for passport.yandex.ru',
                                                       u'created_at': 1445385700.0,
                                                       u'created_by': 100,
                                                       u'creator_login': u'vault-test-100',
                                                       u'keys': [u'cert.crt',
                                                                 u'cert.key',
                                                                 u'domain'],
                                                       u'version': version_1}],
                                 u'tokens': [],
                                 u'updated_at': 1445385701.0,
                                 u'updated_by': 100,
                                 u'uuid': secret},
                     u'status': u'ok'}
                )

        with PermissionsMock(uid=200):
            self.assertResponseEqual(
                self.client.get_version(version_1, return_raw=True),
                {u'status': u'ok',
                 u'version': {u'comment': u'The first SSL certificate for passport.yandex.ru',
                              u'created_at': 1445385700.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'secret_name': u'new_cert',
                              u'secret_uuid': secret,
                              u'value': [{u'key': u'domain',
                                          u'value': u'passport.yandex.ru'},
                                         {u'encoding': u'base64',
                                          u'key': u'cert.crt',
                                          u'value': b64encode('Certificate')},
                                         {u'encoding': u'base64',
                                          u'key': u'cert.key',
                                          u'value': b64encode('Key')}],
                              u'version': version_1}},
            )
            self.assertResponseEqual(
                self.client.get_version(version_2, return_raw=True),
                {u'status': u'ok',
                 u'version': {u'comment': u'The new SSL certificate for passport.yandex.ru',
                              u'created_at': 1445385701.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'parent_version_uuid': version_1,
                              u'secret_name': u'new_cert',
                              u'secret_uuid': secret,
                              u'value': [{u'encoding': u'base64',
                                          u'key': u'cert.crt',
                                          u'value': b64encode('Certificate 2')},
                                         {u'key': u'domain',
                                          u'value': u'passport.yandex.ru'},
                                         {u'encoding': u'base64',
                                          u'key': u'cert.key',
                                          u'value': b64encode('Key 2')}],
                              u'version': version_2}},
            )

    def test_appender_approved_actions(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=100):
                secret = self.client.create_secret('new_cert')
                version_1 = self.client.create_secret_version(
                    secret,
                    comment='The first SSL certificate for passport.yandex.ru',
                    value=[
                        {'key': 'domain', 'value': 'passport.yandex.ru'},
                        {'key': 'cert.crt', 'value': b64encode('Certificate'), 'encoding': 'base64'},
                        {'key': 'cert.key', 'value': b64encode('Key'), 'encoding': 'base64'},
                    ],
                )
                self.client.add_user_role_to_secret(secret, 'APPENDER', uid=200)
                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [{u'created_at': 1445385700.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'uid': 100},
                     {u'created_at': 1445385700.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'role_slug': u'APPENDER',
                      u'uid': 200}],
                )
                _, token_uuid = self.client.create_token(secret)

        with PermissionsMock(uid=200):
            self.assertResponseOk(self.client.get_secret(secret, return_raw=True))
            self.assertResponseEqual(
                self.client.list_secrets(return_raw=True),
                {u'page': 0,
                 u'page_size': 50,
                 u'secrets': [{u'acl': [{u'created_at': 1445385700.0,
                                         u'created_by': 100,
                                         u'creator_login': u'vault-test-100',
                                         u'role_slug': u'APPENDER',
                                         u'uid': 200}],
                               u'created_at': 1445385700.0,
                               u'created_by': 100,
                               u'creator_login': u'vault-test-100',
                               u'effective_role': u'APPENDER',
                               u'last_secret_version': {u'comment': u'The first SSL certificate for passport.yandex.ru',
                                                        u'version': version_1},
                               u'name': u'new_cert',
                               u'secret_roles': [{u'created_at': 1445385700.0,
                                                  u'created_by': 100,
                                                  u'creator_login': u'vault-test-100',
                                                  u'login': u'vault-test-100',
                                                  u'role_slug': u'OWNER',
                                                  u'uid': 100},
                                                 {u'created_at': 1445385700.0,
                                                  u'created_by': 100,
                                                  u'creator_login': u'vault-test-100',
                                                  u'role_slug': u'APPENDER',
                                                  u'uid': 200}],
                               u'tokens_count': 1,
                               u'updated_at': 1445385700.0,
                               u'updated_by': 100,
                               u'uuid': secret,
                               u'versions_count': 1}],
                 u'status': u'ok'},
            )
            self.assertResponseEqual(
                self.client.list_tokens(secret, return_raw=True),
                {u'status': u'ok',
                 u'tokens': [{u'created_at': 1445385700.0,
                              u'created_by': 100,
                              u'creator_login': u'vault-test-100',
                              u'state_name': u'normal',
                              u'secret_uuid': secret,
                              u'token_uuid': token_uuid}]},
            )

    def test_appender_forbidden_actions(self):
        with PermissionsMock(uid=100):
            with TimeMock(offset=100):
                secret = self.client.create_secret('new_cert')
                version_1 = self.client.create_secret_version(
                    secret,
                    comment='The first SSL certificate for passport.yandex.ru',
                    value=[
                        {'key': 'domain', 'value': 'passport.yandex.ru'},
                        {'key': 'cert.crt', 'value': b64encode('Certificate'), 'encoding': 'base64'},
                        {'key': 'cert.key', 'value': b64encode('Key'), 'encoding': 'base64'},
                    ],
                )
                self.client.add_user_role_to_secret(secret, 'APPENDER', uid=200)
                self.assertListEqual(
                    self.client.get_secret(secret)['secret_roles'],
                    [{u'created_at': 1445385700.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'login': u'vault-test-100',
                      u'role_slug': u'OWNER',
                      u'uid': 100},
                     {u'created_at': 1445385700.0,
                      u'created_by': 100,
                      u'creator_login': u'vault-test-100',
                      u'role_slug': u'APPENDER',
                      u'uid': 200}],
                )
                _, token_uuid = self.client.create_token(secret)

        with PermissionsMock(uid=200):
            self.assertResponseError(
                self.client.update_secret(secret, comment='new comment', return_raw=True),
                AccessError,
            )

            self.assertResponseError(
                self.client.get_version(version_1, return_raw=True),
                AccessError,
            )

            self.assertResponseError(
                self.client.update_version(version_1, state='hidden', return_raw=True),
                AccessError,
            )

            self.assertResponseError(
                self.client.add_user_role_to_secret(secret, 'READER', uid=300, return_raw=True),
                AccessError,
            )

            self.assertResponseError(
                self.client.delete_user_role_from_secret(secret, 'OWNER', uid=100, return_raw=True),
                AccessError,
            )

            self.assertResponseError(
                self.client.create_token(secret, return_raw=True),
                AccessError,
            )

            self.assertResponseError(
                self.client.revoke_token(token_uuid, return_raw=True),
                AccessError,
            )

            self.assertResponseError(
                self.client.add_supervisor(uid=300, return_raw=True),
                AccessError,
            )
