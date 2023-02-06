# -*- coding: utf-8 -*-

from library.python.vault_client import VaultClient
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.builders import (
    get_abc,
    get_staff,
)
from passport.backend.vault.api.db import get_db
from passport.backend.vault.api.models import (
    ExternalRecord,
    Roles,
    TvmAppInfo,
    TvmGrants,
    UserInfo,
)
from passport.backend.vault.api.test.fake_abc import (
    FakeABC,
    TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE,
    TEST_ABC_GET_ALL_PERSONS_RESPONSE,
    TEST_ABC_GET_ALL_ROLES_RESPONSE,
    TEST_ABC_GET_ALL_TVM_APPS_RESPONSE,
)
from passport.backend.vault.api.test.fake_staff import (
    FakeStaff,
    TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE,
    TEST_STAFF_GET_ALL_PERSONS_RESPONSE,
)
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.test.secrets_mock import SecretsMock
from passport.backend.vault.api.test.test_client import TestClient
from passport.backend.vault.api.test.uuid_mock import UuidMock
from sqlalchemy.exc import IntegrityError


TEST_UID = 100
TEST_DELEGATION_TOKEN = 'gcwCk8kPz65Y54HnTrDKbjAN0FXAJPlnJVzpJtpRhwE'


class DbFixture(object):
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.native_client = TestClient(app)
        self.client = VaultClient(
            native_client=self.native_client,
            user_ticket='user_ticket',
            service_ticket='service_ticket',
        )
        self.db = get_db()

    def __enter__(self):
        self.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    def commit(self):
        self.rollback()
        self.create_tables()

    def rollback(self):
        self.drop_tables()

    def create_tables(self):
        self.db.create_all(app=self.app)

    def fill_staff(self):
        with FakeStaff() as faker:
            faker.set_response_value('get_all_persons', TEST_STAFF_GET_ALL_PERSONS_RESPONSE)
            faker.set_response_value('get_all_departments', TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE)
            with self.app.app_context():
                staff_persons = get_staff(self.config).get_all_persons()
                staff_departments = get_staff(self.config).get_all_departments()
                ExternalRecord.insert_staff(staff_persons, staff_departments)

    def fill_abc(self):
        with FakeABC() as faker:
            faker.set_response_value('get_all_persons', TEST_ABC_GET_ALL_PERSONS_RESPONSE)
            faker.set_response_value('get_all_roles', TEST_ABC_GET_ALL_ROLES_RESPONSE)
            faker.set_response_value('get_all_departments', TEST_ABC_GET_ALL_DEPARTMENTS_RESPONSE)
            with self.app.app_context():
                (
                    abc_persons,
                    abc_scopes,
                    abc_services_scopes,
                    abc_roles,
                    abc_services_roles,
                ) = get_abc(self.config).get_all_persons_and_scopes()
                abc_departments = get_abc(self.config).get_all_departments()
                ExternalRecord.insert_abc(
                    abc_persons,
                    abc_scopes,
                    abc_services_scopes,
                    abc_departments,
                    abc_roles,
                    abc_services_roles,
                )

    def fill_tvm_apps(self):
        with FakeABC() as faker:
            faker.set_response_value('get_all_tvm_apps', TEST_ABC_GET_ALL_TVM_APPS_RESPONSE)
            with self.app.app_context():
                tvm_apps = get_abc(self.config).get_all_tvm_apps()
                TvmAppInfo.insert_tvm_apps(tvm_apps)

    def add_user(self, uid, **kwargs):
        with self.app.app_context():
            self.db.session.add(
                UserInfo(uid=uid, **kwargs),
            )
            self.db.session.commit()

    def assign_abc_role_or_scope_to_uid(self, uid, abc_id, abc_role_id=0, abc_scope_id=0):
        with self.app.app_context():
            self.db.session.add(
                ExternalRecord(
                    external_type='abc',
                    uid=uid,
                    external_id=abc_id,
                    external_scope_id=abc_scope_id,
                    external_role_id=abc_role_id,
                ),
            )
            self.db.session.commit()

    def fill_grants(self):
        with self.app.app_context():
            with TimeMock():
                try:
                    TvmGrants.grant(1, u'Default external app')
                except IntegrityError:
                    pass

    def insert_data(self, skip_staff=False, skip_abc=False, skip_tvm=False, skip_grants=False):
        if not skip_staff:
            self.fill_staff()
        if not skip_abc:
            self.fill_abc()
        if not skip_tvm:
            self.fill_tvm_apps()
        if not skip_grants:
            self.fill_grants()

        with self.app.app_context():
            with TimeMock() as time_mock:
                with UuidMock():
                    with PermissionsMock(uid=100):
                        secret_uuid_1 = self.client.create_secret(name='secret_1')
                        secret_1_versions = []
                        time_mock.tick()
                        for _ in range(3):
                            secret_1_versions.append(
                                self.client.create_secret_version(
                                    secret_uuid=secret_uuid_1,
                                    value=[
                                        {'key': 'password', 'value': '123'},
                                    ],
                                ),
                            )
                            time_mock.tick()
                        secret_uuid_2 = self.client.create_secret(name='secret_2')
                        secret_2_versions = []
                        time_mock.tick()
                        for _ in range(4):
                            secret_2_versions.append(
                                self.client.create_secret_version(
                                    secret_uuid=secret_uuid_2,
                                    value=[{'key': 'password', 'value': '123'}],
                                ),
                            )
                            time_mock.tick()
                    with PermissionsMock(uid=101):
                        secret_uuid_3 = self.client.create_secret(name='secret_3')
                        time_mock.tick()
                        self.client.add_user_role_to_secret(
                            secret_uuid=secret_uuid_3,
                            role=Roles.READER.name,
                            staff_id=38096,
                        )
                        for _ in range(3):
                            self.client.create_secret_version(
                                secret_uuid=secret_uuid_3,
                                value=[{'key': 'password', 'value': '123'}],
                            )
                            time_mock.tick()
                        secret_uuid_4 = self.client.create_secret(name='secret_4')
                        time_mock.tick()
                        self.client.add_user_role_to_secret(
                            secret_uuid=secret_uuid_4,
                            role=Roles.READER.name,
                            abc_id=14,
                        )
                        for _ in range(4):
                            self.client.create_secret_version(
                                secret_uuid=secret_uuid_4,
                                value=[{'key': 'password', 'value': '123'}],
                            )
                            time_mock.tick()
                    with PermissionsMock(uid=102, fixture=self, staff_groups=[574]):
                        with SecretsMock(TEST_DELEGATION_TOKEN):
                            self.client.create_token(
                                secret_uuid=secret_uuid_3,
                                signature='666',
                                return_raw=True,
                            )

                with UuidMock(base_value=4000000):
                    with PermissionsMock(uid=100):
                        bundle_uuid_1 = self.client.create_bundle(
                            name='passport_top_bundle_1',
                            comment='All secrets',
                        )

                        self.client.create_bundle_version(
                            bundle_uuid=bundle_uuid_1,
                            secret_versions=[
                                secret_1_versions[1],
                                secret_2_versions[2],
                            ],
                        )

                        self.client.create_bundle(
                            name='passport_top_bundle_2',
                            comment='All secrets 2',
                        )

    def drop_tables(self):
        self.db.drop_all(app=self.app)
