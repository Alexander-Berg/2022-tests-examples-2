# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.differ import diff
from passport.backend.core.models.account import Account
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_no_default_phone_chosen,
    assert_no_phone_in_db,
    assert_no_secure_phone,
    assert_phone_has_been_bound,
    assert_phone_marked,
    assert_phone_unbound,
    assert_phonenumber_alias_missing,
    assert_phonenumber_alias_removed,
    assert_secure_phone_being_bound,
    assert_secure_phone_being_removed,
    assert_secure_phone_being_replaced,
    assert_secure_phone_bound,
    assert_simple_phone_being_bound,
    assert_simple_phone_being_bound_replace_secure,
    assert_simple_phone_being_securified,
    assert_simple_phone_bound,
    assert_simple_phone_replace_secure,
    build_account,
    build_account_from_session,
    build_current_phone_binding,
    build_phone_being_bound,
    build_phone_secured,
    build_unbound_phone_binding,
    predict_next_operation_id,
)
from passport.backend.core.models.phones.phones import SECURITY_IDENTITY
from passport.backend.core.processor import run_eav
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.utils.common import (
    deep_merge,
    generate_random_code,
)


UID = 2
PHONE_ID = 4
PHONE_NUMBER = u'+79026411724'
PHONE_ALIAS = u'79026411724'
PHONE_ALIAS2 = u'79259164525'
OPERATION_ID = 6

PHONE_ID_EXTRA = 8
PHONE_NUMBER_EXTRA = u'+79259164525'
OPERATION_ID_EXTRA = 10

CREATE_TIME = datetime(2000, 1, 1, 0, 0, 1)
BIND_TIME = datetime(2000, 1, 1, 0, 0, 4)
CONFIRM_TIME = datetime(2000, 1, 1, 0, 0, 5)
SECURE_TIME = datetime(2000, 1, 1, 0, 0, 6)

STARTED_TIME = datetime(2000, 1, 1, 0, 0, 2)
FINISHED_TIME = datetime(2000, 1, 1, 0, 0, 3)


