# -*- coding: utf-8 -*-

import random
import time

from passport.backend.vault.api.models import (
    AbcDepartmentInfo,
    AbcRole,
    AbcScope,
    ExternalRecord,
    StaffDepartmentInfo,
)
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.utils.ulid import ULID


class TestHighloadAccess(BaseTestClass):
    fill_database = False
    fill_staff = True
    fill_grants = True
    send_user_ticket = True

    def fill_abc_and_staff(self, records_count=5000, first_record_number=60000):
        with self.fixture.app.app_context():
            abc_scopes = [
                AbcScope(id=5, unique_name='development', display_name=u'Разработка'),
                AbcScope(id=17, unique_name='tvm_management', display_name=u'TVM менеджер'),
                AbcScope(id=8, unique_name='administration', display_name=u'Администрирование'),
            ]
            abc_roles = [
                AbcRole(id=8, display_name=u'Developer', english_name=u'Developer'),
                AbcRole(id=16, display_name=u'System administrator', english_name=u'System administrator'),
                AbcRole(id=2, display_name=u'Project manager', english_name=u'Project manager'),
            ]
            for i in range(0, records_count):
                r_num = first_record_number + i
                self.fixture.db.session.add(StaffDepartmentInfo(
                    id=r_num,
                    unique_name='fake_staff_{}'.format(r_num),
                    display_name='Fake Staff group {}'.format(r_num),
                ))

                abc_department = AbcDepartmentInfo(
                    id=r_num,
                    unique_name='fake_service_{}'.format(r_num),
                    display_name='Fake ABC Service {}'.format(r_num),
                )
                for s in abc_scopes:
                    abc_department.scopes.append(s)
                for r in abc_roles:
                    abc_department.roles.append(r)
                self.fixture.db.session.add(abc_department)

            self.fixture.db.session.commit()

    def insert_multiple_records(self, owner_uid, uid, records_count=5000, versions_count=0, first_record_number=60000):
        with self.fixture.app.app_context():
            roles = ['OWNER', 'READER']
            abc_scopes = list(AbcScope.query.all())
            abc_roles = list(AbcRole.query.all())
            for i in range(0, records_count):
                r_num = first_record_number + i

                secret = self.client.create_secret('ololoken-test-{}'.format(i))
                self.client.create_token(secret, tvm_client_id=2000367)
                self.client.create_token(secret)

                # Чтобы вставить версии, выстави параметр versions_count
                for k in range(0, versions_count):
                    self.client.create_secret_version(
                        secret,
                        value=dict(key='value {}'.format(k)),
                    )

                self.fixture.db.session.add(ExternalRecord(
                    uid=uid,
                    external_type='staff',
                    external_id=r_num,
                ))
                self.client.add_user_role_to_secret(secret, random.choice(roles), staff_id=r_num)

                abc_scope = random.choice(abc_scopes)
                self.fixture.db.session.add(ExternalRecord(
                    uid=uid,
                    external_type='abc',
                    external_id=r_num,
                    external_scope_id=abc_scope.id,
                    external_role_id=0,
                ))
                abc_role = random.choice(abc_roles)
                self.fixture.db.session.add(ExternalRecord(
                    uid=uid,
                    external_type='abc',
                    external_id=r_num,
                    external_scope_id=0,
                    external_role_id=abc_role.id,
                ))
                self.client.add_user_role_to_secret(secret, random.choice(roles), abc_id=r_num, abc_scope=abc_scope.unique_name)
                self.client.add_user_role_to_secret(secret, random.choice(roles), abc_id=r_num, abc_role_id=abc_role.id)

            self.fixture.db.session.commit()

    def test_many_external_records_and_secrets(self):
        items_count = 200
        self.fill_abc_and_staff(items_count)
        with PermissionsMock(uid=100):
            self.insert_multiple_records(
                100, 101,
                records_count=items_count,
                versions_count=3,
            )

        with PermissionsMock(uid=100):
            self.assertResponseOk(
                self.client.list_secrets(
                    with_tvm_apps=True,
                    return_raw=True,
                )
            )

        with PermissionsMock(uid=101):
            self.assertResponseOk(
                self.client.list_secrets(
                    with_tvm_apps=True,
                    return_raw=True,
                )
            )

    def test_search_secret_by_uuid(self):
        items_count = 300
        self.fill_abc_and_staff(items_count)
        with PermissionsMock(uid=100):
            self.insert_multiple_records(
                100, 101,
                records_count=items_count,
                versions_count=5,
            )

        with PermissionsMock(uid=100):
            query = str(ULID(prefix='sec'))
            start = time.time()
            self.assertResponseOk(
                self.client.list_secrets(query=query, return_raw=True)
            )
            self.assertLess(time.time() - start, 1.0)
