# -*- coding: utf-8 -*-

import mock
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_loginoccupation_response,
)
from passport.backend.core.eav_type_mapping import get_attr_name
from passport.backend.core.geobase.faker.fake_geobase import FakeRegion
from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_FIRSTNAME1,
    TEST_LASTNAME1,
    TEST_SCHOLAR_LOGIN1,
    TEST_SCHOLAR_PASSWORD1,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.string import (
    smart_bytes,
    smart_text,
)


@with_settings_hosts()
class TestAccountRegisterScholar(BaseBundleTestViews):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/scholar/register/'
    http_headers = dict(
        consumer_ip=TEST_CONSUMER_IP1,
        user_agent=TEST_USER_AGENT1,
        user_ip=TEST_USER_IP1,
    )
    http_method = 'POST'
    http_query_args = dict(
        firstname=TEST_FIRSTNAME1,
        lastname=TEST_LASTNAME1,
        login=TEST_SCHOLAR_LOGIN1,
        password=TEST_SCHOLAR_PASSWORD1,
    )

    def __init__(self, *args, **kwargs):
        super(TestAccountRegisterScholar, self).__init__(*args, **kwargs)

        self.is_login_busy = False
        self.scholar_password_hash = '%s:pwd' % PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON
        self.scholar_uid = 1

    def setUp(self):
        super(TestAccountRegisterScholar, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer=TEST_CONSUMER1,
                grants=dict(account=['register_scholar']),
                networks=[TEST_CONSUMER_IP1],
            ),
        )
        self.setup_statbox_templates()

        self.fake_region = FakeRegion()
        self.fake_region.set_region_for_ip(TEST_USER_IP1, dict())

        self.__patches = [
            self.env,
            self.fake_region,
        ]

        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestAccountRegisterScholar, self).tearDown()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            ip=str(TEST_USER_IP1),
            user_agent=str(TEST_USER_AGENT1),
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=[
                'account_modification',
                'base',
            ],
            consumer=TEST_CONSUMER1,
            uid=str(self.scholar_uid),
        ),
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['base'],
            action='submitted',
            mode='account_register_scholar',
        )
        self.env.statbox.bind_entry(
            'aliases.scholar',
            _inherit_from=['account_modification'],
            entity='aliases',
            operation='added',
            type=str(EavSerializer.alias_name_to_type('scholar')),
            value=smart_text(TEST_SCHOLAR_LOGIN1),
        )

        attrs = {
            'account.disabled_status': 'enabled',
            'account.scholar_password': None,
            'person.country': mock.ANY,
            'person.firstname': TEST_FIRSTNAME1,
            'person.fullname': '%s %s' % (TEST_FIRSTNAME1, TEST_LASTNAME1),
            'person.language': mock.ANY,
            'person.lastname': TEST_LASTNAME1,
        }
        for attr_name, attr_value in attrs.items():
            bits = dict()
            if attr_value is not None:
                bits.update(new=attr_value, old='-')
            self.env.statbox.bind_entry(
                attr_name,
                _inherit_from=['account_modification'],
                entity=attr_name,
                operation='created',
                **bits
            )

        self.env.statbox.bind_entry(
            'frodo_karma',
            _inherit_from=['frodo_karma', 'base'],
            action='account_register_scholar',
            login=smart_text(TEST_SCHOLAR_LOGIN1),
            registration_datetime=DatetimeNow(convert_to_datetime=True),
            consumer=TEST_CONSUMER1,
            uid=str(self.scholar_uid),
        )
        self.env.statbox.bind_entry(
            'subscription.passport',
            _inherit_from=['account_modification', 'base'],
            entity='subscriptions',
            operation='added',
            sid=str(Service.by_slug('passport').sid),
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from=['base'],
            action='account_created',
            login=smart_text(TEST_SCHOLAR_LOGIN1),
            mode='account_register_scholar',
            uid=str(self.scholar_uid),
        )

    def setup_environment(self):
        self.setup_blackbox()

    def setup_blackbox(self):
        login_occupation_status = 'occupied' if self.is_login_busy else 'free'
        self.env.blackbox.set_response_side_effect(
            'loginoccupation',
            [
                blackbox_loginoccupation_response({TEST_SCHOLAR_LOGIN1: login_occupation_status}),
            ],
        )

        self.env.blackbox.set_response_side_effect(
            'create_pwd_hash',
            [
                blackbox_create_pwd_hash_response(password_hash=self.scholar_password_hash),
            ],
        )

    def build_ok_register_scholar_response(self):
        return dict(
            firstname=TEST_FIRSTNAME1,
            lastname=TEST_LASTNAME1,
            login=smart_text(TEST_SCHOLAR_LOGIN1),
            uid=self.scholar_uid,
        )

    def assert_ok_register_scholar_db(
        self,
        extra_attrs=None,
    ):
        """
        Входные параметры

            extra_attrs

                Словарь (имя атрибута, значение) с атрибутами, которые должны
                быть у школьника, помимо обязательных.
        """
        self.env.db.check(
            'aliases',
            'scholar',
            smart_bytes(TEST_SCHOLAR_LOGIN1),
            db='passportdbcentral',
            uid=self.scholar_uid,
        )

        aliases = self.env.db.select('aliases', uid=self.scholar_uid, db='passportdbcentral')
        self.assertEqual(len(aliases), 1)

        expected_attrs = dict()
        if extra_attrs:
            expected_attrs.update(extra_attrs)
        for key in self.scholar_required_attributes:
            if key not in expected_attrs:
                expected_attrs[key] = self.scholar_required_attributes[key]

        attrs = self.env.db.select('attributes', uid=self.scholar_uid, db='passportdbshard1')
        attrs = {get_attr_name(a['type']): a['value'] for a in attrs}
        self.assertEqual(attrs, expected_attrs)

        assert not self.env.db.select('extended_attributes', uid=self.scholar_uid, db='passportdbshard1')

    @property
    def scholar_required_attributes(self):
        return {
            'account.registration_datetime': TimeNow(),
            'account.scholar_password': self.scholar_password_hash,
            'person.firstname': TEST_FIRSTNAME1.encode('utf8'),
            'person.lastname': TEST_LASTNAME1.encode('utf8'),
        }

    def assert_ok_create_kiddish_event_log(self, extra_events=None):
        expected = extra_events or dict()
        required_events = {'info.login': TEST_SCHOLAR_LOGIN1}
        for name in required_events:
            if name not in expected:
                expected[name] = required_events[name]

        e = EventCompositor(uid=str(self.scholar_uid))

        e('info.login', smart_bytes(expected['info.login']))
        e('info.ena', '1')
        e('info.disabled_status', '0')
        e('info.reg_date', DatetimeNow(convert_to_datetime=True))
        e('info.firstname', smart_bytes(TEST_FIRSTNAME1))
        e('info.lastname', smart_bytes(TEST_LASTNAME1))
        e('info.country', mock.ANY)
        e('info.lang', mock.ANY)
        e('info.karma_prefix', '0')
        e('info.karma_full', '0')
        e('info.karma', '0')
        e('alias.scholar.add', smart_bytes(expected['info.login']))
        e('sid.add', smart_bytes('8|' + expected['info.login']))
        e('info.scholar_password', self.scholar_password_hash)
        e('action', 'account_register_scholar')
        e('consumer', TEST_CONSUMER1)
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def assert_ok_create_kiddish_statbox_log(self):
        lines = list()

        def req(name):
            lines.append(self.env.statbox.entry(name))

        req('submitted')
        req('account.disabled_status')
        req('aliases.scholar')
        req('account.scholar_password')
        req('person.firstname')
        req('person.lastname')
        req('person.language')
        req('person.country')
        req('person.fullname')
        req('frodo_karma')
        req('subscription.passport')
        req('account_created')

        self.env.statbox.assert_equals(lines)

    def assert_ok_loginoccupation_request(self, request):
        request.assert_query_equals(
            dict(
                format='json',
                ignore_stoplist='1',
                logins=smart_text(TEST_SCHOLAR_LOGIN1),
                method='loginoccupation',
            ),
        )

    def assert_ok_create_pwd_hash_request(self, request):
        request.assert_post_data_equals(
            dict(
                format='json',
                method='create_pwd_hash',
                password=smart_text(TEST_SCHOLAR_PASSWORD1),
                uid=str(self.scholar_uid),
                ver='6',
            ),
        )

    def test_ok(self):
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_ok_register_scholar_response())
        self.assert_ok_register_scholar_db()
        self.assert_ok_create_kiddish_event_log()
        self.assert_ok_create_kiddish_statbox_log()

        assert len(self.env.blackbox.requests) == 2
        self.assert_ok_loginoccupation_request(self.env.blackbox.requests[0])
        self.assert_ok_create_pwd_hash_request(self.env.blackbox.requests[1])

    def test_login_busy(self):
        self.is_login_busy = True
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(rv, ['login.notavailable'])

    def test_login_prohibitedsymbols(self):
        self.setup_environment()

        rv = self.make_request(query_args=dict(login='portal'))

        self.assert_error_response(rv, ['login.prohibitedsymbols'])

    def test_password_prohibitedsymbols(self):
        self.setup_environment()

        rv = self.make_request(query_args=dict(password='password'))

        self.assert_error_response(rv, ['password.prohibitedsymbols'])

    required_args = [
        'firstname',
        'lastname',
        'login',
        'password',
    ]

    @parameterized.expand([(n,) for n in required_args])
    def test_empty_required_arg(self, name):
        self.setup_environment()

        rv = self.make_request(query_args={name: ''})

        self.assert_error_response(rv, ['%s.empty' % name])

    @parameterized.expand([(n,) for n in required_args])
    def test_no_required_arg(self, name):
        self.setup_environment()

        rv = self.make_request(exclude_args=[name])

        self.assert_error_response(rv, ['%s.empty' % name])
