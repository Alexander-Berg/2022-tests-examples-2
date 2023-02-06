# -*- coding: utf-8 -*-

import json

from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.api.test.views import BaseMdapiTestCase
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_find_pdd_accounts_response,
    blackbox_hosted_domains_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.federal_configs_api import FederalConfigsApiNotFoundError
from passport.backend.core.builders.federal_configs_api.faker import federal_config_ok
from passport.backend.core.dbmanager.manager import get_dbm
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE
from passport.backend.core.models.domain import Domain
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_ADMIN_UID = 1
TEST_CYRILLIC_DOMAIN = u'окна.рф'.encode('idna')
TEST_CYRILLIC_ALIAS = u'ёлки.ком'.encode('idna')
TEST_DEFAULT_USER_LOGIN = 'default'
TEST_PDD_LOGIN = 'pdd@okna.ru'
TEST_DEFAULT_USER_UID = 65535
TEST_DOMAIN = 'naydex.ru'
TEST_DOMAIN_ALIAS = 'another-naydex.ru'
TEST_YANDEX_DOMAIN = 'yandex.ru'
TEST_YANDEX_SUBDOMAIN = 'vesna.yandex.ru'
TEST_YANDEX_DOMAIN_ALIAS = 'ya.ru'
TEST_DOMAIN_ID = 1
TEST_DOMAIN_ALIAS_ID = TEST_DOMAIN_ID + 1
TEST_NEW_ADMIN_UID = TEST_ADMIN_UID + 1
TEST_ORGANIZATION_NAME = 'Organization'
TEST_UID = TEST_ADMIN_UID + 2
PDD_ADMIN_SID = 104
TEST_IDP_DOMAIN_ID = 2997121  # id домена sso-adfs-test-domain.com в тестинге


@with_settings_hosts
class PddAddDomainTestCase(BaseMdapiTestCase):
    url = '/1/bundle/pdd/domain/?consumer=dev'
    mocked_grants = {
        'domain': ['add'],
    }

    def setUp(self):
        super(PddAddDomainTestCase, self).setUp()
        self.env.statbox.bind_entry(
            'add_domain',
            mode='mdapi',
            action='pdd_add_domain',
            admin_uid=str(TEST_ADMIN_UID),
            domain=TEST_DOMAIN,
            domain_id=str(TEST_DOMAIN_ID),
            ip='3.3.3.3',
            user_agent='curl',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'domain_modification',
            domain_id=str(TEST_DOMAIN_ID),
            consumer='dev',
            old='-',
            user_agent='curl',
            ip='3.3.3.3',
            event='domain_modification',
            operation='created',
        )
        self.env.statbox.bind_entry(
            'add_sid_104',
            uid=str(TEST_ADMIN_UID),
            ip='3.3.3.3',
            entity='subscriptions',
            user_agent='curl',
            sid='104',
            consumer='dev',
            event='account_modification',
            operation='added',
        )

    def check_statbox_entries(self, mx=False, enabled=True, subscription_created=True, domain=TEST_DOMAIN):
        entries = []
        if subscription_created:
            entries.append(
                self.env.statbox.entry('add_sid_104'),
            )
        entries += [
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_name',
                new=domain,
            ),
            self.env.statbox.entry(
                'add_domain',
                mx='1' if mx else '0',
                enabled='1' if enabled else '0',
                domain=domain,
                domain_id=str(TEST_DOMAIN_ID)
            ),
        ]
        self.env.statbox.assert_has_written(entries)

    def check_response_ok(self, response, subscription_created=True, domain=TEST_DOMAIN):
        data = super(PddAddDomainTestCase, self).check_response_ok(response)
        # Проверяем, что нам отдали доменное имя
        eq_(data['domain'], domain.decode('idna'))

        # Информация о доменах хранится на центральном узле БД
        eq_(self.env.db.query_count('passportdbcentral'), 2)
        # Информация о подписках хранится на шардах
        eq_(self.env.db.query_count('passportdbshard1'), 1 if subscription_created else 0)

        if subscription_created:
            # Проверяем, что новоиспеченный админ ПДД отмечен соответствующим образом
            self.env.db.check(
                'attributes',
                'account.is_pdd_admin',
                '1',
                uid=TEST_ADMIN_UID,
                db='passportdbshard1',
            )
            self.assert_events_are_logged(
                self.env.handle_mock,
                {
                    'action': 'make_pdd_admin',
                    'sid.add': '104',
                    'user_agent': 'curl',
                    'consumer': 'dev',
                },
            )

        # Проверяем, что домен создался
        self.env.db.check(
            'domains',
            'name',
            domain,
            admin_uid=TEST_ADMIN_UID,
            db='passportdbcentral',
        )

    @parameterized.expand(
        [
            (TEST_DOMAIN,),
            (TEST_YANDEX_SUBDOMAIN,),
        ]
    )
    def test_ok(self, domain):
        # Добавление ранее несуществовавшего домена проходит без проблем.
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(TEST_ADMIN_UID),
        )

        resp = self.make_request(data={
            'domain': domain,
            'admin_uid': TEST_ADMIN_UID,
        })
        self.check_response_ok(resp, domain=domain)
        self.check_statbox_entries(mx=False, enabled=True, domain=domain)

    def test_ok_with_additional_parameters(self):
        """
        Добавлением ранее несуществовавшего домена проходит без проблем,
        особенно если указать ему дополнительные параметры вроде использования
        MX или флага активности.
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(TEST_ADMIN_UID),
        )

        resp = self.make_request(data={
            'domain': TEST_DOMAIN,
            'admin_uid': TEST_ADMIN_UID,
            'mx': 'true',
            'enabled': 'false',
        })
        self.check_response_ok(resp)
        self.check_statbox_entries(mx=True, enabled=False)

        # Проверяем, что переданные нами параметры зафиксировались.
        self.env.db.check(
            'domains',
            'name',
            TEST_DOMAIN,
            admin_uid=TEST_ADMIN_UID,
            mx=True,
            enabled=False,
            db='passportdbcentral',
        )

    def test_ok_with_cyrillic_domain(self):
        """
        Добавление незакодированного кирилического домена проходит без проблем.
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(TEST_ADMIN_UID),
        )

        resp = self.make_request(data={
            'domain': TEST_CYRILLIC_DOMAIN.decode('idna'),
            'admin_uid': TEST_ADMIN_UID,
        })
        self.check_response_ok(resp, domain=TEST_CYRILLIC_DOMAIN)
        self.check_statbox_entries(mx=False, enabled=True, domain=TEST_CYRILLIC_DOMAIN)

    def test_domain_already_exists(self):
        """
        Добавление домена с уже существующим именем приводит
        к ошибке.
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(TEST_ADMIN_UID),
        )

        resp = self.make_request(data={
            'domain': TEST_DOMAIN,
            'admin_uid': TEST_ADMIN_UID,
        })
        self.check_error_response(
            resp,
            [u'domain.already_exists'],
        )
        self.env.statbox.assert_has_written([])

    def test_error_on_add_yandex_domain(self):
        """
        Добавление домена яндекса как своего приводит
        к ошибке.
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(TEST_ADMIN_UID),
        )

        resp = self.make_request(data={
            'domain': TEST_YANDEX_DOMAIN,
            'admin_uid': TEST_ADMIN_UID,
        })
        self.check_error_response(
            resp,
            ['domain.native'],
        )
        self.env.statbox.assert_has_written([])

    def test_pdd_can_become_admin(self):
        """
        ПДДшник может просто так взять и стать администратором домена (нужно для Коннекта)
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_ADMIN_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )

        resp = self.make_request(data={
            'domain': TEST_DOMAIN,
            'admin_uid': TEST_ADMIN_UID,
        })
        self.check_response_ok(resp)
        self.check_statbox_entries()

    def test_pdd_is_admin_already(self):
        """
        ПДДшник, которого уже сделали администратором, может создавать новые домены
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_ADMIN_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                subscribed_to=[PDD_ADMIN_SID],
            ),
        )

        resp = self.make_request(data={
            'domain': TEST_DOMAIN,
            'admin_uid': TEST_ADMIN_UID,
        })
        self.check_response_ok(resp, subscription_created=False)
        self.check_statbox_entries(mx=False, enabled=True, subscription_created=False)


