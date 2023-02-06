# -*- coding: utf-8 -*-

import abc
from datetime import datetime

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.env import Environment
from passport.backend.core.logging_utils.loggers import StatboxLogger
from passport.backend.core.models.alias import PhonenumberAlias
from passport.backend.core.models.email import Emails
from passport.backend.core.models.phones.faker import (
    assert_phonenumber_alias_missing,
    assert_secure_phone_bound,
    build_phone_secured,
)
from passport.backend.core.models.phones.phones import (
    Phones,
    ReplaceSecurePhoneWithBoundPhoneOperation,
    ReplaceSecurePhoneWithNonboundPhoneOperation,
    SimpleBindOperation,
)
from passport.backend.core.runner.context_managers import UPDATE
from passport.backend.core.test.consts import (
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_CONSUMER1,
    TEST_LOGIN1,
    TEST_NEOPHONISH_LOGIN1,
    TEST_PHONE_ID1,
    TEST_PHONE_ID2,
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import (
    Brazil2016PhoneTranslationRule,
    PhoneNumber,
)
from passport.backend.core.yasms.phone_numbering import PhoneNumberTranslator
from passport.backend.utils.common import deep_merge

from .base import TestCase
from .consts import (
    TEST_ALL_SUPPORTED_LANGUAGES,
    TEST_DISPLAY_LANGUAGES,
    TranslationSettings,
)


@with_settings_hosts(
    ALL_SUPPORTED_LANGUAGES=TEST_ALL_SUPPORTED_LANGUAGES,
    BLACKBOX_ATTRIBUTES=tuple(),
    BLACKBOX_URL='http://blackbox.url/',
    DISPLAY_LANGUAGES=TEST_DISPLAY_LANGUAGES,
    translations=TranslationSettings(),
)
class TestPhoneNumberTranslator(TestCase):
    def setUp(self):
        super(TestPhoneNumberTranslator, self).setUp()
        self._account = mock.Mock()
        self._account.uid = TEST_UID3
        self._account.phonenumber_alias = PhonenumberAlias()
        self._phones = Phones(parent=self._account)
        self._account.phones = self._phones
        self._account.emails = Emails()
        self._translator = self.build_translator()

    def tearDown(self):
        del self._phones
        del self._account
        super(TestPhoneNumberTranslator, self).tearDown()

    def build_translator(
        self,
        old_phone_number=None,
        rule=None,
    ):
        if old_phone_number is None:
            old_phone_number = PhoneNumber.parse('+555180000000', country='BR', allow_impossible=True)
        if rule is None:
            rule = Brazil2016PhoneTranslationRule()
        return PhoneNumberTranslator.build_from_account(
            account=self._account,
            blackbox=Blackbox(),
            consumer=TEST_CONSUMER1,
            old_phone_number=old_phone_number,
            rule=rule,
            statbox=StatboxLogger(),
        )

    def test_old(self):
        self._phones.create('+555180000000', existing_phone_id=1)

        self._translator.check_all()
        self._translator.translate()

        eq_(self._phones.all()[1].number.e164, '+5551980000000')

    def test_new(self):
        self._phones.create('+5551980000000', existing_phone_id=1)

        with self.assertRaises(PhoneNumberTranslator.PhoneNotFoundError):
            self._translator.check_all()

    def test_no_specified_phone(self):
        self._phones.create('+79259160000', existing_phone_id=1)

        with self.assertRaises(PhoneNumberTranslator.PhoneNotFoundError):
            self._translator.check_all()

    def test_different_phones(self):
        self._phones.create('+555180000000', existing_phone_id=1)
        self._phones.create('+5551980000001', existing_phone_id=2)
        self._phones.create('+555180000002', existing_phone_id=3)
        self._phones.create('+79259160003', existing_phone_id=4)

        self._translator.check_all()
        self._translator.translate()

        eq_(self._phones.all()[1].number.e164, '+5551980000000')
        eq_(self._phones.all()[2].number.e164, '+5551980000001')
        eq_(self._phones.all()[3].number.e164, '+555180000002')
        eq_(self._phones.all()[4].number.e164, '+79259160003')

    def test_old__secure(self):
        phone = self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone.set_as_secure()

        self._translator.check_all()
        self._translator.translate()

        eq_(phone.number.e164, '+5551980000000')

    def test_new__secure(self):
        phone = self._phones.create('+5551980000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone.set_as_secure()

        with self.assertRaises(PhoneNumberTranslator.PhoneNotFoundError):
            self._translator.check_all()

    def test_conflict__new_secure_old_simple(self):
        self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone2 = self._phones.create('+5551980000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=2)
        phone2.set_as_secure()

        self._translator.check_all()
        self._translator.translate()

        ok_(1 not in self._phones.all())
        phone2 = self._phones.by_id(2)
        eq_(phone2.number.e164, '+5551980000000')
        ok_(phone2 is self._phones.secure)

    def test_conflict__new_simple_old_secure(self):
        phone1 = self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone1.set_as_secure()
        self._phones.create('+5551980000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=2)
        ReplaceSecurePhoneWithBoundPhoneOperation.create(self._phones, 1, 2, '1', '2', self._statbox, 1)

        self._translator.check_all()
        self._translator.translate()

        phone1 = self._phones.by_id(1)
        eq_(phone1.number.e164, '+5551980000000')
        ok_(phone1 is self._phones.secure)
        ok_(2 not in self._phones.all())

    def test_conflict__new_replaces_secure_old_simple(self):
        self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        self._phones.create('+5551980000000', existing_phone_id=2)
        phone3 = self._phones.create('+79259164525', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=3)
        phone3.set_as_secure()
        ReplaceSecurePhoneWithNonboundPhoneOperation.create(self._phones, 3, 2, '1', '2', self._statbox)

        self._translator.check_all()
        self._translator.translate()

        ok_(1 not in self._phones.all())
        phone2 = self._phones.by_id(2)
        eq_(phone2.number.e164, '+5551980000000')
        ok_(3 in self._phones.all())

    def test_conflict__new_simple_old_replaces_secure(self):
        self._phones.create('+555180000000', existing_phone_id=1)
        self._phones.create('+5551980000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=2)
        phone3 = self._phones.create('+79259164525', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=3)
        phone3.set_as_secure()
        ReplaceSecurePhoneWithNonboundPhoneOperation.create(self._phones, 3, 1, '1', '2', self._statbox)

        self._translator.check_all()
        self._translator.translate()

        phone1 = self._phones.by_id(1)
        eq_(phone1.number.e164, '+5551980000000')
        ok_(2 not in self._phones.all())
        ok_(3 in self._phones.all())

    def test_conflict__new_simple_old_simple(self):
        self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        self._phones.create('+5551980000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=2)

        self._translator.check_all()
        self._translator.translate()

        ok_(1 not in self._phones.all())
        phone2 = self._phones.by_id(2)
        eq_(phone2.number.e164, '+5551980000000')

    def test_conflict__new_not_bound_old_simple(self):
        self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        self._phones.create('+5551980000000', existing_phone_id=2)

        self._translator.check_all()
        self._translator.translate()

        phone1 = self._phones.by_id(1)
        eq_(phone1.number.e164, '+5551980000000')
        ok_(2 not in self._phones.all())

    def test_conflict__both_being_simple_bound(self):
        self._phones.create('+555180000000', existing_phone_id=1)
        SimpleBindOperation.create(self._phones, 1, '1', False, self._statbox)
        self._phones.create('+5551980000000', existing_phone_id=2)
        SimpleBindOperation.create(self._phones, 2, '1', False, self._statbox)

        self._translator.check_all()
        self._translator.translate()

        ok_(1 not in self._phones.all())
        phone2 = self._phones.by_id(2)
        eq_(phone2.number.e164, '+5551980000000')

    def test_conflict__new_not_bound_old_being_simple_bound(self):
        self._phones.create('+555180000000', existing_phone_id=1)
        SimpleBindOperation.create(self._phones, 1, '1', False, self._statbox)
        self._phones.create('+5551980000000', existing_phone_id=2)

        self._translator.check_all()
        self._translator.translate()

        phone1 = self._phones.by_id(1)
        eq_(phone1.number.e164, '+5551980000000')
        ok_(2 not in self._phones.all())

    def test_conflict__both_not_bound(self):
        self._phones.create('+555180000000', existing_phone_id=1)
        self._phones.create('+5551980000000', existing_phone_id=2)

        self._translator.check_all()
        self._translator.translate()

        ok_(1 not in self._phones.all())
        phone2 = self._phones.by_id(2)
        eq_(phone2.number.e164, '+5551980000000')

    def test_rule_not_applicable_to_phone(self):
        translator = self.build_translator(old_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1)

        with self.assertRaises(PhoneNumberTranslator.InapplicablePhoneTranslationRule):
            translator.check_all()

    def test_old_phone_is_phonenumber_email_alias(self):
        phone = self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone.set_as_secure()
        self._account.phonenumber_alias.number = phone.number
        self._account.phonenumber_alias.enable_search = True

        with self.assertRaises(PhoneNumberTranslator.UnableToTranslatePhoneNumber):
            self._translator.check_all()

    def test_old_phone_is_phonenumber_alias(self):
        phone = self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone.set_as_secure()
        self._account.phonenumber_alias.number = phone.number
        PortalBlackboxResponse(
            blackbox_faker=self._blackbox_builder_faker,
            db_faker=self._db_faker,
        ).setup()

        self._translator.check_all()

        with UPDATE(self._translator.old_phonenumber_alias_owner, Environment(), dict(action='foo')):
            self._translator.take_phonenumber_alias_away_from_old_owner()

        self._translator.translate()

        new_phone_number = '+5551980000000'
        eq_(self._phones.all()[1].number.e164, new_phone_number)
        eq_(self._account.phonenumber_alias.number.e164, new_phone_number)
        ok_(not self._account.phonenumber_alias.enable_search)

        assert_phonenumber_alias_missing(db_faker=self._db_faker, uid=TEST_UID2)
        assert_secure_phone_bound.check_db(
            db_faker=self._db_faker,
            phone_attributes=dict(id=TEST_PHONE_ID2, number=new_phone_number),
            uid=TEST_UID2,
        )

    def test_new_phone_is_phonenumber_alias_is_email_on_old_owner(self):
        phone = self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone.set_as_secure()
        self._account.phonenumber_alias.number = phone.number
        PortalBlackboxResponse(
            blackbox_faker=self._blackbox_builder_faker,
            db_faker=self._db_faker,
            is_enabled_search_for_alias=True,
        ).setup()

        with self.assertRaises(PhoneNumberTranslator.UnableToTranslatePhoneNumber):
            self._translator.check_all()

    def test_old_owner_of_new_phonenumber_alias_is_neophonish(self):
        phone = self._phones.create('+555180000000', confirmed=datetime.now(), bound=datetime.now(), existing_phone_id=1)
        phone.set_as_secure()
        self._account.phonenumber_alias.number = phone.number
        NeophonishBlackboxResponse(
            blackbox_faker=self._blackbox_builder_faker,
            db_faker=self._db_faker,
        ).setup()

        with self.assertRaises(PhoneNumberTranslator.UnableToTranslatePhoneNumber):
            self._translator.check_all()


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
                    phone_number='+5551980000000',
                ),
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
                    phone_number='+5551980000000',
                ),
            ),
        )

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()
