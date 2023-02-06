# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)
from functools import partial

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.dbmanager.manager import safe_execute_queries
from passport.backend.core.mailer.faker.mail_utils import create_native_email
from passport.backend.core.models.phones.faker import (
    assert_no_default_phone_chosen,
    assert_no_phone_in_db,
    assert_no_secure_phone,
    assert_phone_unbound,
    assert_phonenumber_alias_missing,
    assert_phonenumber_alias_removed,
    assert_secure_phone_being_removed,
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    build_account,
    build_mark_operation,
    build_phone_being_bound_replaces_secure_operations,
    build_phone_bound,
    build_phone_secured,
    build_phone_unbound,
    build_remove_operation,
    build_secure_phone_being_bound,
    build_simple_replaces_secure_operations,
)
from passport.backend.core.models.phones.phones import (
    PhoneChangeSet,
    SECURITY_IDENTITY,
)
from passport.backend.core.runner.context_managers import UPDATE
from passport.backend.core.serializers.eav.exceptions import EavDeletedObjectNotFound
from passport.backend.core.serializers.eav.query import EavInsertPhoneOperationCreatedQuery
from passport.backend.core.test.consts import (
    TEST_PASSWORD_HASH1,
    TEST_SOCIAL_LOGIN1,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.bit_vector import PhoneOperationFlags
from passport.backend.core.yasms.test.emails import (
    assert_user_notified_about_dealiasify,
    assert_user_notified_about_secure_phone_removed_with_quarantine,
    assert_user_notified_about_secure_phone_replaced,
)
from passport.backend.dbscripts.phone_harvester.base import (
    harvest_account,
    harvest_expired_phone_operations,
    harvest_uids,
)
from passport.backend.dbscripts.test.base_phone_harvester import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_ACTION1,
    TEST_BLACKBOX_URL1,
    TEST_EMAIL1,
    TEST_EMAIL2,
    TEST_ENVIRONMENT1,
    TEST_FIRSTNAME1,
    TEST_FIRSTNAME2,
    TEST_LOGIN1,
    TEST_LOGIN2,
    TEST_OPERATION_ID1,
    TEST_OPERATION_ID2,
    TEST_OPERATION_ID3,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_ID3,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_SHORT_OPERATION_TTL,
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.utils.common import deep_merge


def _build_account(db_faker, **kwargs):
    kwargs = deep_merge(
        {
            'uid': TEST_UID1,
            'login': TEST_LOGIN1,
            'firstname': TEST_FIRSTNAME1,
            'emails': [create_native_email(*TEST_EMAIL1.split('@'))],
        },
        kwargs,
        {
            'aliases': {'portal': TEST_LOGIN1},
        }
    )
    return build_account(db_faker, **kwargs)


@with_settings_hosts()
class TestHarvestExpiredPhoneOperations(TestCase):
    def test_no_operations(self):
        account = self._build_account(phones=[], phone_operations=[])

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())
        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})

    def test_operation_in_quarantine_and_not_expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                self._build_remove_operation_quarantined(
                    finished=datetime.now() + timedelta(hours=1),
                ),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})

        phone = account.phones.by_id(TEST_PHONE_ID1)
        logical_op = phone.get_logical_operation(self._statbox)
        ok_(logical_op.in_quarantine)
        ok_(not logical_op.is_expired)

    def test_removal_secure__not_in_quarantine_and_expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                ),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='remove_secure',
            ),
        ])

        phone_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,
            phone_fmt('number'): TEST_PHONE_NUMBER1.e164,
            op_fmt('type'): 'remove',
            op_fmt('security_identity'): str(SECURITY_IDENTITY),
            op_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_removal_secure__in_quarantine_and_expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    is_alias=True,
                ),
                self._build_remove_operation_quarantined(),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet(unbound_numbers={TEST_PHONE_NUMBER1.e164}))

        ok_(not account.phones.by_number(TEST_PHONE_NUMBER1))
        ok_(not account.phones.secure)

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )
        assert_no_secure_phone(db_faker=self._db_faker, uid=TEST_UID1)

        assert_phonenumber_alias_missing(db_faker=self._db_faker, uid=TEST_UID1)
        assert_phonenumber_alias_removed(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            alias=TEST_PHONE_NUMBER1.digital,
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('phonenumber_alias_removed', uid=str(TEST_UID1)),
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='deleted',
                old=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID1),
            ),
            self._statbox_faker.entry('phonenumber_alias_subscription_removed'),
            self._statbox_faker.entry('secure_phone_removed'),
        ])

        phone_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,

            phone_fmt('number'): TEST_PHONE_NUMBER1.e164,
            phone_fmt('action'): 'deleted',
            'phones.secure': u'0',

            'alias.phonenumber.rm': TEST_PHONE_NUMBER1.international,

            op_fmt('type'): 'remove',
            op_fmt('security_identity'): str(SECURITY_IDENTITY),
            op_fmt('action'): 'deleted',
        })

        assert_user_notified_about_dealiasify(
            mailer_faker=self._mailer_faker,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
            portal_email=TEST_EMAIL1,
            phonenumber_alias=TEST_PHONE_NUMBER1.digital,
        )

    def test_removal_secure__in_quarantine_and_expired__2fa(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    is_alias=True,
                ),
                self._build_remove_operation_quarantined(),
                {'attributes': {u'account.2fa_on': True}},
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='remove_secure',
            ),
        ])

        phone_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,
            phone_fmt('number'): TEST_PHONE_NUMBER1.e164,
            op_fmt('type'): 'remove',
            op_fmt('security_identity'): str(SECURITY_IDENTITY),
            op_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_removal_secure__in_quarantine_and_expired__sms_2fa(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    is_alias=True,
                ),
                self._build_remove_operation_quarantined(),
                {'attributes': {u'account.sms_2fa_on': True}},
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='remove_secure',
            ),
        ])

        phone_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,
            phone_fmt('number'): TEST_PHONE_NUMBER1.e164,
            op_fmt('type'): 'remove',
            op_fmt('security_identity'): str(SECURITY_IDENTITY),
            op_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_removal_secure__in_quarantine_and_expired__passwordless_account(self):
        account = build_account(
            self._db_faker,
            **deep_merge(
                dict(
                    aliases=dict(social=TEST_SOCIAL_LOGIN1),
                    login=TEST_SOCIAL_LOGIN1,
                    crypt_password=None,
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                self._build_remove_operation_quarantined(password_verified=None),
            )
        )

        self._harvest_expired_phone_operations(account)

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )
        assert_no_secure_phone(db_faker=self._db_faker, uid=TEST_UID1)

    def test_not_bound_replaces_secure__not_in_quarantine_and_expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_phone_unbound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID1,
                    being_bound_operation_id=TEST_OPERATION_ID2,
                    being_bound_phone_id=TEST_PHONE_ID2,
                    being_bound_phone_number=TEST_PHONE_NUMBER2.e164,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                ),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
        )

        ok_(not account.phones.by_number(TEST_PHONE_NUMBER2))
        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID2,
            phone_number=TEST_PHONE_NUMBER2.e164,
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='replace_secure_phone_with_nonbound_phone',
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        phone2_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op2_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,

            phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
            op1_fmt('type'): 'replace',
            op1_fmt('security_identity'): str(SECURITY_IDENTITY),
            op1_fmt('action'): 'deleted',

            phone2_fmt('number'): TEST_PHONE_NUMBER2.e164,
            phone2_fmt('action'): 'deleted',
            op2_fmt('type'): 'bind',
            op2_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
            op2_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_not_bound_replaces_secure__in_quarantine_and_expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    is_alias=True,
                ),
                build_phone_unbound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                self._build_phone_being_bound_replaces_secure_operations_quarantined(),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(
            change_set,
            PhoneChangeSet(
                bound_numbers={TEST_PHONE_NUMBER2.e164},
                unbound_numbers={TEST_PHONE_NUMBER1.e164},
                secured_number=TEST_PHONE_NUMBER2.e164,
            ),
        )

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID2},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )

        ok_(not account.phones.by_number(TEST_PHONE_NUMBER1))
        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('phonenumber_alias_removed'),
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='updated',
                old=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID1),
                new=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                new_entity_id=str(TEST_PHONE_ID2),
            ),
            self._statbox_faker.entry('phonenumber_alias_subscription_removed'),
            self._statbox_faker.entry(
                'simple_phone_bound',
                number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                phone_id=str(TEST_PHONE_ID2),
            ),
            self._statbox_faker.entry(
                'secure_phone_replaced',
                old_secure_number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_secure_phone_id=str(TEST_PHONE_ID1),
                new_secure_number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                new_secure_phone_id=str(TEST_PHONE_ID2),
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        phone2_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op2_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,

            phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
            phone1_fmt('action'): 'deleted',
            op1_fmt('type'): 'replace',
            op1_fmt('security_identity'): str(SECURITY_IDENTITY),
            op1_fmt('action'): 'deleted',

            'alias.phonenumber.rm': TEST_PHONE_NUMBER1.international,

            phone2_fmt('number'): TEST_PHONE_NUMBER2.e164,
            phone2_fmt('action'): 'changed',
            phone2_fmt('confirmed'): TimeNow(),
            phone2_fmt('bound'): TimeNow(),
            phone2_fmt('secured'): TimeNow(),
            op2_fmt('type'): 'bind',
            op2_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
            op2_fmt('action'): 'deleted',

            'phones.secure': str(TEST_PHONE_ID2),
        })

        assert_user_notified_about_dealiasify(
            mailer_faker=self._mailer_faker,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
            portal_email=TEST_EMAIL1,
            phonenumber_alias=TEST_PHONE_NUMBER1.digital,
        )

    def test_not_bound_replaces_secure__in_quarantine_and_expired__passwordless_account(self):
        account = build_account(
            db_faker=self._db_faker,
            **deep_merge(
                dict(
                    aliases=dict(social=TEST_SOCIAL_LOGIN1),
                    login=TEST_SOCIAL_LOGIN1,
                    crypt_password=None,
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_phone_unbound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                self._build_phone_being_bound_replaces_secure_operations_quarantined(
                    password_verified=None,
                ),
            )
        )

        self._harvest_expired_phone_operations(account)

        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )

    def test_bound_replaces_secure__not_in_quarantine_and_expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_phone_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_simple_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID1,
                    simple_operation_id=TEST_OPERATION_ID2,
                    simple_phone_id=TEST_PHONE_ID2,
                    simple_phone_number=TEST_PHONE_NUMBER2.e164,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                ),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
        )

        assert_simple_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID2},
        )
        assert_simple_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='replace_secure_phone_with_bound_phone',
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        phone2_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op2_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,

            phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
            op1_fmt('type'): 'replace',
            op1_fmt('security_identity'): str(SECURITY_IDENTITY),
            op1_fmt('action'): 'deleted',

            phone2_fmt('number'): TEST_PHONE_NUMBER2.e164,
            op2_fmt('type'): 'mark',
            op2_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
            op2_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_bound_replaces_secure__in_quarantine_and_expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    is_alias=True,
                ),
                build_phone_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                self._build_simple_replaces_secure_operations_quarantined(),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(
            change_set,
            PhoneChangeSet(
                unbound_numbers={TEST_PHONE_NUMBER1.e164},
                secured_number=TEST_PHONE_NUMBER2.e164,
            ),
        )

        ok_(not account.phones.by_number(TEST_PHONE_NUMBER1))
        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID2},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry('phonenumber_alias_removed'),
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='updated',
                old=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID1),
                new=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                new_entity_id=str(TEST_PHONE_ID2),
            ),
            self._statbox_faker.entry('phonenumber_alias_subscription_removed'),
            self._statbox_faker.entry(
                'secure_phone_replaced',
                old_secure_number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_secure_phone_id=str(TEST_PHONE_ID1),
                new_secure_number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                new_secure_phone_id=str(TEST_PHONE_ID2),
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        phone2_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op2_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,

            phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
            phone1_fmt('action'): 'deleted',
            op1_fmt('type'): 'replace',
            op1_fmt('security_identity'): str(SECURITY_IDENTITY),
            op1_fmt('action'): 'deleted',

            'alias.phonenumber.rm': TEST_PHONE_NUMBER1.international,

            phone2_fmt('number'): TEST_PHONE_NUMBER2.e164,
            phone2_fmt('action'): 'changed',
            phone2_fmt('confirmed'): TimeNow(),
            phone2_fmt('secured'): TimeNow(),
            op2_fmt('type'): 'mark',
            op2_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
            op2_fmt('action'): 'deleted',

            'phones.secure': str(TEST_PHONE_ID2),
        })

        assert_user_notified_about_dealiasify(
            mailer_faker=self._mailer_faker,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
            portal_email=TEST_EMAIL1,
            phonenumber_alias=TEST_PHONE_NUMBER1.digital,
        )

    def test_bound_replaces_secure__in_quarantine_and_expired__passwordless_account(self):
        account = build_account(
            self._db_faker,
            **deep_merge(
                dict(
                    aliases=dict(social=TEST_SOCIAL_LOGIN1),
                    login=TEST_SOCIAL_LOGIN1,
                    crypt_password=None,
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_phone_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                self._build_simple_replaces_secure_operations_quarantined(
                    password_verified=None,
                ),
            )
        )

        self._harvest_expired_phone_operations(account)

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )

        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )

    def test_secure_bind_operation__expired(self):
        account = self._build_account(
            **build_secure_phone_being_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER1.e164,
                operation_id=TEST_OPERATION_ID1,
                operation_started=datetime.now() - timedelta(hours=2),
                operation_finished=datetime.now() - timedelta(hours=1),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        ok_(not account.phones.by_number(TEST_PHONE_NUMBER1.e164))
        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='secure_bind',
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,
            phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
            phone1_fmt('action'): 'deleted',
            op1_fmt('type'): 'bind',
            op1_fmt('security_identity'): str(SECURITY_IDENTITY),
            op1_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_mark_operation__expired(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_mark_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                ),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet())

        assert_secure_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID1},
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='mark',
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,
            phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
            op1_fmt('type'): 'mark',
            op1_fmt('security_identity'): TEST_PHONE_NUMBER1.digital,
            op1_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def test_many_operations(self):
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                self._build_remove_operation_quarantined(),
                build_phone_bound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_mark_operation(
                    operation_id=TEST_OPERATION_ID2,
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                ),
            )
        )

        change_set = self._harvest_expired_phone_operations(account)

        eq_(change_set, PhoneChangeSet(unbound_numbers={TEST_PHONE_NUMBER1.e164}))

        ok_(not account.phones.by_number(TEST_PHONE_NUMBER1))
        ok_(not account.phones.secure)

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )
        assert_no_secure_phone(db_faker=self._db_faker, uid=TEST_UID1)

        assert_simple_phone_bound(
            account=account,
            phone_attributes={'id': TEST_PHONE_ID2},
        )
        assert_simple_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'phone_operation_cancelled',
                operation_type='mark',
                operation_id=str(TEST_OPERATION_ID2),
            ),
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='deleted',
                old=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID1),
            ),
            self._statbox_faker.entry('secure_phone_removed'),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        phone2_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op2_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        self._event_logger_faker.assert_events_are_logged({
            'action': TEST_ACTION1,

            phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
            phone1_fmt('action'): 'deleted',
            'phones.secure': u'0',

            op1_fmt('type'): 'remove',
            op1_fmt('security_identity'): str(SECURITY_IDENTITY),
            op1_fmt('action'): 'deleted',

            phone2_fmt('number'): TEST_PHONE_NUMBER2.e164,
            op2_fmt('type'): 'mark',
            op2_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
            op2_fmt('action'): 'deleted',
        })

        eq_(self._mailer_faker.messages, [])

    def _harvest_expired_phone_operations(self, account):
        with UPDATE(account, TEST_ENVIRONMENT1, {'action': TEST_ACTION1}):
            change_set = harvest_expired_phone_operations(account, self._statbox)
        self._statbox.dump_stashes()
        return change_set

    def _build_account(self, **kwargs):
        return _build_account(db_faker=self._db_faker, **kwargs)

    def _build_remove_operation_quarantined(
        self,
        finished=None,
        password_verified=Undefined,
    ):
        if password_verified is Undefined:
            password_verified = datetime.now()

        if finished is None:
            finished = datetime.now() - timedelta(hours=1)

        flags = PhoneOperationFlags()
        flags.in_quarantine = True

        return build_remove_operation(
            operation_id=TEST_OPERATION_ID1,
            phone_id=TEST_PHONE_ID1,
            password_verified=password_verified,
            code_value=None,
            code_send_count=0,
            code_last_sent=None,
            started=datetime.now() - timedelta(hours=2),
            finished=finished,
            flags=flags,
        )

    def _build_phone_being_bound_replaces_secure_operations_quarantined(
        self,
        password_verified=Undefined,
    ):
        if password_verified is Undefined:
            password_verified = datetime.now()

        flags = PhoneOperationFlags()
        flags.in_quarantine = True

        return build_phone_being_bound_replaces_secure_operations(
            secure_operation_id=TEST_OPERATION_ID1,
            secure_phone_id=TEST_PHONE_ID1,
            being_bound_operation_id=TEST_OPERATION_ID2,
            being_bound_phone_id=TEST_PHONE_ID2,
            being_bound_phone_number=TEST_PHONE_NUMBER2.e164,
            started=datetime.now() - timedelta(hours=2),
            finished=datetime.now() - timedelta(hours=1),
            secure_code_value=None,
            secure_code_send_count=0,
            secure_code_last_sent=None,
            being_bound_code_confirmed=datetime.now(),
            password_verified=password_verified,
            flags=flags,
        )

    def _build_simple_replaces_secure_operations_quarantined(self, password_verified=Undefined):
        if password_verified is Undefined:
            password_verified = datetime.now()

        flags = PhoneOperationFlags()
        flags.in_quarantine = True

        return build_simple_replaces_secure_operations(
            secure_operation_id=TEST_OPERATION_ID1,
            secure_phone_id=TEST_PHONE_ID1,
            simple_operation_id=TEST_OPERATION_ID2,
            simple_phone_id=TEST_PHONE_ID2,
            simple_phone_number=TEST_PHONE_NUMBER2.e164,
            started=datetime.now() - timedelta(hours=2),
            finished=datetime.now() - timedelta(hours=1),
            password_verified=password_verified,
            simple_code_confirmed=datetime.now(),
            secure_code_value=None,
            secure_code_send_count=0,
            secure_code_last_sent=None,
            flags=flags,
        )


