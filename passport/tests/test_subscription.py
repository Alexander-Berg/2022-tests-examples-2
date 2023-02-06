# -*- coding: utf-8 -*-
from datetime import date
import unittest

from nose.tools import eq_
from passport.backend.core.models.domain import PartialPddDomain
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.subscription import Subscription
from passport.backend.core.services import Service


class TestSubscription(unittest.TestCase):
    def test_parse_service_1(self):
        subscription = Subscription().parse({'sid': 2})
        expected_service = Service(sid=2, slug='mail')
        eq_(subscription.service.sid, expected_service.sid)
        eq_(subscription.service.slug, expected_service.slug)

    def test_parse_service_2(self):
        subscription = Subscription().parse({'sid': Service(sid=2, slug='mail')})
        expected_service = Service(sid=2, slug='mail')
        eq_(subscription.service.sid, expected_service.sid)
        eq_(subscription.service.slug, expected_service.slug)

    def test_database_login(self):
        subscription = Subscription().parse({'sid': 2, 'login': 'login'})
        eq_(subscription.database_login, 'login')

    def test_database_login_stored_not_in_uid(self):
        acc = default_account()
        subscription = Subscription(parent=acc).parse({
            'sid': Service(sid=2, slug='mail', stores_not_uid_in_login=True),
        })
        eq_(subscription.database_login, 'login')

    def test_database_login_stored_not_in_uid_is_pdd(self):
        acc = default_account(alias='login', alias_type='pdd')
        acc.domain = PartialPddDomain(id=1, domain='domain.ru')
        subscription = Subscription(parent=acc).parse({
            'sid': Service(sid=2, slug='mail', stores_not_uid_in_login=True),
        })
        eq_(subscription.database_login, 'login@domain.ru')

    def test_parse_born_date(self):
        subscription = Subscription().parse({
            'sid': Service(sid=2, slug='mail'),
            'born_date': '2000-01-01 12:34:56',
        })
        expected_date = date(2000, 1, 1)
        eq_(subscription.created_date, expected_date)
