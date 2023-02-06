# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.db.faker.db import (
    attribute_table_insert_on_duplicate_update_key,
    insert_ignore_into_removed_aliases,
    pddsuid_table_insert,
    suid_table_insert,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    aliases_table,
    attributes_table,
    suid2_table,
)
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE,
    ATTRIBUTE_NAME_TO_TYPE,
    SID_TO_SUBSCRIPTION_ATTR as STS,
)
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.subscription import (
    Host,
    Subscription,
)
from passport.backend.core.serializers.eav.subscription import (
    password_is_creating_required_processor,
    SubscriptionEavSerializer,
)
from passport.backend.core.services import Service
from passport.backend.core.undefined import Undefined
from six import iteritems
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_


DEFAULT_UID = 123
DEFAULT_PDD_UID = 1130000000000001
DEFAULT_LOGIN_RULE = 5
DEFAULT_HOST_ID = 10
DEFAULT_LOGIN = 'test'

TEST_SUID = 99


class TestBaseSubscription(unittest.TestCase):

    def build_default_subscription(self, acc=None, svc=None, host=None, login_rule=None):
        acc = acc or default_account(uid=DEFAULT_UID, alias=DEFAULT_LOGIN)
        svc = svc or Service(sid=672, slug='test')
        host = host or Host(id=DEFAULT_HOST_ID)
        login_rule = DEFAULT_LOGIN_RULE if login_rule is None else login_rule
        return Subscription(acc, service=svc, host=host, login_rule=login_rule)


