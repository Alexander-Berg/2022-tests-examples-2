# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_NON_NATIVE_EMAIL,
    TEST_USER_AGENT,
    TEST_USER_FIRSTNAME,
    TEST_USER_IP,
    TEST_USER_LASTNAME,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.federal_configs_api import FederalConfigsApiNotFoundError
from passport.backend.core.builders.federal_configs_api.faker import federal_config_ok
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


TEST_UID = 1130000000000001
TEST_SSO_DOMAIN_ID = 2997121
TEST_DOMAIN = 'domain.ru'
TEST_LOGIN = 'login123'
TEST_EMAIL = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)
TEST_NAME_ID = '%s/%s' % (TEST_SSO_DOMAIN_ID, TEST_LOGIN)


@with_settings_hosts()
class TestAccountRegisterFederal(BaseBundleTestViews,
                                 StatboxTestMixin):
    default_url = '/1/bundle/account/register/federal/?consumer=dev'
    http_method = 'POST'
    http_headers = {
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['register_federal'],
        }))

        self.http_query_args = {
            'name_id': TEST_LOGIN,
            'domain_id': TEST_SSO_DOMAIN_ID,
            'firstname': TEST_USER_FIRSTNAME,
            'lastname': TEST_USER_LASTNAME,
            'email': TEST_EMAIL,
        }

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domain=TEST_DOMAIN, domid=TEST_SSO_DOMAIN_ID, is_enabled=True),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            json.dumps({'users': [{'id': '', 'uid': {}}]}),
        )
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def check_events(self, display_name=None, is_disabled=False):
        expected = {
            'action': 'account_register_federal',
            'consumer': 'dev',
            'info.login': TEST_EMAIL,
            'info.ena': '0' if is_disabled else '1',
            'info.disabled_status': '1' if is_disabled else '0',
            'info.firstname': TEST_USER_FIRSTNAME,
            'info.lastname': TEST_USER_LASTNAME,
            'info.country': 'ru',
            'info.lang': 'ru',
            'info.tz': 'Europe/Moscow',
            'info.reg_date': DatetimeNow(convert_to_datetime=True),
            'mail.add': '1',
            'sid.add': '2',
            'alias.pdd.add': TEST_NAME_ID,
            'info.mail_status': '1',
            'info.domain_id': str(TEST_SSO_DOMAIN_ID),
            'info.domain_name': TEST_DOMAIN,
            'info.karma': '0',
            'info.karma_prefix': '0',
            'info.karma_full': '0',
            'user_agent': TEST_USER_AGENT,
        }
        if display_name:
            expected['info.display_name'] = display_name
        self.assert_events_are_logged(self.env.handle_mock, expected)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification'],
            _exclude=['mode'],
            ip=TEST_USER_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            old='-',
            operation='created',
            uid=str(TEST_UID),
        )

    def check_statbox_ok(self,
                         federal_alias=TEST_NAME_ID,
                         pdd_alias=TEST_EMAIL,
                         firstname=TEST_USER_FIRSTNAME,
                         lastname=TEST_USER_LASTNAME,
                         display_name=None,
                         is_disabled=False):
        entries = []
        entries.extend([
            self.env.statbox.entry(
                'submitted',
                action='submitted',
                mode='account_register_federal',
                ip=TEST_USER_IP,
                user_agent=TEST_USER_AGENT,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                new='disabled' if is_disabled else 'enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.mail_status',
                new='active',
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='added',
                entity='aliases',
                type='7',
                value=pdd_alias,
                _exclude=['old'],
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='aliases',
                type='24',
                operation='added',
                value=federal_alias,
                _exclude=['old'],
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.firstname',
                new=firstname,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.lastname',
                new=lastname,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.language',
                new='ru',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.country',
                new='ru',
            ),
        ])
        if display_name:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.display_name',
                    new=display_name,
                ),
            ])

        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                entity='person.fullname',
                new='{} {}'.format(firstname, lastname),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='domain_name',
                new=TEST_DOMAIN,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='domain_id',
                new=str(TEST_SSO_DOMAIN_ID),
            ),
            self.env.statbox.entry(
                'account_modification',
                action='account_register_federal',
                entity='karma',
                destination='frodo',
                new='0',
                suid='1',
                registration_datetime=DatetimeNow(convert_to_datetime=True),
                _exclude=['operation'],
                login=TEST_EMAIL,
            ),
            self.env.statbox.entry(
                'account_modification',
                sid='2',
                suid='1',
                entity='subscriptions',
                operation='added',
                _exclude=['old'],
            ),
            self.env.statbox.entry(
                'account_created',
                login=TEST_LOGIN,
                mode='account_register_federal',
                uid=str(TEST_UID),
                ip=TEST_USER_IP,
                _exclude=['track_id', 'suggest_generation_number', 'password_quality', 'karma', 'consumer', 'country', 'is_suggested_login'],
            ),
        ])
        self.env.statbox.assert_has_written(entries)

    def assert_ok_db(self,
                     federal_alias=TEST_NAME_ID,
                     pdd_alias=TEST_NAME_ID,
                     firstname=TEST_USER_FIRSTNAME,
                     lastname=TEST_USER_LASTNAME,
                     display_name=None,
                     is_disabled=False):
        eq_(self.env.db.query_count('passportdbcentral'), 4)
        eq_(self.env.db.query_count('passportdbshard2'), 1)

        self.env.db.check('aliases', 'federal', federal_alias, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('aliases', 'pdd', pdd_alias, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('attributes', 'subscription.mail.status', '1', uid=TEST_UID, db='passportdbshard2')
        self.env.db.check('attributes', 'account.registration_datetime', TimeNow(), uid=TEST_UID, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'account.user_defined_login', uid=TEST_UID, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'karma.value', uid=TEST_UID, db='passportdbshard2')
        self.env.db.check('attributes', 'person.firstname', firstname, uid=TEST_UID, db='passportdbshard2')
        self.env.db.check('attributes', 'person.lastname', lastname, uid=TEST_UID, db='passportdbshard2')
        self.env.db.check_missing('attributes', 'person.gender', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=TEST_UID, db='passportdbshard2')

        if display_name:
            self.env.db.check('attributes', 'account.display_name', display_name, uid=TEST_UID, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'account.display_name', uid=TEST_UID, db='passportdbshard2')

        if is_disabled:
            self.env.db.check('attributes', 'account.is_disabled', '1', uid=TEST_UID, db='passportdbshard2')
        else:
            self.env.db.check_missing('attributes', 'account.is_disabled', uid=TEST_UID, db='passportdbshard2')

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, uid=TEST_UID)

        self.assert_ok_db()
        self.check_statbox_ok()
        self.check_events()

    def test_register_disabled_account_ok(self):
        resp = self.make_request(query_args={'active': False})
        self.assert_ok_response(resp, uid=TEST_UID)

        self.assert_ok_db(is_disabled=True)
        self.check_statbox_ok(is_disabled=True)
        self.check_events(is_disabled=True)

    def test_register_with_displayname_ok(self):
        resp = self.make_request(query_args={'display_name': 'ololo'})
        self.assert_ok_response(resp, uid=TEST_UID)

        self.assert_ok_db(display_name='p:ololo')
        self.check_statbox_ok(display_name='p:ololo')
        self.check_events(display_name='p:ololo')

    def test_invalid_domain_error(self):
        form_data = {
            'name_id': TEST_LOGIN,
            'domain_id': TEST_SSO_DOMAIN_ID + 1,
            'firstname': TEST_USER_FIRSTNAME,
            'lastname': TEST_USER_LASTNAME,
            'email': TEST_EMAIL,
        }
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domid=TEST_SSO_DOMAIN_ID + 1, domain='balagur.com.ua', is_enabled=True),
        )
        self.env.federal_configs_api.set_response_side_effect('config_by_domain_id', FederalConfigsApiNotFoundError())

        resp = self.make_request(query_args=form_data)
        self.assert_error_response(
            resp,
            ['domain.not_found'],
        )

    def test_account_already_exist_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_EMAIL,
                aliases={
                    'pdd': TEST_EMAIL,
                    'federal': TEST_NAME_ID,
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['account.already_registered'],
        )

    def test_mail_occupied_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_EMAIL: 'occupied'}),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['email.exist'],
        )

    def test_mail_on_other_domain_error(self):
        resp = self.make_request(query_args={'email': TEST_NON_NATIVE_EMAIL})
        self.assert_error_response(
            resp,
            ['email.unsupportable_domain'],
        )
