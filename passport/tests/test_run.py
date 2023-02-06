# -*- coding: utf-8 -*-
import unittest

from nose.tools import assert_raises
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.differ import diff
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.processor import run_eav
from passport.backend.core.services import SERVICES


class TestRunDB(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()

    def tearDown(self):
        self.db.stop()
        del self.db

    def test_add_same_subscription__ok(self):
        """Проверяется безошибочная повторная подписка на "обычный" sid"""
        uid = 123
        acc = default_account(uid=uid, alias='testlogin').parse({
            'subscriptions': {8: {'sid': 8, 'host_id': 12, 'login': 'testlogin'}},
        })
        run_eav(None, acc, diff(None, acc))

        service = SERVICES['disk']
        sid = service.sid

        s1 = acc.snapshot()
        acc.parse({'subscriptions': {sid: {'sid': sid, 'login_rule': 100, 'suid': 555}}})

        run_eav(s1, acc, diff(s1, acc))
        self.db.check('attributes', 'subscription.disk.login_rule', '100', uid=uid, db='passportdbshard1')

        run_eav(s1, acc, diff(s1, acc))
        self.db.check('attributes', 'subscription.disk.login_rule', '100', uid=uid, db='passportdbshard1')

    def test_add_mail_subscription__integrity_error(self):
        """
        Проверяем что при повторной подписке на mail возникает ошибка записи в таблицу suid2
        """
        uid = 123
        acc = default_account(uid=uid, alias='testlogin').parse({
            'subscriptions': {8: {'sid': 8, 'host_id': 12, 'login': 'testlogin'}},
        })
        run_eav(None, acc, diff(None, acc))

        service = SERVICES['mail']
        sid = service.sid

        s1 = acc.snapshot()
        acc.parse({'subscriptions': {sid: {'sid': sid, 'login_rule': 100, 'suid': 555}}})

        run_eav(s1, acc, diff(s1, acc))
        self.db.check('suid2', 'suid', 555, uid=uid, db='passportdbcentral')
        self.db.check('attributes', 'subscription.mail.login_rule', '100', uid=uid, db='passportdbshard1')

        # Новая схема падает
        with assert_raises(DBError):
            run_eav(s1, acc, diff(s1, acc))