class TestNewSubscription(TestBaseSubscription):

    def _store_any_login_rule(self, svc):
        for x in range(-10, 10):
            sub = self.build_default_subscription(svc=svc, login_rule=x)

            queries = SubscriptionEavSerializer().serialize(None, sub, None)

            eq_eav_queries(
                queries,
                [
                    attribute_table_insert_on_duplicate_update_key().values([
                        {
                            'uid': DEFAULT_UID,
                            'type': ATTRIBUTE_NAME_TO_TYPE['subscription.%s.login_rule' % svc.slug],
                            'value': str(x).encode('utf8'),
                        },
                    ]),
                ],
            )

    def test_simple_subscription(self):
        svc = Service.by_sid(76)
        sub = self.build_default_subscription(svc=svc)

        queries = SubscriptionEavSerializer().serialize(None, sub, None)

        eq_eav_queries(
            queries,
            [
                attribute_table_insert_on_duplicate_update_key().values([
                    {
                        'uid': DEFAULT_UID,
                        'type': ATTRIBUTE_NAME_TO_TYPE['subscription.76'],
                        'value': b'1',
                    },
                ]),
            ],
        )

    def test_attribute_mapped_subscriptions(self):
        for sid, attr_type in iteritems(STS):
            eq_(
                'subscription.{}'.format(sid) not in ATTRIBUTE_NAME_TO_TYPE,
                True,
                '"subscription.{}" should not be in ATTRIBUTE_NAME_TO_TYPE'.format(sid)
            )

            svc = Service.by_sid(sid)
            sub = self.build_default_subscription(svc=svc)

            queries = SubscriptionEavSerializer().serialize(None, sub, None)

            eq_eav_queries(
                queries,
                [
                    attribute_table_insert_on_duplicate_update_key().values([
                        {
                            'uid': DEFAULT_UID,
                            'type': attr_type,
                            'value': b'1',
                        },
                    ]),
                ],
            )

    def test_mail(self):
        svc = Service.by_slug('mail')
        sub = self.build_default_subscription(svc=svc)
        queries = SubscriptionEavSerializer().serialize(None, sub, None)

        eq_eav_queries(
            queries,
            [
                suid_table_insert(),
                attribute_table_insert_on_duplicate_update_key().values([
                    {
                        'uid': DEFAULT_UID,
                        'type': ATTRIBUTE_NAME_TO_TYPE['subscription.mail.login_rule'],
                        'value': str(DEFAULT_LOGIN_RULE).encode('utf8'),
                    },
                ]),
                suid2_table.insert().values({'uid': sub.parent.uid, 'suid': TEST_SUID}),
            ],
            inserted_keys=[TEST_SUID],
        )

    def test_pdd_mail(self):
        svc = Service.by_slug('mail')
        sub = self.build_default_subscription(
            default_account(uid=DEFAULT_PDD_UID, alias='login@okna.ru', alias_type='pdd'),
            svc=svc,
        )
        queries = SubscriptionEavSerializer().serialize(None, sub, None)

        eq_eav_queries(
            queries,
            [
                pddsuid_table_insert(),
                attribute_table_insert_on_duplicate_update_key().values([
                    {
                        'uid': DEFAULT_PDD_UID,
                        'type': ATTRIBUTE_NAME_TO_TYPE['subscription.mail.login_rule'],
                        'value': str(DEFAULT_LOGIN_RULE).encode('utf8'),
                    },
                ]),
                suid2_table.insert().values({'uid': sub.parent.uid, 'suid': TEST_SUID}),
            ],
            inserted_keys=[TEST_SUID],
        )

    def test_mail_default_login_rule(self):
        svc = Service.by_slug('mail')
        sub = self.build_default_subscription(svc=svc, login_rule=1)

        queries = SubscriptionEavSerializer().serialize(None, sub, None)

        eq_eav_queries(
            queries,
            [
                suid_table_insert(),
                suid2_table.insert().values({'uid': DEFAULT_UID, 'suid': TEST_SUID}),
            ],
            inserted_keys=[TEST_SUID],
        )

    def test_set_default_login_rule(self):
        for slug in ['jabber', 'disk']:
            svc = Service.by_slug(slug)
            sub = self.build_default_subscription(svc=svc, login_rule=Undefined)
            queries = SubscriptionEavSerializer().serialize(None, sub, None)
            eq_eav_queries(
                queries,
                [
                    attribute_table_insert_on_duplicate_update_key().values([
                        {
                            'uid': DEFAULT_UID,
                            'type': ATTRIBUTE_NAME_TO_TYPE['subscription.%s.login_rule' % slug],
                            'value': b'1',
                        },
                    ]),
                ],
            )

    def test_jabber(self):
        svc = Service.by_slug('jabber')
        self._store_any_login_rule(svc)

    def test_wwwdgt(self):
        svc = Service.by_slug('wwwdgt')
        sub = self.build_default_subscription(svc=svc)

        queries = SubscriptionEavSerializer().serialize(None, sub, None)

        eq_eav_queries(
            queries,
            [
                attribute_table_insert_on_duplicate_update_key().values([
                    {
                        'uid': DEFAULT_UID,
                        'type': ATTRIBUTE_NAME_TO_TYPE['subscription.wwwdgt.mode'],
                        'value': str(DEFAULT_HOST_ID).encode('utf8'),
                    },
                ]),
            ],
        )

    def test_disk(self):
        svc = Service.by_slug('disk')
        self._store_any_login_rule(svc)

    def test_empty_attrs_subscriptions(self):
        for slug in ['light', 'social', 'mdalias', 'galatasaray', 'phonish']:
            svc = Service.by_slug(slug)
            sub = self.build_default_subscription(svc=svc)

            queries = SubscriptionEavSerializer().serialize(None, sub, None)

            eq_eav_queries(queries, [])

    def test_100_login_rule_eq_1(self):
        svc = Service.by_sid(100)
        sub = self.build_default_subscription(svc=svc, login_rule=1)

        queries = SubscriptionEavSerializer().serialize(None, sub, None)

        eq_eav_queries(
            queries,
            [
                attribute_table_insert_on_duplicate_update_key().values([
                    {
                        'uid': DEFAULT_UID,
                        'type': ATTRIBUTE_NAME_TO_TYPE['password.is_creating_required'],
                        'value': b'1',
                    },
                ]),
            ],
        )

    def test_100_login_rule_neq_1(self):
        svc = Service.by_sid(100)
        sub = self.build_default_subscription(svc=svc, login_rule=2)

        queries = SubscriptionEavSerializer().serialize(None, sub, None)

        eq_eav_queries(queries, [])

    def test_suid0(self):
        acc = default_account(uid=123, alias='test')
        svc = Service(sid=999, slug='foo')
        sub = Subscription(acc, service=svc, suid=1234)
        sub.suid = 0

        queries = SubscriptionEavSerializer().serialize(None, sub, None)
        eq_eav_queries(queries, [])


