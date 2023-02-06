# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_EMAIL,
    TEST_SUID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_USER_LOGIN_NORMALIZED,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON
from passport.backend.core.test.data import TEST_IMPOSSIBLE_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import merge_dicts


TEST_USER_LOGIN = 'Test-Login'
TEST_AUTORU_ALIAS = 'Alias_1@Auto.Ru'
TEST_AUTORU_ALIAS_NORMALIZED = 'alias_1@auto.ru'
TEST_AUTORU_ALIAS_DB = '1120001/alias_1'


def build_headers():
    return mock_headers(
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
    )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    ALT_DOMAINS={
        'galatasaray.net': 2,
        'auto.ru': 1120001,
    },
)
class TestAccountRegisterIntranet(BaseBundleTestViews, StatboxTestMixin):
    def prepare_testone_address_response(self, address=TEST_EMAIL, native=True):
        response = {
            'users': [
                {
                    'address-list': [
                        {
                            'address': address,
                            'born-date': '2014-12-26 16:11:15',
                            'default': True,
                            'native': native,
                            'prohibit-restore': False,
                            'rpop': False,
                            'silent': False,
                            'unsafe': False,
                            'validated': True,
                        },
                    ],
                    'have_hint': False,
                    'have_password': True,
                    'id': str(TEST_UID),
                    'karma': {
                        'value': 0,
                    },
                    'karma_status': {
                        'value': 0,
                    },
                    'login': TEST_USER_LOGIN,
                    'uid': {
                        'hosted': False,
                        'lite': False,
                        'value': str(TEST_UID),
                    },
                },
            ],
        }
        return json.dumps(response)

    def setUp(self):
        yenv_mock = mock.Mock()
        yenv_mock.name = 'intranet'
        self.yenv_patch = mock.patch('passport.backend.api.app.yenv', yenv_mock)
        self.yenv_patch.start()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['register_intranet']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=None),
                self.prepare_testone_address_response(native=False),
            ],
        )
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        self.yenv_patch.stop()
        del self.env
        del self.track_manager
        del self.yenv_patch

    def account_register_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/account/register/intranet/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'login': TEST_USER_LOGIN,
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='register_intranet',
        )
        super(TestAccountRegisterIntranet, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'intranet_account_created',
            track_id=self.track_id,
            action='account_created',
            login=TEST_USER_LOGIN_NORMALIZED,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'aliases',
            _exclude=['mode', 'track_id'],
            operation='added',
            consumer='dev',
            type='9',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
        )

    def assert_statbox_ok(self, external_email=None, altdomain_alias_domain_id=None,
                          email_created=False):
        entries = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                entity='account.mail_status',
                old='-',
                new='active',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='user_defined_login',
                old='-',
                new=TEST_USER_LOGIN,
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'new'],
                entity='aliases',
                operation='added',
                type=str(ANT['portal']),
                value=TEST_USER_LOGIN_NORMALIZED,
            ),
        ]

        if external_email:
            masked_email = mask_email_for_statbox(external_email).encode('utf-8')
            if email_created:
                now = DatetimeNow(convert_to_datetime=True)
                entries.append(
                    self.env.statbox.entry(
                        'account_modification',
                        bound_at=now,
                        confirmed_at=now,
                        created_at=now,
                        email_id='1',
                        entity='account.emails',
                        new=masked_email.decode('utf-8'),
                        uid=str(TEST_UID),
                        is_unsafe='0',
                        operation='added',
                        is_suitable_for_restore='1',
                    ),
                )

        for entity, new in [
            ('person.language', 'ru'),
            ('person.country', 'ru'),
        ]:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    new=new,
                ),
            )
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'new'],
                entity='password.encrypted',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.encoding_version',
                new=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.quality',
                new='0',
            ),
        ])
        entries.append(self.env.statbox.entry('account_register'))
        entries.extend([
            self.env.statbox.entry(
                'subscriptions',
                sid='8',
            ),
            self.env.statbox.entry(
                'subscriptions',
                sid='2',
                suid=str(TEST_SUID),
            ),
        ])
        if altdomain_alias_domain_id:
            entries.append(
                self.env.statbox.entry(
                    'aliases',
                    domain_id=altdomain_alias_domain_id,
                ),
            )

        entries.append(self.env.statbox.entry('intranet_account_created'))
        self.env.statbox.assert_has_written(entries)

    def check_ok(self, rv, is_maillist=False, external_email=None,
                 altdomain_alias=None, central_query_count=4,
                 sharddb_query_count=1, email_created=False,
                 firstname_global=None, lastname_global=None):
        timenow = TimeNow()

        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'uid': 1,
            },
        )

        if email_created:
            central_query_count += 1
            sharddb_query_count += 2

        eq_(self.env.db.query_count('passportdbcentral'), central_query_count)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_query_count)

        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=1, db='passportdbshard1')

        if is_maillist:
            self.env.db.check_missing('attributes', 'account.is_employee', uid=1, db='passportdbshard1')
            self.env.db.check('attributes', 'account.is_maillist', '1', uid=1, db='passportdbshard1')
        else:
            self.env.db.check('attributes', 'account.is_employee', '1', uid=1, db='passportdbshard1')
            self.env.db.check_missing('attributes', 'account.is_maillist', uid=1, db='passportdbshard1')

        if external_email:
            self.env.db.check(
                'attributes',
                'account.default_email',
                external_email.encode('utf-8'),
                uid=1,
                db='passportdbshard1',
            )
        else:
            self.env.db.check_missing('attributes', 'account.default_email', uid=1, db='passportdbshard1')

        if altdomain_alias:
            self.env.db.check('aliases', 'altdomain', altdomain_alias, uid=1, db='passportdbcentral')
        else:
            self.env.db.check_missing('aliases', 'altdomain', uid=1, db='passportdbcentral')

        if firstname_global:
            self.env.db.check('attributes', 'person.firstname_global', firstname_global, uid=1, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'person.firstname_global', uid=1, db='passportdbshard1')
        if lastname_global:
            self.env.db.check('attributes', 'person.lastname_global', lastname_global, uid=1, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'person.lastname_global', uid=1, db='passportdbshard1')

        for missing_attr_name in (
            'subscription.mail.login_rule',
            'account.display_name',
            'person.gender',
            'person.birthday',
            'person.country',
            'person.city',
            'person.language',
            'person.timezone',
        ):
            self.env.db.check_missing('attributes', missing_attr_name, uid=1, db='passportdbshard1')

        # Почтовый логин совпадает с portal => не создается aliases.mail
        self.env.db.check_missing('aliases', 'mail', uid=1, db='passportdbcentral')

        self.env.db.check('attributes', 'password.encrypted', TEST_IMPOSSIBLE_PASSWORD, uid=1, db='passportdbshard1')

        expected_events = [
            {'name': 'info.login', 'value': TEST_USER_LOGIN_NORMALIZED},
            {'name': 'info.login_wanted', 'value': TEST_USER_LOGIN},
            {'name': 'info.ena', 'value': '1'},
            {'name': 'info.disabled_status', 'value': '0'},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
            {'name': 'info.is_maillist', 'value': '1'} if is_maillist else {'name': 'info.is_employee', 'value': '1'},
        ]
        if external_email:
            expected_events.append({'name': 'info.default_email', 'value': external_email.encode('utf-8')})
        expected_events.extend([
            {'name': 'info.mail_status', 'value': '1'},
            {'name': 'info.country', 'value': 'ru'},
            {'name': 'info.tz', 'value': 'Europe/Moscow'},
            {'name': 'info.lang', 'value': 'ru'},
        ])
        if firstname_global:
            expected_events.append({'name': 'info.firstname_global', 'value': firstname_global})
        if lastname_global:
            expected_events.append({'name': 'info.lastname_global', 'value': lastname_global})
        expected_events.extend([
            {'name': 'info.password', 'value': TEST_IMPOSSIBLE_PASSWORD},
            {'name': 'info.password_quality', 'value': '0'},
            {'name': 'info.password_update_time', 'value': timenow},
            {'name': 'info.karma_prefix', 'value': '0'},
            {'name': 'info.karma_full', 'value': '0'},
            {'name': 'info.karma', 'value': '0'},
            {'name': 'alias.portal.add', 'value': TEST_USER_LOGIN_NORMALIZED},
        ])
        if altdomain_alias:
            expected_events.append({'name': 'alias.altdomain.add', 'value': altdomain_alias})
        expected_events.extend([
            {'name': 'mail.add', 'value': '1'},
            {'name': 'sid.add', 'value': '8|%s,2' % TEST_USER_LOGIN},
        ])

        if email_created:
            expected_events.extend([
                {'name': 'email.1', 'value': 'created'},
                {'name': 'email.1.address', 'value': external_email.encode('utf-8')},
                {'name': 'email.1.confirmed_at', 'value': timenow},
                {'name': 'email.1.created_at', 'value': timenow},
                {'name': 'email.1.bound_at', 'value': timenow},
                {'name': 'email.1.is_unsafe', 'value': '0'},
            ])
        expected_events.extend([
            {'name': 'action', 'value': 'account_register'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
        ])

        self.assert_events_are_logged_with_order(self.env.handle_mock, expected_events)
        self.assert_statbox_ok(
            external_email=external_email,
            altdomain_alias_domain_id=altdomain_alias.split('/')[0] if altdomain_alias else None,
            email_created=email_created,
        )

    def test_successful_register(self):
        rv = self.account_register_request(
            self.query_params(),
            build_headers(),
        )
        self.check_ok(rv, is_maillist=False)

    def test_register_with_external_email(self):
        rv = self.account_register_request(
            self.query_params(external_email=u'admin@yandex.ru'),
            build_headers(),
        )
        self.check_ok(
            rv,
            external_email=u'admin@yandex.ru',
            email_created=True,
        )

    def test_register_with_external_email_on_cyrillic_domain(self):
        rv = self.account_register_request(
            self.query_params(external_email=u'admin@яндекс.рф'),
            build_headers(),
        )
        self.check_ok(
            rv,
            external_email=u'admin@яндекс.рф',
            email_created=True,
        )

    def test_register_as_maillist(self):
        rv = self.account_register_request(
            self.query_params(is_maillist='1', external_email=u'admin@яндекс.рф'),
            build_headers(),
        )
        self.check_ok(
            rv,
            is_maillist=True,
            external_email=u'admin@яндекс.рф',
            email_created=True,
        )

    def test_register_with_global_names(self):
        firstname_global = 'first name'
        lastname_global = 'last name'
        rv = self.account_register_request(
            self.query_params(
                firstname_global=firstname_global,
                lastname_global=lastname_global,
            ),
            build_headers(),
        )
        self.check_ok(
            rv,
            firstname_global=firstname_global,
            lastname_global=lastname_global,
        )

    def test_without_required_headers_error(self):
        rv = self.account_register_request(
            self.query_params(),
            {},
        )
        self.assert_error_response(rv, ['ip.empty'])

    def test_register_with_autoru_alias_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_USER_LOGIN: 'free',
                TEST_AUTORU_ALIAS_NORMALIZED: 'free',
            }),
        )
        rv = self.account_register_request(
            self.query_params(altdomain_alias=TEST_AUTORU_ALIAS),
            build_headers(),
        )
        self.check_ok(
            rv,
            is_maillist=False,
            altdomain_alias=TEST_AUTORU_ALIAS_DB,
        )

    def test_register_with_occupied_autoru_alias_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_USER_LOGIN: 'free',
                TEST_AUTORU_ALIAS_NORMALIZED: 'occupied',
            }),
        )
        rv = self.account_register_request(
            self.query_params(altdomain_alias=TEST_AUTORU_ALIAS),
            build_headers(),
        )
        self.assert_error_response(rv, ['altdomain_alias.notavailable'])
