# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from nose.tools import assert_raises
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.dbmanager.manager import safe_execute_queries
from passport.backend.core.differ import diff
from passport.backend.core.mailer.faker.mail_utils import EmailDatabaseMatcher
from passport.backend.core.models.account import Account
from passport.backend.core.models.email import Email
from passport.backend.core.serializers.eav.emails import EmailsEavSerializer
from passport.backend.core.test.consts import (
    TEST_EMAIL1,
    TEST_EMAIL2,
    TEST_EMAIL_ID1,
    TEST_UID1,
    TEST_UNIXTIME1,
    TEST_UNIXTIME2,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow


class TestEmailDatabaseMatcher(TestCase):
    def setUp(self):
        super(TestEmailDatabaseMatcher, self).setUp()
        self.fake_db = FakeDB()
        self.account = Account(uid=TEST_UID1).parse({})
        self.fake_db.start()

    def tearDown(self):
        self.fake_db.stop()
        del self.account
        del self.fake_db
        super(TestEmailDatabaseMatcher, self).tearDown()

    def serialize(self, s1, s2):
        queries = EmailsEavSerializer().serialize(s1, s2, diff(s1, s2))
        safe_execute_queries(queries)

    def to_db(self, instance):
        self.account.emails.add(instance)
        return self.serialize(None, self.account.emails)

    def create_email(self, **kwargs):
        defaults = dict(
            id=TEST_EMAIL_ID1,
            address=TEST_EMAIL1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return Email(**kwargs)

    def examine_same_value(self, attr, value):
        email = self.create_email(**{attr: value})
        self.to_db(email)

        matcher = EmailDatabaseMatcher(self.fake_db, TEST_UID1, email)
        matcher.match_all()

    def examine_different_value(self, attr, value1, value2):
        assert value1 != value2

        email1 = self.create_email(**{attr: value1})
        self.to_db(email1)

        email2 = self.create_email(**{attr: value2})
        matcher = EmailDatabaseMatcher(self.fake_db, TEST_UID1, email2)
        with assert_raises(AssertionError):
            matcher.match_all()

    def examine_timestamp_now(self, attr):
        email1 = self.create_email(**{attr: datetime.now()})
        self.to_db(email1)

        email2 = self.create_email(**{attr: DatetimeNow()})
        matcher = EmailDatabaseMatcher(self.fake_db, TEST_UID1, email2)
        matcher.match_all()

    def test_same_address(self):
        self.examine_same_value('address', TEST_EMAIL1)

    def test_different_address(self):
        self.examine_different_value('address', TEST_EMAIL1, TEST_EMAIL2)

    def test_same_created_at(self):
        self.examine_same_value('created_at', datetime.fromtimestamp(TEST_UNIXTIME1))

    def test_different_created_at(self):
        self.examine_different_value(
            'created_at',
            datetime.fromtimestamp(TEST_UNIXTIME1),
            datetime.fromtimestamp(TEST_UNIXTIME2),
        )

    def test_created_at_now(self):
        self.examine_timestamp_now('created_at')

    def test_same_confirmed_at(self):
        self.examine_same_value('confirmed_at', datetime.fromtimestamp(TEST_UNIXTIME1))

    def test_different_confirmed_at(self):
        self.examine_different_value(
            'confirmed_at',
            datetime.fromtimestamp(TEST_UNIXTIME1),
            datetime.fromtimestamp(TEST_UNIXTIME2),
        )

    def test_confirmed_at_now(self):
        self.examine_timestamp_now('confirmed_at')

    def test_same_bound_at(self):
        self.examine_same_value('bound_at', datetime.fromtimestamp(TEST_UNIXTIME1))

    def test_different_bound_at(self):
        self.examine_different_value(
            'bound_at',
            datetime.fromtimestamp(TEST_UNIXTIME1),
            datetime.fromtimestamp(TEST_UNIXTIME2),
        )

    def test_bound_at_now(self):
        self.examine_timestamp_now('bound_at')

    def test_same_is_rpop(self):
        self.examine_same_value('is_rpop', True)

    def test_different_is_rpop(self):
        self.examine_different_value('is_rpop', True, False)

    def test_same_is_unsafe(self):
        self.examine_same_value('is_unsafe', True)

    def test_different_is_unsafe(self):
        self.examine_different_value('is_unsafe', True, False)

    def test_same_is_silent(self):
        self.examine_same_value('is_silent', True)

    def test_different_is_silent(self):
        self.examine_different_value('is_silent', True, False)