@with_settings_hosts(OPTIONS_USE_NEW_SERIALIATION_SCHEME=True)
class PddEditDomainTestCase(BaseMdapiTestCase):
    url = '/1/bundle/pdd/domain/%s/?consumer=dev' % TEST_DOMAIN_ID
    mocked_grants = {
        'domain': ['edit'],
    }

    def setUp(self):
        super(PddEditDomainTestCase, self).setUp()
        self.setup_statbox_templates()

        self.setup_domain_data()

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_ADMIN_UID,
                subscribed_to=[PDD_ADMIN_SID],
            ),
        )

    def setup_domain_data(self, domain=TEST_DOMAIN, default_uid=None, admin_uid=TEST_ADMIN_UID,
                          mx=False, is_master=True, organization_name=None,
                          is_enabled=True, can_users_change_password=True, display_master_id=None,
                          ):
        options = dict()
        options['1'] = 1 if can_users_change_password else 0
        if organization_name is not None:
            options['2'] = organization_name
        if display_master_id is not None:
            options['3'] = display_master_id

        self.test_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': str(default_uid or 0),
                    'admin': str(admin_uid or 0),
                    'domid': str(TEST_DOMAIN_ID if is_master else TEST_DOMAIN_ID + 1),
                    'options': json.dumps(options),
                    'slaves': '',
                    'master_domain': '' if is_master else str(TEST_DOMAIN_ID),
                    'mx': str(int(mx)),
                    'domain': domain,
                    'ena': '1' if is_enabled else '0',
                },
            ],
        }
        test_domain = Domain().parse(self.test_domain_data['hosted_domains'][0])
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            self.test_domain_data,
        )

        table, db_name = self.env.db.get_table_and_db('domains', 'passportdbcentral')
        get_dbm(db_name).get_engine().execute(table.delete())
        self.env.db._serialize_to_eav(test_domain)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'edit_domain',
            mode='mdapi',
            action='pdd_domain_edit',
            admin_uid='1',
            domain=TEST_DOMAIN,
            domain_id=str(TEST_DOMAIN_ID),
            default_uid='0',
            mx='0',
            enabled='1',
            can_users_change_password='1',
            ip='3.3.3.3',
            user_agent='curl',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'domain_modification',
            domain_id=str(TEST_DOMAIN_ID),
            event='domain_modification',
            consumer='dev',
            ip='3.3.3.3',
            old='-',
            user_agent='curl',
            operation='created',
        )
        self.env.statbox.bind_entry(
            'edit_sid_104',
            uid=str(TEST_ADMIN_UID),
            ip='3.3.3.3',
            entity='subscriptions',
            user_agent='curl',
            sid='104',
            consumer='dev',
            event='account_modification',
            operation='added',
        )

    def test_ok(self):
        resp = self.make_request(data={
            'mx': 'true',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_domain',
                mx='1',
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_dont_touch_missing_fields(self):
        self.setup_domain_data(
            organization_name=TEST_ORGANIZATION_NAME,
            is_enabled=False,
            can_users_change_password=False,
        )

        resp = self.make_request()
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_domain',
                enabled='0',
                can_users_change_password='0',
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_remove_fields(self):
        self.setup_domain_data(
            organization_name=TEST_ORGANIZATION_NAME,
            display_master_id=TEST_DOMAIN_ALIAS_ID,
        )

        resp = self.make_request(data={
            'organization_name': '',
            'display_master_id': '',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_organization_name',
                operation='deleted',
                old=str(TEST_ORGANIZATION_NAME),
                new='-',
            ),
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_display_master_id',
                operation='deleted',
                old=str(TEST_DOMAIN_ALIAS_ID),
                new='-',
            ),
            self.env.statbox.entry('edit_domain'),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_cyrillic_domain(self):
        self.setup_domain_data(domain=TEST_CYRILLIC_DOMAIN)

        resp = self.make_request(data={
            'mx': 'true',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_domain',
                domain=TEST_CYRILLIC_DOMAIN,
                mx='1',
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_full_data(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    uid=TEST_DEFAULT_USER_UID,
                    login='%s@%s' % (
                        TEST_DEFAULT_USER_LOGIN,
                        TEST_DOMAIN,
                    ),
                ),
                blackbox_userinfo_response(
                    uid=TEST_ADMIN_UID,
                    subscribed_to=[PDD_ADMIN_SID],
                ),
                blackbox_userinfo_response(uid=TEST_NEW_ADMIN_UID),
            ],
        )

        resp = self.make_request(data={
            'mx': 'true',
            'enabled': 'false',
            'admin_uid': TEST_NEW_ADMIN_UID,
            'default': '%s' % TEST_DEFAULT_USER_LOGIN,
            'can_users_change_password': True,
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_sid_104',
                operation='added',
                uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_domain',
                mx='1',
                enabled='0',
                admin_uid=str(TEST_NEW_ADMIN_UID),
                default_uid=str(TEST_DEFAULT_USER_UID),
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check(
            'domains',
            'name',
            TEST_DOMAIN,
            db='passportdbcentral',
        )
        self.env.db.check(
            'domains',
            'enabled',
            False,
            db='passportdbcentral',
        )
        self.env.db.check(
            'attributes',
            'account.is_pdd_admin',
            '1',
            uid=TEST_NEW_ADMIN_UID,
            db='passportdbshard1',
        )
        self.env.db.check_missing(
            'attributes',
            'account.is_pdd_admin',
            uid=TEST_ADMIN_UID,
            db='passportdbshard1',
        )

    def test_ok_turn_mx_off(self):
        self.setup_domain_data(mx=True)

        resp = self.make_request(data={
            'mx': 'false',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_domain',
                mx='0',
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_default_by_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_DEFAULT_USER_UID,
                login='%s@%s' % (
                    TEST_DEFAULT_USER_LOGIN,
                    TEST_DOMAIN,
                ),
            ),
        )
        resp = self.make_request(data={
            'default': TEST_DEFAULT_USER_LOGIN,
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_domain',
                default_uid=str(TEST_DEFAULT_USER_UID),
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_delete_default(self):
        self.setup_domain_data(default_uid=1)
        resp = self.make_request(data={
            'default': '',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_domain',
                default_uid='0',
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_glogout_all_on_domain(self):
        resp = self.make_request(data={
            'glogouted': '1',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_domain',
                glogout_time=TimeNow(),
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_set_organization_name(self):
        resp = self.make_request(data={
            'organization_name': TEST_ORGANIZATION_NAME,
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_organization_name',
                new=TEST_ORGANIZATION_NAME,
            ),
            self.env.statbox.entry(
                'edit_domain',
            ),
        ])
        self.env.db.check(
            'domains',
            'options',
            '{"1": 1, "2": "%s"}' % TEST_ORGANIZATION_NAME,
            db='passportdbcentral',
        )

        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

    def test_ok_no_old_admin(self):
        self.setup_domain_data(admin_uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_NEW_ADMIN_UID),
        )

        resp = self.make_request(data={
            'admin_uid': TEST_NEW_ADMIN_UID,
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_sid_104',
                operation='added',
                uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_domain',
                admin_uid=str(TEST_NEW_ADMIN_UID),
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check(
            'attributes',
            'account.is_pdd_admin',
            '1',
            uid=TEST_NEW_ADMIN_UID,
            db='passportdbshard1',
        )

    def test_ok_old_admin_deleted(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=None),
                blackbox_userinfo_response(
                    TEST_NEW_ADMIN_UID,
                ),
            ],
        )

        resp = self.make_request(data={
            'admin_uid': TEST_NEW_ADMIN_UID,
            'mx': 'true',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_sid_104',
                operation='added',
                uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_domain',
                mx='1',
                admin_uid=str(TEST_NEW_ADMIN_UID),
            ),
        ])
        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

    def test_ok_admin_not_enabled(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    TEST_ADMIN_UID,
                    subscribed_to=[PDD_ADMIN_SID],
                ),
                blackbox_userinfo_response(
                    TEST_NEW_ADMIN_UID,
                    enabled=False,
                ),
            ],
        )

        resp = self.make_request(data={
            'admin_uid': TEST_NEW_ADMIN_UID,
            'mx': 'true',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_sid_104',
                operation='added',
                uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_domain',
                mx='1',
                admin_uid=str(TEST_NEW_ADMIN_UID),
            ),
        ])
        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

    def test_ok_old_admin_not_enabled(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    TEST_ADMIN_UID,
                    subscribed_to=[PDD_ADMIN_SID],
                    enabled=False,
                ),
                blackbox_userinfo_response(
                    TEST_NEW_ADMIN_UID,
                ),
            ],
        )

        resp = self.make_request(data={
            'admin_uid': TEST_NEW_ADMIN_UID,
            'mx': 'true',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_sid_104',
                operation='added',
                uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_domain',
                mx='1',
                admin_uid=str(TEST_NEW_ADMIN_UID),
            ),
        ])
        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

    def test_pdd_can_become_admin(self):
        self.setup_domain_data(admin_uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_NEW_ADMIN_UID,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )

        resp = self.make_request(data={
            'admin_uid': TEST_NEW_ADMIN_UID,
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_sid_104',
                operation='added',
                uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_domain',
                admin_uid=str(TEST_NEW_ADMIN_UID),
            ),
        ])

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 1)

        self.env.db.check(
            'domains',
            'admin_uid',
            TEST_NEW_ADMIN_UID,
            db='passportdbcentral',
        )
        self.env.db.check(
            'attributes',
            'account.is_pdd_admin',
            '1',
            uid=TEST_NEW_ADMIN_UID,
            db='passportdbshard1',
        )

    def test_ok_last_remaining_domain_on_admin(self):
        """
        Если у старого админа этот домен был последним, то мы должны снять с
        него 104 сид.
        """
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    TEST_ADMIN_UID,
                    subscribed_to=[PDD_ADMIN_SID],
                ),
                blackbox_userinfo_response(TEST_NEW_ADMIN_UID),
            ],
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                dict(hosted_domains={}),
            ],
        )
        resp = self.make_request(data={
            'admin_uid': TEST_NEW_ADMIN_UID,
            'mx': 'true',
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'edit_sid_104',
                operation='added',
                uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_domain',
                mx='1',
                admin_uid=str(TEST_NEW_ADMIN_UID),
            ),
            self.env.statbox.entry(
                'edit_sid_104',
                operation='removed',
                uid=str(TEST_ADMIN_UID),
            ),
        ])
        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

    def test_ok_set_display_master_id(self):
        alias_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ID + 1),
                    'options': '{}',
                    'slaves': '',
                    'master_domain': TEST_DOMAIN_ID,
                    'mx': '0',
                    'domain': TEST_DOMAIN_ALIAS,
                    'ena': '1',
                },
            ],
        }
        master_domain_data = self.test_domain_data.copy()
        master_domain_data['hosted_domains'][0]['slaves'] = TEST_DOMAIN_ALIAS
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                master_domain_data,
                alias_domain_data,
            ],
        )

        resp = self.make_request(data={
            'display_master_id': TEST_DOMAIN_ID + 1,
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_display_master_id',
                new=str(TEST_DOMAIN_ID + 1),
            ),
            self.env.statbox.entry(
                'edit_domain',
                display_master_id=str(TEST_DOMAIN_ID + 1),
            ),
        ])
        eq_(self.env.db.query_count('passportdbcentral'), 2)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.env.db.check(
            'domains',
            'options',
            '{"1": 1, "3": 2}',
            db='passportdbcentral',
        )
        self.env.blackbox.requests[0].assert_query_contains(
            {
                'method': 'hosted_domains',
                'domain_id': str(TEST_DOMAIN_ID),
                'aliases': 'True',
            },
        )
        self.env.blackbox.requests[1].assert_query_contains(
            {
                'method': 'hosted_domains',
                'domain_id': str(TEST_DOMAIN_ID + 1),
            },
        )

    def test_domain_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        resp = self.make_request(data={
            'mx': 'true',
        })
        self.check_error_response(
            resp,
            [u'domain.not_found'],
        )
        self.env.statbox.assert_has_written([])

    def test_admin_not_found(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(TEST_ADMIN_UID, subscribed_to=[PDD_ADMIN_SID]),
                blackbox_userinfo_response(uid=None),
            ],
        )

        resp = self.make_request(data={
            'mx': 'true',
            'admin_uid': 42,
        })
        self.check_error_response(
            resp,
            [u'account.not_found'],
        )
        self.env.statbox.assert_has_written([])

    def test_set_display_master_id_not_our_alias(self):
        alias_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ID + 1),
                    'options': '{}',
                    'slaves': '',
                    'master_domain': TEST_DOMAIN_ID,
                    'mx': '0',
                    'domain': 'not-' + TEST_DOMAIN_ALIAS,
                    'ena': '1',
                },
            ],
        }
        master_domain_data = self.test_domain_data.copy()
        master_domain_data['hosted_domains'][0]['slaves'] = TEST_DOMAIN_ALIAS
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                master_domain_data,
                alias_domain_data,
            ],
        )
        resp = self.make_request(data={
            'display_master_id': TEST_DOMAIN_ID + 1,
        })
        self.check_error_response(
            resp,
            ['domain_alias.not_found'],
        )
        self.env.blackbox.requests[0].assert_query_contains(
            {
                'method': 'hosted_domains',
                'domain_id': '1',
                'aliases': 'True',
            },
        )
        self.env.blackbox.requests[1].assert_query_contains(
            {
                'method': 'hosted_domains',
                'domain_id': '2',
            },
        )


