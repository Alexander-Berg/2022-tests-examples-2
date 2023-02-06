# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import assert_raises
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.env import Environment
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.runner.context_managers import UPDATE
from passport.backend.core.test.events import EventLoggerFaker
from passport.backend.core.test.test_utils import with_settings_hosts


UID = 100
ACTION = 'testaction'


@with_settings_hosts()
class TestEventLoggerFaker(TestCase):
    def setUp(self):
        self._faker = EventLoggerFaker()
        self._faker.start()
        self._db_faker = FakeDB()
        self._db_faker.start()

    def tearDown(self):
        self._db_faker.stop()
        self._faker.stop()
        del self._db_faker
        del self._faker

    def test_with_order__ok(self):
        self._do_actions()

        self._faker.assert_events_are_logged_with_order([
            {u'name': u'info.default_email', u'value': u'john@doe'},
            {u'name': u'action', u'value': ACTION},
            {u'name': u'info.default_email', u'value': u'mike@tyson'},
            {u'name': u'action', u'value': ACTION},
        ])

    def test_with_order__fail(self):
        with assert_raises(AssertionError):
            self._do_actions()

            self._faker.assert_events_are_logged_with_order([
                {u'name': u'action', u'value': ACTION},
                {u'name': u'info.default_email', u'value': u'john@doe'},
                {u'name': u'action', u'value': ACTION},
                {u'name': u'info.default_email', u'value': u'mike@tyson'},
            ])

    def test_without_order__list__ok(self):
        self._do_actions()

        self._faker.assert_events_are_logged([
            {u'name': u'action', u'value': ACTION},
            {u'name': u'info.default_email', u'value': u'john@doe'},
            {u'name': u'action', u'value': ACTION},
            {u'name': u'info.default_email', u'value': u'mike@tyson'},
        ])

    def test_without_order__list__fail(self):
        with assert_raises(AssertionError):
            self._do_actions()

            self._faker.assert_events_are_logged([
                {u'name': u'info.default_email', u'value': u'john@doe'},
                {u'name': u'action', u'value': ACTION},
                {u'name': u'info.default_email', u'value': u'mike@tyson'},
            ])

    def test_without_order__dict__ok(self):
        account = default_account(uid=UID)

        with UPDATE(account, Environment(), {u'action': ACTION}):
            account.default_email = u'john@doe'

        self._faker.assert_events_are_logged({
            u'action': ACTION,
            u'info.default_email': u'john@doe',
        })

    def test_without_order__dict__fail(self):
        with assert_raises(AssertionError):
            account = default_account(uid=UID)

            with UPDATE(account, Environment(), {u'action': ACTION}):
                account.default_email = u'john@doe'

            self._faker.assert_events_are_logged({
                u'action': ACTION,
                u'info.default_email': u'ivan@doe',
            })

    def test_event_is_logged__ok(self):
        self._do_actions()
        self._faker.assert_event_is_logged(u'info.default_email', u'john@doe')

    def test_event_is_logged__fail(self):
        with assert_raises(AssertionError):
            self._do_actions()
            self._faker.assert_event_is_logged(u'info.default_email', u'ivan@doe')

    def test_assert_contains__ok(self):
        self._do_actions()
        self._faker.assert_contains([
            {u'uid': str(UID), u'name': u'info.default_email', u'value': u'mike@tyson'},
            {u'uid': str(UID), u'name': u'info.default_email', u'value': u'john@doe'},
        ])

    def test_assert_contains__fail(self):
        with assert_raises(AssertionError):
            self._do_actions()
            self._faker.assert_contains([
                {u'uid': str(UID), u'name': u'info.default_email', u'value': u'mike@tyson'},
                {u'uid': str(UID), u'name': u'info.default_email', u'value': u'john@doe'},
                {u'uid': str(UID), u'name': u'info.default_email', u'value': u'ivan@doe'},
            ])

    def _do_actions(self):
        account = default_account(uid=UID)

        with UPDATE(account, Environment(), {u'action': ACTION}):
            account.default_email = u'john@doe'

        with UPDATE(account, Environment(), {u'action': ACTION}):
            account.default_email = u'mike@tyson'