class TestAssertNoPhoneInDb(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_ok(self):
        self._db_faker.serialize(
            blackbox_userinfo_response(
                uid=UID,
                phones=[],
                phone_operations=[],
            ),
        )
        assert_no_phone_in_db(self._db_faker, UID, PHONE_ID, PHONE_NUMBER)


class TestAssertPhonenumberAliasRemoved(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_ok(self):
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[],
            phone_operations=[],
            aliases={
                u'portal': u'login',
                u'phonenumber': PHONE_ALIAS,
            },
            attributes={u'account.enable_search_by_phone_alias': u'1'},
        )
        snapshot = account.snapshot()
        account.phonenumber_alias = None
        run_eav(snapshot, account, diff(snapshot, account))
        assert_phonenumber_alias_removed(self._db_faker, UID, PHONE_ALIAS)

    def test_never_exist(self):
        with assert_raises(AssertionError):
            build_account(db_faker=self._db_faker, uid=UID, aliases={u'portal': u'login'})
            assert_phonenumber_alias_removed(self._db_faker, UID, PHONE_ALIAS)


class TestAssertAccountHasPhonenumberAlias(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_has_this_alias(self):
        build_account(
            db_faker=self._db_faker,
            uid=UID,
            aliases={
                u'portal': u'login',
                u'phonenumber': PHONE_ALIAS,
            },
            attributes={u'account.enable_search_by_phone_alias': u'1'},
        )
        assert_account_has_phonenumber_alias(self._db_faker, UID, PHONE_ALIAS)

    def test_has_other_alias(self):
        with assert_raises(AssertionError):
            build_account(
                db_faker=self._db_faker,
                uid=UID,
                aliases={
                    u'portal': u'login',
                    u'phonenumber': PHONE_ALIAS,
                },
                attributes={u'account.enable_search_by_phone_alias': u'1'},
            )
            assert_account_has_phonenumber_alias(self._db_faker, UID, PHONE_ALIAS2)

    def test_has_not_alias(self):
        with assert_raises(AssertionError):
            build_account(db_faker=self._db_faker, uid=UID, aliases={u'portal': u'login'})
            assert_account_has_phonenumber_alias(self._db_faker, UID, PHONE_ALIAS)


class TestAssertPhonenumberAliasMissing(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_missing(self):
        build_account(db_faker=self._db_faker, uid=UID, aliases={u'portal': u'login'})
        assert_phonenumber_alias_missing(self._db_faker, UID)

    def test_not_missing(self):
        with assert_raises(AssertionError):
            build_account(
                db_faker=self._db_faker,
                uid=UID,
                aliases={
                    u'portal': u'login',
                    u'phonenumber': PHONE_ALIAS,
                },
                attributes={u'account.enable_search_by_phone_alias': u'1'},
            )
            assert_phonenumber_alias_missing(self._db_faker, UID)


@with_settings(
    BLACKBOX_ATTRIBUTES={},
)
class TestBuildAccount(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()
        self._blackbox_faker = FakeBlackbox()
        self._blackbox_faker.start()

        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self._fake_tvm_credentials_manager.start()

        self._blackbox = Blackbox(u'http://bla.ck.ox/')

    def tearDown(self):
        self._fake_tvm_credentials_manager.stop()
        self._blackbox_faker.stop()
        self._db_faker.stop()
        del self._db_faker
        del self._blackbox_faker
        del self._fake_tvm_credentials_manager

    def test_from_userinfo(self):
        account1 = build_account(
            db_faker=self._db_faker,
            blackbox_faker=self._blackbox_faker,
            uid=UID,
            **build_phone_being_bound(PHONE_ID, PHONE_NUMBER, OPERATION_ID)
        )

        user_info = self._blackbox.userinfo(uid=UID)
        account2 = Account().parse(user_info)

        self._assert_ok(account1, account2)

    def test_from_session(self):
        account1 = build_account_from_session(
            db_faker=self._db_faker,
            blackbox_faker=self._blackbox_faker,
            uid=UID,
            **build_phone_being_bound(PHONE_ID, PHONE_NUMBER, OPERATION_ID)
        )

        user_info = self._blackbox.sessionid(u'session_id', u'ip', u'host')
        account2 = Account().parse(user_info)

        self._assert_ok(account1, account2)

    def _assert_ok(self, account1, account2):
        expected_phone = {u'id': PHONE_ID, u'number': PHONE_NUMBER}
        expected_operation = {u'id': OPERATION_ID}
        assert_simple_phone_being_bound(
            account1,
            expected_phone,
            expected_operation,
        )
        assert_simple_phone_being_bound(
            account2,
            expected_phone,
            expected_operation,
        )
        assert_simple_phone_being_bound.check_db(
            self._db_faker,
            UID,
            expected_phone,
            expected_operation,
        )


class TestPhoneStateChecker(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_simple_phone_being_bound__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'created': CREATE_TIME,
            u'number': PHONE_NUMBER,
        }
        operation_attributes = {
            u'id': OPERATION_ID,
            u'phone_id': PHONE_ID,
            u'phone_number': PHONE_NUMBER,
            u'type': u'bind',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
        }
        phone_bindings = [build_unbound_phone_binding(PHONE_ID, PHONE_NUMBER)]
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_operations=[operation_attributes],
            phone_bindings=phone_bindings,
        )

        assert_simple_phone_being_bound(
            account,
            phone_attributes,
            operation_attributes,
        )
        assert_simple_phone_being_bound.check_db(
            self._db_faker,
            UID,
            phone_attributes,
            operation_attributes,
        )

    def test_simple_phone_being_bound__fail(self):
        with assert_raises(AssertionError):
            account = build_account(
                db_faker=self._db_faker,
                uid=UID,
                phones=[],
                phone_operations=[],
            )

            assert_simple_phone_being_bound(
                account,
                {u'id': PHONE_ID},
                {u'id': OPERATION_ID},
            )

    def test_secure_phone_being_bound__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'created': CREATE_TIME,
            u'number': PHONE_NUMBER,
        }
        operation_attributes = {
            u'id': OPERATION_ID,
            u'phone_id': PHONE_ID,
            u'security_identity': SECURITY_IDENTITY,
            u'type': u'bind',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
        }
        phone_bindings = [build_unbound_phone_binding(PHONE_ID, PHONE_NUMBER)]
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_operations=[operation_attributes],
            phone_bindings=phone_bindings,
        )

        assert_secure_phone_being_bound(
            account,
            phone_attributes,
            operation_attributes,
        )
        assert_secure_phone_being_bound.check_db(
            self._db_faker,
            UID,
            phone_attributes,
            operation_attributes,
        )

    def test_secure_phone_being_bound__fail(self):
        with assert_raises(AssertionError):
            account = build_account(
                db_faker=self._db_faker,
                uid=UID,
                phones=[],
                phone_operations=[],
            )

            assert_secure_phone_being_bound(
                account,
                {u'id': PHONE_ID},
                {u'id': OPERATION_ID},
            )

    def test_simple_phone_bound__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
        }
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_bindings=[
                {
                    'type': 'current',
                    'number': PHONE_NUMBER,
                    'phone_id': PHONE_ID,
                    'bound': BIND_TIME,
                },
            ],
        )

        assert_simple_phone_bound(account, phone_attributes)
        assert_simple_phone_bound.check_db(self._db_faker, UID, phone_attributes)
        assert_no_secure_phone(self._db_faker, UID)

    def test_simple_phone_bound__fail(self):
        with assert_raises(AssertionError):
            account = build_account(
                db_faker=self._db_faker,
                uid=UID,
                phones=[],
                phone_operations=[],
            )
            assert_simple_phone_bound(account, {u'id': PHONE_ID})

    def test_secure_phone_bound__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
            u'secured': SECURE_TIME,
        }
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_bindings=[
                {
                    'type': 'current',
                    'number': PHONE_NUMBER,
                    'phone_id': PHONE_ID,
                    'bound': BIND_TIME,
                },
            ],
            attributes={
                u'phones.secure': PHONE_ID,
            },
        )

        assert_secure_phone_bound(account, phone_attributes)
        assert_secure_phone_bound.check_db(self._db_faker, UID, phone_attributes)

    def test_simple_phone_being_securified__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
        }
        operation_attributes = {
            u'id': OPERATION_ID,
            u'phone_id': PHONE_ID,
            u'security_identity': SECURITY_IDENTITY,
            u'type': u'securify',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
        }
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_operations=[operation_attributes],
            phone_bindings=[
                {
                    'type': 'current',
                    'number': PHONE_NUMBER,
                    'phone_id': PHONE_ID,
                    'bound': BIND_TIME,
                },
            ],
        )

        assert_simple_phone_being_securified(
            account,
            phone_attributes,
            operation_attributes,
        )
        assert_simple_phone_being_securified.check_db(
            self._db_faker,
            UID,
            phone_attributes,
            operation_attributes,
        )

    def test_secure_phone_being_removed__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
            u'secured': SECURE_TIME,
        }
        operation_attributes = {
            u'id': OPERATION_ID,
            u'phone_id': PHONE_ID,
            u'security_identity': SECURITY_IDENTITY,
            u'type': u'remove',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
        }
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_bindings=[
                {
                    'type': 'current',
                    'number': PHONE_NUMBER,
                    'phone_id': PHONE_ID,
                    'bound': BIND_TIME,
                },
            ],
            phone_operations=[operation_attributes],
            attributes={
                u'phones.secure': PHONE_ID,
            },
        )

        assert_secure_phone_being_removed(
            account,
            phone_attributes,
            operation_attributes,
        )
        assert_secure_phone_being_removed.check_db(
            self._db_faker,
            UID,
            phone_attributes,
            operation_attributes,
        )

    def test_simple_phone_being_bound_to_replace_secure__ok(self):
        secure_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
            u'secured': SECURE_TIME,
        }
        secure_operation_attributes = {
            u'id': OPERATION_ID,
            u'phone_id': PHONE_ID,
            u'security_identity': SECURITY_IDENTITY,
            u'type': u'replace',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
            u'phone_id2': PHONE_ID_EXTRA,
        }
        secure_phone_bindings = [build_current_phone_binding(PHONE_ID, PHONE_NUMBER, BIND_TIME)]
        simple_attributes = {
            u'id': PHONE_ID_EXTRA,
            u'number': PHONE_NUMBER_EXTRA,
            u'created': CREATE_TIME,
        }
        simple_operation_attributes = {
            u'id': OPERATION_ID_EXTRA,
            u'phone_id': PHONE_ID_EXTRA,
            u'phone_number': PHONE_NUMBER_EXTRA,
            u'type': u'bind',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
            u'phone_id2': PHONE_ID,
        }
        simple_phone_bindings = [build_unbound_phone_binding(PHONE_ID_EXTRA, PHONE_NUMBER_EXTRA)]
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[secure_attributes, simple_attributes],
            phone_bindings=secure_phone_bindings + simple_phone_bindings,
            phone_operations=[secure_operation_attributes, simple_operation_attributes],
            attributes={
                u'phones.secure': PHONE_ID,
            },
        )

        assert_simple_phone_being_bound_replace_secure(
            account,
            simple_attributes,
            simple_operation_attributes,
        )
        assert_simple_phone_being_bound_replace_secure.check_db(
            self._db_faker,
            UID,
            simple_attributes,
            simple_operation_attributes,
        )
        assert_secure_phone_being_replaced(
            account,
            secure_attributes,
            secure_operation_attributes,
        )
        assert_secure_phone_being_replaced.check_db(
            self._db_faker,
            UID,
            secure_attributes,
            secure_operation_attributes,
        )

    def test_simple_phone_replacing_secure__ok(self):
        secure_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
            u'secured': SECURE_TIME,
        }
        secure_operation_attributes = {
            u'id': OPERATION_ID,
            u'phone_id': PHONE_ID,
            u'security_identity': SECURITY_IDENTITY,
            u'type': u'replace',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
            u'phone_id2': PHONE_ID_EXTRA,
        }
        simple_attributes = {
            u'id': PHONE_ID_EXTRA,
            u'number': PHONE_NUMBER_EXTRA,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
        }
        simple_operation_attributes = {
            u'id': OPERATION_ID_EXTRA,
            u'phone_id': PHONE_ID_EXTRA,
            u'phone_number': PHONE_NUMBER_EXTRA,
            u'type': u'mark',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
            u'phone_id2': PHONE_ID,
        }
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[secure_attributes, simple_attributes],
            phone_operations=[secure_operation_attributes, simple_operation_attributes],
            phone_bindings=[
                {
                    'type': 'current',
                    'number': PHONE_NUMBER,
                    'phone_id': PHONE_ID,
                    'bound': BIND_TIME,
                },
                {
                    'type': 'current',
                    'number': PHONE_NUMBER_EXTRA,
                    'phone_id': PHONE_ID_EXTRA,
                    'bound': BIND_TIME,
                },
            ],
            attributes={
                u'phones.secure': PHONE_ID,
            },
        )

        assert_simple_phone_replace_secure(
            account,
            simple_attributes,
            simple_operation_attributes,
        )
        assert_simple_phone_replace_secure.check_db(
            self._db_faker,
            UID,
            simple_attributes,
            simple_operation_attributes,
        )

    def test_phone_unbound__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'confirmed': CONFIRM_TIME,
        }
        phone_bindings = [build_unbound_phone_binding(PHONE_ID, PHONE_NUMBER)]
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_bindings=phone_bindings,
        )

        assert_phone_unbound(account, phone_attributes)
        assert_phone_unbound.check_db(self._db_faker, UID, phone_attributes)

    def test_phone_marked__ok(self):
        phone_attributes = {
            u'id': PHONE_ID,
            u'number': PHONE_NUMBER,
            u'created': CREATE_TIME,
            u'bound': BIND_TIME,
            u'confirmed': CONFIRM_TIME,
            u'secured': SECURE_TIME,
        }
        operation_attributes = {
            u'id': OPERATION_ID,
            u'phone_id': PHONE_ID,
            u'phone_number': PHONE_NUMBER,
            u'type': u'mark',
            u'started': STARTED_TIME,
            u'finished': FINISHED_TIME,
        }
        account = build_account(
            db_faker=self._db_faker,
            uid=UID,
            phones=[phone_attributes],
            phone_bindings=[
                {
                    'type': 'current',
                    'number': PHONE_NUMBER,
                    'phone_id': PHONE_ID,
                    'bound': BIND_TIME,
                },
            ],
            phone_operations=[operation_attributes],
        )

        assert_phone_marked(
            account,
            phone_attributes,
            operation_attributes,
        )
        assert_phone_marked.check_db(
            self._db_faker,
            UID,
            phone_attributes,
            operation_attributes,
        )


