# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.differ import (
    diff,
    utils,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.password import Password
from passport.backend.core.models.subscription import Subscription
from passport.backend.core.services import Service
from passport.backend.core.undefined import Undefined


class TestDiffer(unittest.TestCase):
    def test_none_diff(self):
        actual_result = diff({'a': None}, {'a': None})
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {})
        ok_(not actual_result)

    def test_added_none(self):
        actual_result = diff({}, {'a': None})
        eq_(actual_result.added, {'a': None})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {})
        ok_(actual_result)

    @raises(TypeError)
    def test_invalid_arguments(self):
        diff(14, {})


class TestSliceDiff(unittest.TestCase):
    def test_empty_diff(self):
        added = {}
        changed = {}
        deleted = {}
        empty_diff = (added, changed, deleted)

        actual_result = utils.slice_diff(empty_diff, 'foo')
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {})

    def test_none_in_deleted(self):
        added = {'foo': 123}
        changed = {'foo': 456}
        deleted = {'foo': None}

        actual_result = utils.slice_diff(
            (added, changed, deleted),
            'foo',
        )
        eq_(actual_result.added, 123)
        eq_(actual_result.changed, 456)
        eq_(actual_result.deleted, None)

    def test_nothing_deleted(self):
        added = {'foo': 123}
        changed = {'foo': 456}
        deleted = {'zar': None}

        actual_result = utils.slice_diff(
            (added, changed, deleted),
            'foo',
        )
        eq_(actual_result.added, 123)
        eq_(actual_result.changed, 456)
        eq_(actual_result.deleted, {})

    def test_nested_diffs(self):
        added = {
            'foo': {
                'bar': 123,
            },
        }
        changed = {}
        deleted = {
            'foo': {
                'bar': {
                    'zar': 456,
                },
            },
        }

        actual_result = utils.slice_diff(
            utils.slice_diff(
                (added, changed, deleted),
                'foo'
            ),
            'bar',
        )
        eq_(actual_result.added, 123)
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {'zar': 456})


class TestDifferAccount(unittest.TestCase):
    def test_simple_1(self):
        acc = Account()
        acc.uid = 123
        s1 = acc.snapshot()

        acc.display_login = 'john_doe'
        acc.uid = 456
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {'display_login': 'john_doe'})
        eq_(actual_result.changed, {'uid': 456})
        eq_(actual_result.deleted, {})

    def test_simple_2(self):
        acc = Account()
        acc.uid = 123
        s1 = acc.snapshot()

        acc.display_login = 'john_doe'
        acc.uid = None
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {'display_login': 'john_doe'})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {'uid': None})

    def test_model(self):
        acc = Account()
        acc.uid = 123

        pwd = Password(acc)
        pwd.is_expired = True
        acc.password = pwd
        s1 = acc.snapshot()

        acc.password.is_expired = False
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {'password': {'is_expired': False}})
        eq_(actual_result.deleted, {})

    def test_model_deleted(self):
        acc = Account()
        acc.uid = 123
        s1 = acc.snapshot()

        actual_result = diff(s1, None)
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {'uid': 123})

    def test_subscriptions_created(self):
        acc = Account()
        acc.uid = 123
        s1 = acc.snapshot()

        sub1 = Subscription()
        sub1.suid = 123
        sub2 = Subscription()
        sub2.suid = 456
        acc.subscriptions = [sub1, sub2]
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(
            actual_result.added,
            {
                'subscriptions': [
                    (Undefined, {'suid': 123}),
                    (Undefined, {'suid': 456}),
                ],
            },
        )
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {})

    def test_subscription_deleted(self):
        acc = Account()
        acc.uid = 123

        sub1 = Subscription()
        sub1.suid = 123
        sub2 = Subscription()
        sub2.suid = 456
        acc.subscriptions = [sub1, sub2]
        s1 = acc.snapshot()

        acc.subscriptions.remove(sub1)
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(
            actual_result.deleted,
            {
                'subscriptions': [
                    ({'suid': 123}, None)
                ],
            },
        )

    def test_subscriptions_changed(self):
        acc = Account()
        acc.uid = 123

        sub1 = Subscription()
        sub1.suid = 123
        sub2 = Subscription()
        sub2.suid = 456
        acc.subscriptions = [sub1, sub2]
        s1 = acc.snapshot()

        for s in acc.subscriptions:
            s.suid *= 2
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(
            actual_result.changed,
            {
                'subscriptions': [
                    (
                        {'suid': 123},
                        {'suid': 123 * 2},
                    ),
                    (
                        {'suid': 456},
                        {'suid': 456 * 2},
                    ),
                ]
            },
        )
        eq_(actual_result.deleted, {})

    def test_subscription_value_deleted(self):
        acc = Account()
        acc.uid = 123

        sub1 = Subscription()
        sub1.suid = 123
        sub2 = Subscription()
        sub2.suid = 456
        acc.subscriptions = [sub1, sub2]

        s1 = acc.snapshot()

        for s in acc.subscriptions:
            s.suid = None
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(
            actual_result.deleted,
            {
                'subscriptions': [
                    ({'suid': 123}, None),
                    ({'suid': 456}, None)
                ]
            },
        )

    def test_subscription_with_service_added(self):
        acc = Account()
        acc.uid = 123
        s1 = acc.snapshot()

        sub1 = Subscription()
        sub1.suid = 123
        svc1 = Service(sid=123, description='foo')
        sub1.service = svc1
        acc.subscriptions = [sub1]
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(
            actual_result.added,
            {
                'subscriptions': [
                    (
                        Undefined,
                        {
                            'suid': 123,
                            'service': svc1,
                        },
                    ),
                ]
            },
        )
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {})

    def test_account_password_added(self):
        acc = Account()
        s1 = acc.snapshot()

        acc.uid = 123
        pwd = Password(acc)
        pwd.encrypted_password = 'weak'
        acc.password = pwd
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(
            actual_result.added,
            {
                'uid': 123,
                'password': {
                    'encrypted_password': 'weak',
                },
            },
        )
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {})

    def test_account_password_deleted(self):
        acc = Account()
        acc.uid = 123
        pwd = Password(acc)
        acc.password = pwd
        s1 = acc.snapshot()

        acc.password = None
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {'password': None})

    def test_account_password_forced_changing_reason_unset(self):
        acc = Account()
        acc.uid = 123
        pwd = Password(acc)
        pwd.setup_password_changing_requirement()
        acc.password = pwd
        s1 = acc.snapshot()

        pwd.setup_password_changing_requirement(is_required=False)
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {'password': {'forced_changing_reason': None, 'forced_changing_time': None}})

    def test_account_password_changed(self):
        acc = Account()
        acc.uid = 123
        pwd = Password(acc)
        pwd.encrypted_password = 'weak'
        acc.password = pwd
        s1 = acc.snapshot()

        acc.password.encrypted_password = 'strong'
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(
            actual_result.changed,
            {
                'password': {
                    'encrypted_password': 'strong',
                }
            },
        )
        eq_(actual_result.deleted, {})

    def test_lists(self):
        acc = Account()
        acc.subscriptions = [1, 2, 3]
        s1 = acc.snapshot()

        acc.subscriptions = [2, 2, 3]
        s2 = acc.snapshot()

        actual_result = diff(s1, s2)
        eq_(actual_result.added, {})
        eq_(actual_result.changed, {})
        eq_(actual_result.deleted, {'subscriptions': [(1, None)]})