@with_settings_hosts(
    BLACKBOX_URL=TEST_BLACKBOX_URL1,
    YASMS_PHONE_BINDING_LIMIT=1,
    YASMS_MARK_OPERATION_TTL=TEST_SHORT_OPERATION_TTL.total_seconds(),
    DB_RETRIES=1,
)
class TestHarvestUids(TestCase):
    def test_no_uids(self):
        harvest_uids([], TEST_ENVIRONMENT1)

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})
        eq_(self._mailer_faker.messages, [])

    def test_unknown_uid(self):
        self._blackbox_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([{'uid': None}]),
        )
        build_account(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    phone_admitted=datetime.now(),
                    is_default=True,
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                ),
            )
        )

        harvest_uids([TEST_UID1], TEST_ENVIRONMENT1)

        self._statbox_faker.assert_has_written([])
        self._event_logger_faker.assert_events_are_logged({})
        eq_(self._mailer_faker.messages, [])

        assert_no_secure_phone(
            db_faker=self._db_faker,
            uid=TEST_UID1,
        )
        assert_no_default_phone_chosen(
            db_faker=self._db_faker,
            uid=TEST_UID1,
        )
        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )

    def test_phone_number_hits_binding_limit(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        account1_args = dict(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            firstname=TEST_FIRSTNAME1,
            aliases={'portal': TEST_LOGIN1},
            emails=[create_native_email(*TEST_EMAIL1.split('@'))],
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_phone_unbound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID1,
                    being_bound_operation_id=TEST_OPERATION_ID2,
                    being_bound_phone_id=TEST_PHONE_ID2,
                    being_bound_phone_number=TEST_PHONE_NUMBER2.e164,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                    secure_code_value=None,
                    secure_code_send_count=0,
                    secure_code_last_sent=None,
                    being_bound_code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                    flags=phone_operation_flags,
                ),
            )
        )
        response1 = blackbox_userinfo_response_multiple([account1_args])
        self._db_faker.serialize(response1)

        account2_args = dict(
            uid=TEST_UID2,
            login=TEST_LOGIN2,
            firstname=TEST_FIRSTNAME2,
            emails=[create_native_email(*TEST_EMAIL2.split('@'))],
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID3,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                    is_alias=True,
                ),
                {'aliases': {'portal': TEST_LOGIN2}},
            )
        )
        response2 = blackbox_userinfo_response_multiple([account2_args])
        self._db_faker.serialize(response2)

        self._blackbox_faker.set_response_side_effect(
            'userinfo',
            [response1, response2],
        )

        self._blackbox_faker.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    'uid': TEST_UID1,
                    'type': 'current',
                    'number': TEST_PHONE_NUMBER2.e164,
                    'phone_id': TEST_PHONE_ID2,
                    'bound': datetime.now(),
                },
                {
                    'uid': TEST_UID2,
                    'type': 'current',
                    'number': TEST_PHONE_NUMBER2.e164,
                    'phone_id': TEST_PHONE_ID3,
                    'bound': datetime.now() - timedelta(hours=1),
                },
            ]),
        )

        harvest_uids([TEST_UID1], TEST_ENVIRONMENT1)

        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )
        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )

        assert_phone_unbound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID2,
            phone_attributes={'id': TEST_PHONE_ID3},
        )
        assert_phonenumber_alias_missing(db_faker=self._db_faker, uid=TEST_UID2)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='updated',
                old=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID1),
                new=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                new_entity_id=str(TEST_PHONE_ID2),
            ),
            self._statbox_faker.entry(
                'simple_phone_bound',
                number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                phone_id=str(TEST_PHONE_ID2),
            ),
            self._statbox_faker.entry(
                'secure_phone_replaced',
                old_secure_number=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_secure_phone_id=str(TEST_PHONE_ID1),
                new_secure_number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                new_secure_phone_id=str(TEST_PHONE_ID2),
            ),
            self._statbox_faker.entry(
                'phone_acquired_before_unbinding',
                uid=str(TEST_UID2),
                number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                phone_id=str(TEST_PHONE_ID3),
                operation_id='3',
            ),
            self._statbox_faker.entry(
                'phonenumber_alias_removed',
                _exclude={'consumer'},
                uid=str(TEST_UID2),
            ),
            self._statbox_faker.entry(
                'secure_phone_modified',
                _exclude={'consumer'},
                operation='deleted',
                old=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID3),
                uid=str(TEST_UID2),
            ),
            self._statbox_faker.entry(
                'phonenumber_alias_subscription_removed',
                _exclude={'consumer', 'ip'},
                uid=str(TEST_UID2),
            ),
            self._statbox_faker.entry(
                'phone_unbound',
                phone_id=str(TEST_PHONE_ID3),
                number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                uid=str(TEST_UID2),
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        phone2_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op2_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        phone3_fmt = partial(self._phone_fmt, TEST_PHONE_ID3)
        op3_fmt = partial(self._op_fmt, TEST_PHONE_ID3, TEST_OPERATION_ID3)
        self._event_logger_faker.assert_events_are_logged(
            self._events(
                uid=TEST_UID1,
                events={
                    'action': 'harvest_expired_phone_operations',

                    phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
                    phone1_fmt('action'): 'deleted',
                    op1_fmt('type'): 'replace',
                    op1_fmt('security_identity'): str(SECURITY_IDENTITY),
                    op1_fmt('action'): 'deleted',

                    phone2_fmt('number'): TEST_PHONE_NUMBER2.e164,
                    phone2_fmt('action'): 'changed',
                    phone2_fmt('confirmed'): TimeNow(),
                    phone2_fmt('bound'): TimeNow(),
                    phone2_fmt('secured'): TimeNow(),
                    op2_fmt('type'): 'bind',
                    op2_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
                    op2_fmt('action'): 'deleted',

                    'phones.secure': str(TEST_PHONE_ID2),
                },
            ) +
            self._events(
                uid=TEST_UID2,
                events={
                    'action': 'acquire_phone',
                    phone3_fmt('number'): TEST_PHONE_NUMBER2.e164,
                    op3_fmt('type'): 'mark',
                    op3_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
                    op3_fmt('action'): 'created',
                    op3_fmt('started'): TimeNow(),
                    op3_fmt('finished'): TimeNow(offset=TEST_SHORT_OPERATION_TTL.total_seconds()),
                    'consumer': '-',
                },
            ) +
            self._events(
                uid=TEST_UID2,
                events={
                    'action': 'unbind_phone_from_account',
                    phone3_fmt('number'): TEST_PHONE_NUMBER2.e164,
                    phone3_fmt('action'): 'changed',
                    phone3_fmt('bound'): '0',
                    phone3_fmt('secured'): '0',

                    'phones.secure': '0',
                    'reason_uid': str(TEST_UID1),
                    'alias.phonenumber.rm': TEST_PHONE_NUMBER2.international,

                    op3_fmt('type'): 'mark',
                    op3_fmt('security_identity'): TEST_PHONE_NUMBER2.digital,
                    op3_fmt('action'): 'deleted',
                    'consumer': '-',
                },
            ) +
            self._events(
                uid=TEST_UID1,
                events={
                    'unbind_phone_from_account.%d' % TEST_UID2: TEST_PHONE_NUMBER2.e164,
                    'consumer': '-',
                },
            ),
        )

        assert_user_notified_about_secure_phone_replaced(
            mailer_faker=self._mailer_faker,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )
        assert_user_notified_about_dealiasify(
            mailer_faker=self._mailer_faker,
            language='ru',
            email_address=TEST_EMAIL2,
            firstname=TEST_FIRSTNAME2,
            login=TEST_LOGIN2,
            portal_email=TEST_EMAIL2,
            phonenumber_alias=TEST_PHONE_NUMBER2.digital,
        )

    def test_many_accounts(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True

        account1_args = dict(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            aliases={'portal': TEST_LOGIN1},
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    password_verified=datetime.now(),
                    code_value=None,
                    code_send_count=0,
                    code_last_sent=None,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                    flags=phone_operation_flags,
                ),
            )
        )
        self._db_faker.serialize(blackbox_userinfo_response_multiple([account1_args]))

        account2_args = dict(
            uid=TEST_UID2,
            login=TEST_LOGIN1,
            aliases={'portal': TEST_LOGIN2},
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID2,
                    phone_id=TEST_PHONE_ID2,
                    password_verified=datetime.now(),
                    code_value=None,
                    code_send_count=0,
                    code_last_sent=None,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                    flags=phone_operation_flags,
                ),
            )
        )
        self._db_faker.serialize(blackbox_userinfo_response_multiple([account2_args]))

        self._blackbox_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([account1_args, account2_args]),
        )

        harvest_uids([TEST_UID1, TEST_UID2], TEST_ENVIRONMENT1)

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER1.e164,
        )
        assert_no_secure_phone(db_faker=self._db_faker, uid=TEST_UID1)

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID2,
            phone_id=TEST_PHONE_ID2,
            phone_number=TEST_PHONE_NUMBER2.e164,
        )
        assert_no_secure_phone(db_faker=self._db_faker, uid=TEST_UID2)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='deleted',
                old=TEST_PHONE_NUMBER1.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID1),
            ),
            self._statbox_faker.entry('secure_phone_removed'),
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='deleted',
                old=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID2),
                uid=str(TEST_UID2),
            ),
            self._statbox_faker.entry(
                'secure_phone_removed',
                uid=str(TEST_UID2),
                number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                phone_id=str(TEST_PHONE_ID2),
                operation_id=str(TEST_OPERATION_ID2),
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID1)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID1, TEST_OPERATION_ID1)
        phone2_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op2_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        self._event_logger_faker.assert_events_are_logged(
            self._events(
                uid=TEST_UID1,
                events={
                    'action': 'harvest_expired_phone_operations',

                    phone1_fmt('number'): TEST_PHONE_NUMBER1.e164,
                    phone1_fmt('action'): 'deleted',
                    'phones.secure': u'0',

                    op1_fmt('type'): 'remove',
                    op1_fmt('security_identity'): str(SECURITY_IDENTITY),
                    op1_fmt('action'): 'deleted',
                },
            ) +
            self._events(
                uid=TEST_UID2,
                events={
                    'action': 'harvest_expired_phone_operations',

                    phone2_fmt('number'): TEST_PHONE_NUMBER2.e164,
                    phone2_fmt('action'): 'deleted',
                    'phones.secure': u'0',

                    op2_fmt('type'): 'remove',
                    op2_fmt('security_identity'): str(SECURITY_IDENTITY),
                    op2_fmt('action'): 'deleted',
                },
            ),
        )

        eq_(self._mailer_faker.messages, [])

    def _test_fail_does_not_interrupt_harvesting(self, exception):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True

        account1_args = dict(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            aliases={'portal': TEST_LOGIN1},
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    password_verified=datetime.now(),
                    code_value=None,
                    code_send_count=0,
                    code_last_sent=None,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                    flags=phone_operation_flags,
                ),
            )
        )
        self._db_faker.serialize(blackbox_userinfo_response_multiple([account1_args]))

        account2_args = dict(
            uid=TEST_UID2,
            login=TEST_LOGIN1,
            aliases={'portal': TEST_LOGIN2},
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID2,
                    phone_id=TEST_PHONE_ID2,
                    password_verified=datetime.now(),
                    code_value=None,
                    code_send_count=0,
                    code_last_sent=None,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                    flags=phone_operation_flags,
                ),
            )
        )
        self._db_faker.serialize(blackbox_userinfo_response_multiple([account2_args]))

        self._blackbox_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([account1_args, account2_args]),
        )
        self._db_faker.set_side_effect_for_db('passportdbshard1', [exception] + [mock.DEFAULT] * 10)

        harvest_uids([TEST_UID1, TEST_UID2], TEST_ENVIRONMENT1)

        assert_secure_phone_being_removed.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID1},
            operation_attributes={'id': TEST_OPERATION_ID1},
        )

        assert_no_phone_in_db(
            db_faker=self._db_faker,
            uid=TEST_UID2,
            phone_id=TEST_PHONE_ID2,
            phone_number=TEST_PHONE_NUMBER2.e164,
        )
        assert_no_secure_phone(db_faker=self._db_faker, uid=TEST_UID2)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'secure_phone_modified',
                operation='deleted',
                old=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID2),
                uid=str(TEST_UID2),
            ),
            self._statbox_faker.entry(
                'secure_phone_removed',
                uid=str(TEST_UID2),
                number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                phone_id=str(TEST_PHONE_ID2),
                operation_id=str(TEST_OPERATION_ID2),
            ),
        ])

        phone1_fmt = partial(self._phone_fmt, TEST_PHONE_ID2)
        op1_fmt = partial(self._op_fmt, TEST_PHONE_ID2, TEST_OPERATION_ID2)
        self._event_logger_faker.assert_events_are_logged(
            self._events(
                uid=TEST_UID2,
                events={
                    'action': 'harvest_expired_phone_operations',

                    phone1_fmt('number'): TEST_PHONE_NUMBER2.e164,
                    phone1_fmt('action'): 'deleted',
                    'phones.secure': u'0',

                    op1_fmt('type'): 'remove',
                    op1_fmt('security_identity'): str(SECURITY_IDENTITY),
                    op1_fmt('action'): 'deleted',
                },
            ),
        )

        eq_(self._mailer_faker.messages, [])

    def test_db_error_does_not_interrupt_harvesting(self):
        self._test_fail_does_not_interrupt_harvesting(DBError())

    def test_eav_deleted_object_not_found_does_not_interrupt_harvesting(self):
        self._test_fail_does_not_interrupt_harvesting(EavDeletedObjectNotFound())

    @raises(BlackboxTemporaryError)
    def test_getting_many_accounts__blackbox_failed(self):
        self._blackbox_faker.set_response_side_effect(
            'userinfo',
            BlackboxTemporaryError(),
        )

        harvest_uids([TEST_UID1], TEST_ENVIRONMENT1)

    def test_blackbox_request(self):
        self._blackbox_faker.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {'uid': None},
                {'uid': None},
            ]),
        )

        harvest_uids([TEST_UID1, TEST_UID2], TEST_ENVIRONMENT1)

        request = self._blackbox_faker.requests[0]
        request.assert_post_data_contains({
            'uid': ','.join(map(str, [TEST_UID1, TEST_UID2])),
            'getphones': 'all',
            'getphoneoperations': '1',
            'aliases': 'all_with_hidden',
            'emails': 'getall',
        })
        request.assert_contains_attributes({
            'account.2fa_on',
            'phones.secure',
            'phones.default',
        })

    def test_orphaned_simple_phone_operation(self):
        build_account(
            db_faker=self._db_faker,
            blackbox_faker=self._blackbox_faker,
            **deep_merge(
                dict(uid=TEST_UID1),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                ),
            )
        )
        safe_execute_queries(
            [
                EavInsertPhoneOperationCreatedQuery(
                    uid=TEST_UID1,
                    operation_data=dict(
                        id=TEST_OPERATION_ID1,
                        phone_id=TEST_PHONE_ID1,
                        security_identity=1,
                        type=2,
                    ),
                ),
            ],
        )

        self.assertTrue(
            self._db_faker.get(
                'phone_operations',
                db='passportdbshard1',
                uid=TEST_UID1,
                id=TEST_OPERATION_ID1,
            ),
        )

        harvest_uids([TEST_UID1], TEST_ENVIRONMENT1)

        self._db_faker.check_missing(
            'phone_operations',
            db='passportdbshard1',
            uid=TEST_UID1,
            id=TEST_OPERATION_ID1,
        )

    def test_orphaned_phone_complex_operation(self):
        build_account(
            db_faker=self._db_faker,
            blackbox_faker=self._blackbox_faker,
            **deep_merge(
                dict(uid=TEST_UID1),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID2,
                    secure_phone_id=TEST_PHONE_ID2,
                    being_bound_operation_id=TEST_OPERATION_ID1,
                    being_bound_phone_id=TEST_PHONE_ID1,
                    being_bound_phone_number=TEST_PHONE_NUMBER1.e164,
                ),
            )
        )
        safe_execute_queries(
            [
                EavInsertPhoneOperationCreatedQuery(
                    uid=TEST_UID1,
                    operation_data=dict(
                        id=TEST_OPERATION_ID1,
                        phone_id=TEST_PHONE_ID1,
                        security_identity=TEST_PHONE_NUMBER1.e164,
                        type=1,
                    ),
                ),
                EavInsertPhoneOperationCreatedQuery(
                    uid=TEST_UID1,
                    operation_data=dict(
                        id=TEST_OPERATION_ID2,
                        phone_id=TEST_PHONE_ID2,
                        security_identity=1,
                        type=4,
                    ),
                ),
            ],
        )

        self.assertTrue(
            self._db_faker.get(
                'phone_operations',
                db='passportdbshard1',
                uid=TEST_UID1,
                id=TEST_OPERATION_ID1,
            ),
        )
        self.assertTrue(
            self._db_faker.get(
                'phone_operations',
                db='passportdbshard1',
                uid=TEST_UID1,
                id=TEST_OPERATION_ID2,
            ),
        )

        harvest_uids([TEST_UID1], TEST_ENVIRONMENT1)

        self._db_faker.check_missing(
            'phone_operations',
            db='passportdbshard1',
            uid=TEST_UID1,
            id=TEST_OPERATION_ID1,
        )
        self._db_faker.check_missing(
            'phone_operations',
            db='passportdbshard1',
            uid=TEST_UID1,
            id=TEST_OPERATION_ID2,
        )
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            uid=TEST_UID1,
            phone_attributes={'id': TEST_PHONE_ID2},
        )