class TestDeleteSubscription(TestBaseSubscription):
    def _delete_subscription(self, sub, expected_queries):
        queries = SubscriptionEavSerializer().serialize(sub, None, None)
        eq_eav_queries(queries, expected_queries)

    def test_simple_subscription(self):
        svc = Service.by_sid(76)
        sub = self.build_default_subscription(svc=svc)

        queries = SubscriptionEavSerializer().serialize(sub, None, None)

        eq_eav_queries(
            queries,
            [
                attributes_table.delete().where(
                    and_(
                        attributes_table.c.uid == DEFAULT_UID,
                        attributes_table.c.type.in_([ATTRIBUTE_NAME_TO_TYPE['subscription.76']]),
                    ),
                ),
            ],
        )

    def test_attribute_mapped_subscriptions(self):
        for sid, attr_type in iteritems(STS):
            svc = Service.by_sid(sid)
            sub = self.build_default_subscription(svc=svc)

            queries = SubscriptionEavSerializer().serialize(sub, None, None)

            eq_eav_queries(
                queries,
                [
                    attributes_table.delete().where(
                        and_(
                            attributes_table.c.uid == DEFAULT_UID,
                            attributes_table.c.type.in_([attr_type]),
                        ),
                    ),
                ],
            )

    def test_mail(self):
        svc = Service.by_slug('mail')
        sub = self.build_default_subscription(svc=svc)

        self._delete_subscription(sub, [
            insert_ignore_into_removed_aliases(
                select([aliases_table.c.uid, aliases_table.c.type, aliases_table.c.value]).where(
                    and_(aliases_table.c.uid == 123, aliases_table.c.type.in_([ALIAS_NAME_TO_TYPE['mail']])),
                ),
            ),
            aliases_table.delete().where(
                and_(aliases_table.c.uid == DEFAULT_UID, aliases_table.c.type.in_([ALIAS_NAME_TO_TYPE['mail']])),
            ),
            attributes_table.delete().where(
                and_(
                    attributes_table.c.uid == DEFAULT_UID,
                    attributes_table.c.type.in_(
                        [
                            ATTRIBUTE_NAME_TO_TYPE['subscription.mail.login_rule'],
                        ],
                    ),
                ),
            ),
            suid2_table.delete().where(suid2_table.c.uid == DEFAULT_UID),
        ])

    def test_jabber(self):
        svc = Service.by_slug('jabber')
        sub = self.build_default_subscription(svc=svc)

        self._delete_subscription(sub, [
            attributes_table.delete().where(
                and_(
                    attributes_table.c.uid == DEFAULT_UID,
                    attributes_table.c.type.in_([ATTRIBUTE_NAME_TO_TYPE['subscription.jabber.login_rule']]),
                ),
            ),
        ])

    def test_wwwdgt(self):
        svc = Service.by_slug('wwwdgt')
        sub = self.build_default_subscription(svc=svc)

        self._delete_subscription(sub, [
            attributes_table.delete().where(
                and_(
                    attributes_table.c.uid == DEFAULT_UID,
                    attributes_table.c.type.in_([ATTRIBUTE_NAME_TO_TYPE['subscription.wwwdgt.mode']]),
                ),
            ),
        ])

    def test_disk(self):
        svc = Service.by_slug('disk')
        sub = self.build_default_subscription(svc=svc)

        self._delete_subscription(sub, [
            attributes_table.delete().where(
                and_(
                    attributes_table.c.uid == DEFAULT_UID,
                    attributes_table.c.type.in_([ATTRIBUTE_NAME_TO_TYPE['subscription.disk.login_rule']]),
                ),
            ),
        ])

    def test_100(self):
        svc = Service.by_sid(100)
        sub = self.build_default_subscription(svc=svc)

        self._delete_subscription(sub, [
            attributes_table.delete().where(
                and_(
                    attributes_table.c.uid == DEFAULT_UID,
                    attributes_table.c.type.in_([ATTRIBUTE_NAME_TO_TYPE['password.is_creating_required']]),
                ),
            ),
        ])