@with_settings_hosts()
class PddDeleteDomainTestCase(BaseMdapiTestCase):
    url = '/1/bundle/pdd/domain/%s/?consumer=dev' % TEST_DOMAIN_ID
    method = 'DELETE'
    mocked_grants = {
        'domain': ['delete'],
    }

    def setUp(self):
        super(PddDeleteDomainTestCase, self).setUp()
        self.setup_statbox_templates()
        self.env.blackbox.set_blackbox_response_value(
            'find_pdd_accounts',
            blackbox_find_pdd_accounts_response([], total_count=0),
        )
        self.env.federal_configs_api.set_response_side_effect('config_by_domain_id', FederalConfigsApiNotFoundError())

        self.test_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': '1',
                    'options': '{}',
                    'slaves': '',
                    'master_domain': '',
                    'mx': '0',
                    'domain': TEST_DOMAIN,
                    'ena': '1',
                },
            ],
        }
        test_domain = Domain().parse(self.test_domain_data['hosted_domains'][0])
        self.env.db._serialize_to_eav(test_domain)
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            self.test_domain_data,
        )

        self.env.db.insert(
            'aliases',
            uid=TEST_UID,
            type=ALIAS_NAME_TO_TYPE['pdd'],
            surrogate_type=str(ALIAS_NAME_TO_TYPE['pdd']),
            value='%i/test' % TEST_DOMAIN_ID,
            db='passportdbcentral',
        )
        self.env.db.insert(
            'aliases',
            uid=TEST_UID + 1,
            type=ALIAS_NAME_TO_TYPE['pddalias'],
            surrogate_type=str(ALIAS_NAME_TO_TYPE['pddalias']),
            value='%i/test2' % TEST_DOMAIN_ID,
            db='passportdbcentral',
        )
        # Обычный алиас, который не должен быть удален в ходе очистки доменных
        self.env.db.insert(
            'aliases',
            uid=TEST_UID,
            type=ALIAS_NAME_TO_TYPE['altdomain'],
            surrogate_type=str(ALIAS_NAME_TO_TYPE['altdomain']),
            value='%i/test2' % TEST_DOMAIN_ID,
            db='passportdbcentral',
        )
        self.env.db.insert(
            'suid2',
            uid=TEST_UID,
            suid=1,
            db='passportdbcentral',
        )

    def assert_only_domain_aliases_removed(self, domain=TEST_DOMAIN):
        self.env.db.check(
            'removed_aliases',
            'value',
            '%s/test' % domain,
            uid=TEST_UID,
            type=ALIAS_NAME_TO_TYPE['pdd'],
            db='passportdbcentral',
        )
        self.env.db.check(
            'removed_aliases',
            'value',
            '%s/test2' % domain,
            uid=TEST_UID + 1,
            type=ALIAS_NAME_TO_TYPE['pddalias'],
            db='passportdbcentral',
        )
        self.env.db.check_missing(
            'aliases',
            type=ALIAS_NAME_TO_TYPE['pdd'],
            value='%i/test' % TEST_DOMAIN_ID,
            db='passportdbcentral',
        )
        self.env.db.check_missing(
            'aliases',
            value='%i/test2' % TEST_DOMAIN_ID,
            type=ALIAS_NAME_TO_TYPE['pddalias'],
            db='passportdbcentral',
        )
        self.env.db.check_missing(
            'suid2',
            uid=TEST_UID,
            db='passportdbcentral',
        )
        self.env.db.check(
            'aliases',
            'uid',
            TEST_UID,
            type=ALIAS_NAME_TO_TYPE['altdomain'],
            value='%i/test2' % TEST_DOMAIN_ID,
            db='passportdbcentral',
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'edit_sid_104',
            uid=str(TEST_ADMIN_UID),
            ip='3.3.3.3',
            entity='subscriptions',
            user_agent='curl',
            sid='104',
            consumer='dev',
            event='account_modification',
            operation='added',
        )
        self.env.statbox.bind_entry(
            'domain_modification',
            domain_id=str(TEST_DOMAIN_ID),
            ip='3.3.3.3',
            user_agent='curl',
            consumer='dev',
            operation='deleted',
            new='-',
            event='domain_modification',
        )
        self.env.statbox.bind_entry(
            'delete_domain',
            mode='mdapi',
            action='pdd_domain_delete',
            domain=TEST_DOMAIN,
            domain_id=str(TEST_DOMAIN_ID),
            ip='3.3.3.3',
            user_agent='curl',
            consumer='dev',
        )

    def test_delete_by_name(self):
        resp = self.make_request()
        self.check_response_ok(resp)
        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing(
            'domains',
            name=TEST_DOMAIN,
            db='passportdbcentral',
        )
        self.assert_only_domain_aliases_removed()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_name',
                old=TEST_DOMAIN.encode('idna'),
            ),
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_id',
                old=str(TEST_DOMAIN_ID),
            ),
            self.env.statbox.entry('delete_domain'),
        ])

    def test_delete_cyrillic_domain(self):
        test_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ID),
                    'options': '{}',
                    'slaves': '',
                    'master_domain': '',
                    'mx': '0',
                    'domain': TEST_CYRILLIC_DOMAIN,
                    'ena': '1',
                },
            ],
        }

        table, db_name = self.env.db.get_table_and_db('domains', 'passportdbcentral')
        get_dbm(db_name).get_engine().execute(table.delete())

        test_domain = Domain().parse(test_domain_data['hosted_domains'][0])
        self.env.db._serialize_to_eav(test_domain)
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            test_domain_data,
        )

        self.url = '/1/bundle/pdd/domain/%s/?consumer=dev' % TEST_DOMAIN_ID
        resp = self.make_request()
        self.check_response_ok(resp)
        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing(
            'domains',
            name=TEST_CYRILLIC_DOMAIN,
            db='passportdbcentral',
        )
        self.assert_only_domain_aliases_removed(domain=TEST_CYRILLIC_DOMAIN)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_name',
                old=TEST_CYRILLIC_DOMAIN,
            ),
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_id',
                old=str(TEST_DOMAIN_ID),
            ),
            self.env.statbox.entry(
                'delete_domain',
                domain=TEST_CYRILLIC_DOMAIN,
            ),
        ])

    def test_delete_by_id(self):
        self.url = '/1/bundle/pdd/domain/%d/?consumer=dev' % TEST_DOMAIN_ID
        resp = self.make_request()
        self.check_response_ok(resp)
        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.env.db.check_missing(
            'domains',
            domain_id=TEST_DOMAIN_ID,
            db='passportdbcentral',
        )
        self.assert_only_domain_aliases_removed()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_name',
                old=TEST_DOMAIN.encode('idna'),
            ),
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_id',
                old=str(TEST_DOMAIN_ID),
            ),
            self.env.statbox.entry('delete_domain'),
        ])

    def test_delete_domain_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.url = '/1/bundle/pdd/domain/%s/?consumer=dev' % (TEST_DOMAIN_ID + 42)
        resp = self.make_request()
        self.check_error_response(
            resp,
            ['domain.not_found'],
        )
        self.env.db.check(
            'domains',
            'name',
            TEST_DOMAIN,
            db='passportdbcentral',
        )
        self.env.statbox.assert_has_written([])

    def test_delete_saml_sso_domain(self):
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())
        self.url = '/1/bundle/pdd/domain/%s/?consumer=dev' % TEST_DOMAIN_ID

        resp = self.make_request()
        self.check_error_response(
            resp,
            ['domain.invalid_type'],
        )
        self.env.db.check(
            'domains',
            'name',
            TEST_DOMAIN,
            db='passportdbcentral',
        )
        self.env.statbox.assert_has_written([])

    def test_delete_users_remaining_by_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'find_pdd_accounts',
            blackbox_find_pdd_accounts_response(uids=[TEST_UID], count=1),
        )

        self.url = '/1/bundle/pdd/domain/%d/?consumer=dev' % TEST_DOMAIN_ID
        resp = self.make_request()
        self.check_error_response(
            resp,
            ['domain.users_remaining'],
        )
        self.env.db.check(
            'domains',
            'name',
            TEST_DOMAIN,
            db='passportdbcentral',
        )
        self.env.statbox.assert_has_written([])

    def test_delete_last_domain_from_admin(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    TEST_ADMIN_UID,
                    subscribed_to=[PDD_ADMIN_SID],
                    enabled=True,
                ),
            ],
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                blackbox_hosted_domains_response(count=0),
            ],
        )

        resp = self.make_request()
        self.check_response_ok(resp)
        eq_(self.env.db.query_count('passportdbcentral'), 5)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.env.db.check_missing(
            'domains',
            domain_id=TEST_DOMAIN_ID,
            db='passportdbcentral',
        )

        self.assert_only_domain_aliases_removed()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_name',
                old=TEST_DOMAIN.encode('idna'),
            ),
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_id',
                old=str(TEST_DOMAIN_ID),
            ),
            self.env.statbox.entry(
                'edit_sid_104',
                operation='removed',
                uid=str(TEST_ADMIN_UID),
            ),
            self.env.statbox.entry('delete_domain'),
        ])

    def test_delete_domain_with_nonexistent_admin(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                blackbox_hosted_domains_response(count=0),
            ],
        )

        resp = self.make_request()
        self.check_response_ok(resp)

    def test_delete_domain_with_blocked_admin(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_ADMIN_UID,
                subscribed_to=[PDD_ADMIN_SID],
                enabled=False,
            ),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                blackbox_hosted_domains_response(count=0),
            ],
        )

        resp = self.make_request()
        self.check_response_ok(resp)