class TestBuildPhone(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_build_phone_secured(self):
        account = build_account(
            db_faker=self._db_faker,
            **deep_merge(
                dict(
                    uid=UID,
                    login=u'test',
                    aliases={u'portal': u'test'},
                ),
                build_phone_secured(
                    PHONE_ID,
                    PHONE_NUMBER,
                    is_alias=True,
                ),
            )
        )

        assert_secure_phone_bound(
            account,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )
        assert_secure_phone_bound.check_db(
            self._db_faker,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER},
        )

        ok_(not account.phones.default_id)
        assert_no_default_phone_chosen(self._db_faker, UID)

        assert_phone_has_been_bound(self._db_faker, UID, PHONE_NUMBER, times=1)


class TestPredictNextOperationId(TestCase):
    def setUp(self):
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        del self._db_faker

    def test_ok(self):
        account = default_account(uid=UID)
        snapshot = account.snapshot()
        expected_operation_id = predict_next_operation_id(UID)

        phone = account.phones.create(PHONE_NUMBER)
        phone.create_operation(u'bind')
        run_eav(snapshot, account, diff(snapshot, account))

        eq_(phone.operation.id, expected_operation_id)


class TestCodeGeneratorFaker(TestCase):
    def setUp(self):
        self._code_faker = CodeGeneratorFaker()
        self._code_faker.start()

    def tearDown(self):
        self._code_faker.stop()
        del self._code_faker

    def test_default(self):
        eq_(generate_random_code(4), self._code_faker.DEFAULT_CONFIRMATION_CODE)

    def test_set_return_value(self):
        self._code_faker.set_return_value('3232')
        eq_(generate_random_code(4), '3232')

    def test_call_count(self):
        generate_random_code(4)
        generate_random_code(4)
        eq_(self._code_faker.call_count, 2)
