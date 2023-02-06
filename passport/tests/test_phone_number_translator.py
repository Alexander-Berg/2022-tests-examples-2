# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    unicode_literals,
)

import abc

from passport.backend.core.builders.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.env import Environment
from passport.backend.core.logging_utils.loggers import StatboxLogger
from passport.backend.core.models.phones.faker import (
    assert_account_has_phonenumber_alias,
    assert_phonenumber_alias_missing,
    assert_secure_phone_being_removed,
    assert_secure_phone_bound,
    assert_simple_phone_bound,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
)
from passport.backend.core.test.consts import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_LOGIN1,
    TEST_NEOPHONISH_LOGIN1,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_PHONE_OPERATION_ID1,
    TEST_PHONISH_LOGIN1,
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.dbscripts.phone_number_translator.base import translate_phone_number
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.utils.common import deep_merge


@with_settings_hosts()
class TestTranslatePhoneNumber(TestCase):
    def setUp(self):
        super(TestTranslatePhoneNumber, self).setUp()
        self.setup_statbox_templates()

    def setup_statbox_templates(self):
        self._statbox_faker.bind_entry(
            'phonenumber_alias_taken_away_from_old_owner',
            _exclude=['consumer', 'ip', 'user_agent'],
            _inherit_from=['phonenumber_alias_taken_away'],
            number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.masked_format_for_statbox,
            uid=str(TEST_UID2),
        )
        self._statbox_faker.bind_entry(
            'phonenumber_alias_removed_from_old_owner',
            _exclude=['ip'],
            _inherit_from=['phonenumber_alias_removed'],
            consumer='-',
            uid=str(TEST_UID2),
        )
        self._statbox_faker.bind_entry(
            'phonenumber_alias_subscription_removed_from_old_owner',
            _exclude=['ip'],
            _inherit_from=['phonenumber_alias_subscription_removed'],
            consumer='-',
            uid=str(TEST_UID2),
            user_agent='-',
        )
        self._statbox_faker.bind_entry(
            'old_phonenumber_alias_taken_away',
            _exclude=['consumer', 'ip', 'user_agent'],
            _inherit_from=['phonenumber_alias_taken_away'],
            number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.masked_format_for_statbox,
            reason='off',
            uid=str(TEST_UID1),
        )
        self._statbox_faker.bind_entry(
            'new_phonenumber_alias_given_out',
            _exclude=['consumer', 'ip', 'user_agent'],
            _inherit_from=['phonenumber_alias_given_out'],
            is_owner_changed='1',
            login=TEST_NEOPHONISH_LOGIN1,
            number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.masked_format_for_statbox,
            uid=str(TEST_UID1),
        )
        self._statbox_faker.bind_entry(
            'phonenumber_alias_updated',
            _exclude=['ip'],
            _inherit_from=['phonenumber_alias_updated'],
            consumer='-',
            uid=str(TEST_UID1),
        )

    def translate_phone_number(self, phone_number, dry_run=False):
        translate_phone_number(
            blackbox=Blackbox(),
            dry_run=dry_run,
            env=Environment(),
            phone_number=phone_number,
            statbox=StatboxLogger(),
            uid=TEST_UID1,
        )

    def test_neophonish(self):
        NeophonishBlackboxResponse(self._blackbox_faker, self._db_faker).setup()
        PortalBlackboxResponse(self._blackbox_faker, self._db_faker).setup()

        self.translate_phone_number(TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

        assert_account_has_phonenumber_alias(
            alias=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.digital,
            db_faker=self._db_faker,
            enable_search=False,
            uid=TEST_UID1,
        )
        assert_secure_phone_being_removed.check_db(
            db_faker=self._db_faker,
            phone_attributes=dict(
                id=TEST_PHONE_ID1,
                number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164,
            ),
            uid=TEST_UID1,
        )

        assert_phonenumber_alias_missing(db_faker=self._db_faker, uid=TEST_UID2)
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            phone_attributes=dict(
                id=TEST_PHONE_ID2,
                number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164,
            ),
            uid=TEST_UID2,
        )

        e = self._statbox_faker.entry
        self._statbox_faker.assert_equals(
            [
                e('phonenumber_alias_taken_away_from_old_owner'),
                e('phonenumber_alias_removed_from_old_owner'),
                e('phonenumber_alias_subscription_removed_from_old_owner'),
                e('old_phonenumber_alias_taken_away'),
                e('new_phonenumber_alias_given_out'),
                e('phonenumber_alias_updated'),
            ],
        )

        e = EventCompositor()
        with e.uid(str(TEST_UID2)):
            e('alias.phonenumber.rm', TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.international)
            e('action', 'phone_alias_delete')
            e('initiator_uid', str(TEST_UID1))
        with e.uid(str(TEST_UID1)):
            e('alias.phonenumber.change', TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.international)
            with e.prefix('phone.%s.' % TEST_PHONE_ID1):
                e('action', 'changed')
                e('number', TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164)
            e('action', 'apply_phone_translation_rule')
        self._event_logger_faker.assert_events_are_logged(e.to_lines(), in_order=True)

    def test_phonish(self):
        PhonishBlackboxResponse(self._blackbox_faker, self._db_faker).setup()

        self.translate_phone_number(TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

        assert_phonenumber_alias_missing(db_faker=self._db_faker, uid=TEST_UID1)
        assert_simple_phone_bound.check_db(
            db_faker=self._db_faker,
            phone_attributes=dict(
                id=TEST_PHONE_ID1,
                number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164,
            ),
            uid=TEST_UID1,
        )

        self._statbox_faker.assert_equals(list())

        e = EventCompositor(uid=str(TEST_UID1))
        with e.prefix('phone.%s.' % TEST_PHONE_ID1):
            e('action', 'changed')
            e('number', TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164)
        e('action', 'apply_phone_translation_rule')
        self._event_logger_faker.assert_events_are_logged(e.to_lines(), in_order=True)

    def test_dry_run(self):
        NeophonishBlackboxResponse(self._blackbox_faker, self._db_faker).setup()
        PortalBlackboxResponse(self._blackbox_faker, self._db_faker).setup()

        self.translate_phone_number(
            dry_run=True,
            phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

        assert_account_has_phonenumber_alias(
            alias=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.digital,
            db_faker=self._db_faker,
            enable_search=False,
            uid=TEST_UID1,
        )
        assert_account_has_phonenumber_alias(
            alias=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.digital,
            db_faker=self._db_faker,
            enable_search=False,
            uid=TEST_UID2,
        )

        self._statbox_faker.assert_equals(list())
        self._event_logger_faker.assert_events_are_logged(list())

    def test_account_not_found(self):
        self._blackbox_faker.set_response_side_effect('userinfo', [blackbox_userinfo_response(uid=None)])

        self.translate_phone_number(phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_no_rule_for_specified_phone(self):
        NeophonishBlackboxResponse(self._blackbox_faker, self._db_faker).setup()

        self.translate_phone_number(phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_no_specified_phone_on_account(self):
        PhonishBlackboxResponse(
            blackbox_faker=self._blackbox_faker,
            db_faker=self._db_faker,
            phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        ).setup()

        self.translate_phone_number(phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

    def test_new_phonenumber_alias_is_email_on_old_owner(self):
        NeophonishBlackboxResponse(self._blackbox_faker, self._db_faker).setup()
        PortalBlackboxResponse(
            blackbox_faker=self._blackbox_faker,
            db_faker=self._db_faker,
            is_enabled_search_for_alias=True,
        ).setup()

        self.translate_phone_number(phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

        assert_account_has_phonenumber_alias(
            alias=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.digital,
            db_faker=self._db_faker,
            enable_search=False,
            uid=TEST_UID1,
        )
        assert_account_has_phonenumber_alias(
            alias=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.digital,
            db_faker=self._db_faker,
            enable_search=True,
            uid=TEST_UID2,
        )

        self._statbox_faker.assert_equals(list())
        self._event_logger_faker.assert_events_are_logged(list())


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, blackbox_faker, db_faker):
        self._blackbox_faker = blackbox_faker
        self._db_faker = db_faker
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        userinfo_response = blackbox_userinfo_response(**self.kwargs)
        self._db_faker.serialize(userinfo_response)
        self._blackbox_faker.extend_response_side_effect('userinfo', [userinfo_response])


class NeophonishBlackboxResponse(IBlackboxResponse):
    def __init__(self, blackbox_faker, db_faker):
        self._userinfo_response = UserinfoBlackboxResponse(blackbox_faker, db_faker)
        self._userinfo_response.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(neophonish=TEST_NEOPHONISH_LOGIN1),
                    login=TEST_NEOPHONISH_LOGIN1,
                    uid=TEST_UID1,
                ),
                build_phone_secured(
                    is_alias=True,
                    is_enabled_search_for_alias=False,
                    phone_id=TEST_PHONE_ID1,
                    phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164,
                ),
                build_remove_operation(
                    operation_id=TEST_PHONE_OPERATION_ID1,
                    phone_id=TEST_PHONE_ID1,
                ),
            ),
        )

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()


class PhonishBlackboxResponse(IBlackboxResponse):
    def __init__(self, blackbox_faker, db_faker, phone_number=None):
        if phone_number is None:
            phone_number = TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1

        self._userinfo_response = UserinfoBlackboxResponse(blackbox_faker, db_faker)
        self._userinfo_response.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(phonish=TEST_PHONISH_LOGIN1),
                    login=TEST_PHONISH_LOGIN1,
                    uid=TEST_UID1,
                ),
                build_phone_bound(
                    phone_id=TEST_PHONE_ID1,
                    phone_number=phone_number.e164),
            ),
        )

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()


class PortalBlackboxResponse(IBlackboxResponse):
    def __init__(self, blackbox_faker, db_faker, is_enabled_search_for_alias=False):
        self._userinfo_response = UserinfoBlackboxResponse(blackbox_faker, db_faker)
        self._userinfo_response.kwargs.update(
            deep_merge(
                dict(
                    aliases=dict(portal=TEST_LOGIN1),
                    login=TEST_LOGIN1,
                    uid=TEST_UID2,
                ),
                build_phone_secured(
                    is_alias=True,
                    is_enabled_search_for_alias=is_enabled_search_for_alias,
                    phone_id=TEST_PHONE_ID2,
                    phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1.e164,
                ),
            ),
        )

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()