@with_settings_hosts
class PddAliasDomainTestCase(BaseMdapiTestCase):
    url = '/1/bundle/pdd/domain/%s/alias/?consumer=dev' % TEST_DOMAIN_ID
    mocked_grants = {
        'domain_alias': ['add'],
    }

    def setUp(self):
        super(PddAliasDomainTestCase, self).setUp()
        self.setup_statbox_templates()

        self.test_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ID),
                    'options': '{}',
                    'slaves': '',
                    'master_domain': '',
                    'mx': '0',
                    'domain': TEST_DOMAIN,
                    'ena': '1',
                },
            ],
        }
        self.test_alias_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ID + 1),
                    'options': '{}',
                    'slaves': '',
                    'master_domain': TEST_DOMAIN,
                    'mx': '0',
                    'domain': TEST_DOMAIN,
                    'ena': '1',
                },
            ],
        }

        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                dict(hosted_domains={}),
            ],
        )

    @parameterized.expand(
        [
            (TEST_DOMAIN_ALIAS,),
            (TEST_YANDEX_SUBDOMAIN,),
        ]
    )
    def test_alias_creation_ok(self, domain_alias):
        resp = self.make_request(data={
            'alias': domain_alias,
        })
        self.check_response_ok(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('alias_domain',
                                   alias=domain_alias,
                                   ),
        ])
        self.env.db.check(
            'domains',
            'name',
            domain_alias,
            master_domain_id=TEST_DOMAIN_ID,
            db='passportdbcentral',
        )

    def test_alias_creation_error_domain_exists(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                blackbox_hosted_domains_response(count=1),
            ],
        )
        resp = self.make_request(data={
            'alias': TEST_DOMAIN_ALIAS,
        })
        self.check_error_response(
            resp,
            ['domain.already_exists'],
        )

    def test_error_on_add_yandex_domain(self):
        """
        Добавление в алиас домена яндекса как своего приводит
        к ошибке.
        """
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                blackbox_hosted_domains_response(count=1),
            ],
        )
        resp = self.make_request(data={
            'alias': TEST_YANDEX_DOMAIN_ALIAS,
        })

        self.check_error_response(
            resp,
            ['alias.native'],
        )

    def test_alias_creation_error_master_is_an_alias(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_alias_data,
            ],
        )
        resp = self.make_request(data={
            'alias': TEST_DOMAIN_ALIAS,
        })
        self.check_error_response(
            resp,
            ['domain.master_is_alias'],
        )

    def test_alias_creation_error_alias_exists(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                self.test_alias_data,
            ],
        )
        resp = self.make_request(data={
            'alias': TEST_DOMAIN_ALIAS,
        })
        self.check_error_response(
            resp,
            ['domain_alias.exists'],
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'alias_domain',
            mode='mdapi',
            action='pdd_domain_alias',
            domain=TEST_DOMAIN,
            domain_id=str(TEST_DOMAIN_ID),
            alias=TEST_DOMAIN_ALIAS,
            ip='3.3.3.3',
            user_agent='curl',
            consumer='dev',
        )