class TestChangeSubscription(TestBaseSubscription):
    def _change_to_any_login_rule(self, svc):
        for login_rule in range(-10, 10):
            sub = self.build_default_subscription(svc=svc, login_rule=-11)

            s1 = sub.snapshot()
            sub.login_rule = login_rule
            sub.login = 'login'
            sub.host.id = 1

            queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))
            eq_eav_queries(
                queries,
                [
                    attribute_table_insert_on_duplicate_update_key().values([
                        {
                            'uid': DEFAULT_UID,
                            'type': ATTRIBUTE_NAME_TO_TYPE['subscription.%s.login_rule' % svc.slug],
                            'value': str(login_rule).encode('utf8'),
                        },
                    ]),
                ],
            )

    def test_empty_queries(self):
        svc = Service.by_sid(76)
        sub = self.build_default_subscription(svc=svc)

        s1 = sub.snapshot()
        sub.login_rule = 10
        sub.host.id = 25
        sub.login = 'login'

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))
        eq_eav_queries(queries, [])

    def test_mail_change_login_rule_and_host_id(self):
        svc = Service.by_slug('mail')
        sub = self.build_default_subscription(svc=svc, login_rule=1)

        s1 = sub.snapshot()
        sub.login_rule = 2
        sub.host.id = 25

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))

        eq_eav_queries(
            queries,
            [
                attribute_table_insert_on_duplicate_update_key().values([
                    {
                        'uid': DEFAULT_UID,
                        'type': ATTRIBUTE_NAME_TO_TYPE['subscription.mail.login_rule'],
                        'value': b'2',
                    },
                ]),
            ],
        )

    def test_mail__set_to_default_login_rule_and_new_host_id__ok(self):
        svc = Service.by_slug('mail')
        sub = self.build_default_subscription(svc=svc, login_rule=10)

        s1 = sub.snapshot()
        sub.login_rule = 1
        sub.host.id = 25

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))
        eq_eav_queries(
            queries,
            [
                attributes_table.delete().where(
                    and_(
                        attributes_table.c.uid == DEFAULT_UID,
                        attributes_table.c.type.in_([ATTRIBUTE_NAME_TO_TYPE['subscription.mail.login_rule']]),
                    ),
                ),
            ],
        )

    def test_jabber(self):
        svc = Service.by_slug('jabber')
        self._change_to_any_login_rule(svc)

    def test_wwwdgt(self):
        svc = Service.by_slug('wwwdgt')
        sub = self.build_default_subscription(svc=svc)

        s1 = sub.snapshot()
        sub.login_rule = 2
        sub.host.id = 25
        sub.login = 'login'

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))

        eq_eav_queries(
            queries,
            [
                attribute_table_insert_on_duplicate_update_key().values([
                    {'uid': DEFAULT_UID, 'type': ATTRIBUTE_NAME_TO_TYPE['subscription.wwwdgt.mode'], 'value': b'25'},
                ]),
            ],
        )

    def test_disk(self):
        svc = Service.by_slug('disk')
        self._change_to_any_login_rule(svc)

    def test_100_login_rule_eq_1(self):
        svc = Service.by_sid(100)
        sub = self.build_default_subscription(svc=svc, login_rule=0)

        s1 = sub.snapshot()
        sub.login_rule = 1
        sub.host.id = 25
        sub.login = 'login'

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))

        eq_eav_queries(
            queries,
            [
                attribute_table_insert_on_duplicate_update_key().values([
                    {
                        'uid': DEFAULT_UID,
                        'type': ATTRIBUTE_NAME_TO_TYPE['password.is_creating_required'],
                        'value': b'1',
                    },
                ]),
            ],
        )

    def test_100_login_rule_neq_1(self):
        svc = Service.by_sid(100)
        sub = self.build_default_subscription(svc=svc, login_rule=1)

        s1 = sub.snapshot()
        sub.login_rule = 25
        sub.host.id = 25
        sub.login = 'login'

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))

        eq_eav_queries(
            queries,
            [
                attributes_table.delete().where(
                    and_(
                        attributes_table.c.uid == DEFAULT_UID,
                        attributes_table.c.type.in_([ATTRIBUTE_NAME_TO_TYPE['password.is_creating_required']]),
                    ),
                ),
            ],
        )

    def test_669(self):
        svc = Service.by_slug('yastaff')
        sub = self.build_default_subscription(svc=svc)
        sub.login = 'blabla'

        s1 = sub.snapshot()
        sub.login_rule = 10
        sub.host.id = 25
        sub.login = 'yalogin'

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))

        eq_eav_queries(queries, [])

    def test_suid0(self):
        svc = Service.by_slug('mail')
        sub = self.build_default_subscription(svc=svc, login_rule=1)

        s1 = sub.snapshot()
        sub.login_rule = 1
        sub.suid = 0

        queries = SubscriptionEavSerializer().serialize(s1, sub, diff(s1, sub))
        eq_eav_queries(queries, [])


class TestSubscriptionProcessors(unittest.TestCase):
    def test_password_is_creating_required_processor(self):
        # "1", если subscription.login_rule.100 == 1
        eq_(password_is_creating_required_processor(None), None)
        eq_(password_is_creating_required_processor(''), None)
        for x in range(-10, 10):
            if x == 1:
                eq_(password_is_creating_required_processor(x), '1')
            else:
                eq_(password_is_creating_required_processor(x), None)