@with_settings_hosts()
class TestHarvestAccount(TestCase):
    def test_notify_about_replacement(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        account = self._build_account(
            **deep_merge(
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                    is_alias=True,
                ),
                build_phone_unbound(
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_PHONE_NUMBER2.e164,
                ),
                build_phone_being_bound_replaces_secure_operations(
                    secure_operation_id=TEST_OPERATION_ID1,
                    secure_phone_id=TEST_PHONE_ID1,
                    being_bound_operation_id=TEST_OPERATION_ID2,
                    being_bound_phone_id=TEST_PHONE_ID2,
                    being_bound_phone_number=TEST_PHONE_NUMBER2.e164,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                    secure_code_value=None,
                    secure_code_send_count=0,
                    secure_code_last_sent=None,
                    being_bound_code_confirmed=datetime.now(),
                    password_verified=datetime.now(),
                    flags=phone_operation_flags,
                ),
            )
        )

        harvest_account(account, TEST_ENVIRONMENT1)

        assert_user_notified_about_secure_phone_replaced(
            mailer_faker=self._mailer_faker,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def test_notify_about_removal(self):
        phone_operation_flags = PhoneOperationFlags()
        phone_operation_flags.in_quarantine = True
        account = self._build_account(
            **deep_merge(
                dict(
                    crypt_password=TEST_PASSWORD_HASH1,
                ),
                build_phone_secured(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_PHONE_NUMBER1.e164,
                ),
                build_remove_operation(
                    operation_id=TEST_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                    password_verified=datetime.now(),
                    code_value=None,
                    code_send_count=0,
                    code_last_sent=None,
                    started=datetime.now() - timedelta(hours=2),
                    finished=datetime.now() - timedelta(hours=1),
                    flags=phone_operation_flags,
                ),
            )
        )

        harvest_account(account, TEST_ENVIRONMENT1)

        assert_user_notified_about_secure_phone_removed_with_quarantine(
            mailer_faker=self._mailer_faker,
            language='ru',
            email_address=TEST_EMAIL1,
            firstname=TEST_FIRSTNAME1,
            login=TEST_LOGIN1,
        )

    def _build_account(self, **kwargs):
        return _build_account(db_faker=self._db_faker, **kwargs)