@with_settings_hosts
class PddDeleteAliasDomainTestCase(BaseMdapiTestCase):
    url = '/1/bundle/pdd/domain/%s/alias/%s/?consumer=dev' % (
        TEST_DOMAIN_ID,
        TEST_DOMAIN_ALIAS_ID,
    )
    mocked_grants = {
        'domain_alias': ['delete'],
    }

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'unalias_domain',
            mode='mdapi',
            action='pdd_domain_unalias',
            domain=TEST_DOMAIN,
            domain_id=str(TEST_DOMAIN_ID),
            alias=TEST_DOMAIN_ALIAS,
            ip='3.3.3.3',
            user_agent='curl',
            consumer='dev',
        )

    def setUp(self):
        super(PddDeleteAliasDomainTestCase, self).setUp()
        self.setup_statbox_templates()

        self.test_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ID),
                    'options': '{}',
                    'slaves': TEST_DOMAIN_ALIAS,
                    'master_domain': '',
                    'mx': '0',
                    'domain': TEST_DOMAIN,
                    'ena': '1',
                },
            ],
        }
        self.test_alias_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ALIAS_ID),
                    'options': '{}',
                    'slaves': '',
                    'master_domain': TEST_DOMAIN,
                    'mx': '0',
                    'domain': TEST_DOMAIN_ALIAS,
                    'ena': '1',
                },
            ],
        }

        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                self.test_alias_data,
            ],
        )

        alias = Domain().parse(self.test_alias_data)
        self.env.db._serialize_to_eav(alias)

    def test_deletion_ok(self):
        resp = self.make_request(method='DELETE')
        self.check_response_ok(resp)
        self.env.db.check_missing(
            'domains',
            'name',
            master_domain_id=TEST_DOMAIN_ID,
            db='passportdbcentral',
        )

    def test_deletion_alias_not_found(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                dict(hosted_domains=[]),
            ],
        )
        resp = self.make_request(method='DELETE')
        self.check_error_response(
            resp,
            ['domain_alias.not_found'],
        )

    def test_deletion_alias_not_found_on_domain(self):
        self.test_domain_data['hosted_domains'][0]['slaves'] = ''
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            self.test_domain_data,
        )
        resp = self.make_request(method='DELETE')
        self.check_error_response(
            resp,
            ['domain_alias.not_found'],
        )

    def test_deletion_domain_not_found(self):
        # FIXME: Проставленный ранее side_effect имеет в моке больший приоритет
        # нежели устанавливамое здесь значение. Поэтому приходится эмулировать
        # его через ещё side_effect.
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                blackbox_hosted_domains_response(count=0),
            ],
        )

        resp = self.make_request(method='DELETE')
        self.check_error_response(
            resp,
            ['domain.not_found'],
        )


@with_settings_hosts
class PddAliasToMasterTestCase(BaseMdapiTestCase):
    url = '/1/bundle/pdd/domain/%s/alias/%s/make_master/?consumer=dev' % (
        TEST_DOMAIN_ID,
        TEST_DOMAIN_ALIAS_ID,
    )
    method = 'POST'
    mocked_grants = {
        'domain_alias': ['to_master'],
    }

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'pdd_alias_to_master',
            mode='mdapi',
            action='pdd_alias_to_master',
            new_master_domain=TEST_DOMAIN_ALIAS,
            new_alias=TEST_DOMAIN,
            ip='3.3.3.3',
            user_agent='curl',
            consumer='dev',
        )

    def setUp(self):
        super(PddAliasToMasterTestCase, self).setUp()
        self.setup_statbox_templates()

    def setup_domains(self, domain=TEST_DOMAIN, alias=TEST_DOMAIN_ALIAS):
        self.test_domain_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ID),
                    'options': '{}',
                    'slaves': alias,
                    'master_domain': '',
                    'mx': '0',
                    'domain': domain,
                    'ena': '1',
                },
            ],
        }
        self.test_alias_data = {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': str(TEST_ADMIN_UID),
                    'domid': str(TEST_DOMAIN_ALIAS_ID),
                    'options': '{}',
                    'slaves': '',
                    'master_domain': domain,
                    'mx': '0',
                    'domain': alias,
                    'ena': '1',
                },
            ],
        }

        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                self.test_alias_data,
            ],
        )

        master = Domain().parse(self.test_domain_data)
        self.env.db._serialize_to_eav(master)  # алиас сериализуется автоматически

    def test_ok(self):
        self.setup_domains()
        resp = self.make_request()
        self.check_response_ok(resp)
        self.env.db.check(
            'domains',
            'name',
            TEST_DOMAIN_ALIAS,
            domain_id=TEST_DOMAIN_ID,
            db='passportdbcentral',
        )
        self.env.db.check(
            'domains',
            'name',
            TEST_DOMAIN,
            domain_id=TEST_DOMAIN_ALIAS_ID,
            db='passportdbcentral',
        )
        self.env.db.check(
            'domains_events',
            'meta',
            str(TEST_DOMAIN_ALIAS_ID),
            domain_id=TEST_DOMAIN_ID,
            type=8,
            db='passportdbcentral',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('pdd_alias_to_master'),
        ])

    def test_ok_with_cyrillic_domains(self):
        self.setup_domains(
            domain=TEST_CYRILLIC_DOMAIN,
            alias=TEST_CYRILLIC_ALIAS,
        )

        resp = self.make_request()
        self.check_response_ok(resp)
        self.env.db.check(
            'domains',
            'name',
            TEST_CYRILLIC_ALIAS,
            domain_id=TEST_DOMAIN_ID,
            db='passportdbcentral',
        )
        self.env.db.check(
            'domains',
            'name',
            TEST_CYRILLIC_DOMAIN,
            domain_id=TEST_DOMAIN_ALIAS_ID,
            db='passportdbcentral',
        )
        self.env.db.check(
            'domains_events',
            'meta',
            str(TEST_DOMAIN_ALIAS_ID),
            domain_id=TEST_DOMAIN_ID,
            type=8,
            db='passportdbcentral',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'pdd_alias_to_master',
                new_master_domain=TEST_CYRILLIC_ALIAS,
                new_alias=TEST_CYRILLIC_DOMAIN,
            ),
        ])

    def test_alias_not_found(self):
        self.setup_domains()
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                self.test_domain_data,
                dict(hosted_domains=[]),
            ],
        )
        resp = self.make_request()
        self.check_error_response(
            resp,
            ['domain_alias.not_found'],
        )
        self.env.statbox.assert_has_written([])

    def test_alias_not_found_on_domain(self):
        self.setup_domains()
        self.test_domain_data['hosted_domains'][0]['slaves'] = ''
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            self.test_domain_data,
        )
        resp = self.make_request()
        self.check_error_response(
            resp,
            ['domain_alias.not_found'],
        )
        self.env.statbox.assert_has_written([])

    def test_domain_not_found(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'hosted_domains',
            [
                blackbox_hosted_domains_response(count=0),
            ],
        )

        resp = self.make_request()
        self.check_error_response(
            resp,
            ['domain.not_found'],
        )
        self.env.statbox.assert_has_written([])
