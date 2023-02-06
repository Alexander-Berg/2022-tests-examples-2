# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import get_attr_name
from passport.backend.core.models.password import PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_FIRSTNAME1,
    TEST_LASTNAME1,
    TEST_LOGIN1,
    TEST_SCHOLAR_LOGIN1,
    TEST_SCHOLAR_PASSWORD1,
    TEST_UID1,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.string import smart_text


@with_settings_hosts()
class TestChangeScholarPassword(BaseBundleTestViews):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/scholar/change_password/'
    http_method = 'POST'
    http_headers = dict(
        consumer_ip=TEST_CONSUMER_IP1,
        user_agent=TEST_USER_AGENT1,
        user_ip=TEST_USER_IP1,
    )

    def __init__(self, *args, **kwargs):
        super(TestChangeScholarPassword, self).__init__(*args, **kwargs)
        self.password = TEST_SCHOLAR_PASSWORD1
        self.password_hash = self.build_password_hash('pwd')
        self.portal_alias = None
        self.scholar_alias = TEST_SCHOLAR_LOGIN1
        self.uid = TEST_UID1

    @property
    def http_query_args(self):
        return dict(
            password=self.password,
            uid=str(self.uid),
        )

    def setUp(self):
        super(TestChangeScholarPassword, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'account': ['change_scholar_password'],
                    },
                ),
            },
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestChangeScholarPassword, self).tearDown()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            consumer=TEST_CONSUMER1,
            ip=str(TEST_USER_IP1),
            user_agent=str(TEST_USER_AGENT1),
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['base'],
            action='submitted',
            mode='change_scholar_password',
        )
        self.env.statbox.bind_entry(
            'account.scholar_password',
            _inherit_from=[
                'account_modification',
                'base',
            ],
            entity='account.scholar_password',
            operation='updated',
            uid=str(self.uid),
        )
        self.env.statbox.bind_entry(
            'scholar_password_changed',
            _inherit_from=['base'],
            action='scholar_password_changed',
            mode='change_scholar_password',
            uid=str(self.uid),
        )

    def setup_environment(self):
        self.setup_blackbox()
        self.setup_statbox_templates()

    def setup_blackbox(self):
        aliases = dict()
        if self.portal_alias:
            aliases.update(portal=self.portal_alias)
        if self.scholar_alias:
            aliases.update(scholar=self.scholar_alias)

        userinfo = dict(
            aliases=aliases,
            attributes={'account.scholar_password': self.build_password_hash()},
            birthdate=None,
            city=None,
            firstname=TEST_FIRSTNAME1,
            gender=None,
            lastname=TEST_LASTNAME1,
            uid=self.uid,
        )
        userinfo_response = blackbox_userinfo_response(**userinfo)
        self.env.blackbox.set_response_side_effect('userinfo', [userinfo_response])
        self.env.db.serialize(userinfo_response)

        self.env.blackbox.set_response_side_effect(
            'create_pwd_hash',
            [
                blackbox_create_pwd_hash_response(password_hash=self.password_hash),
            ],
        )

    def build_password_hash(self, password_hash='old'):
        return '%s:%s' % (PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON, password_hash)

    def assert_ok_change_scholar_password_db(self, extra_attrs=None):
        expected_attrs = dict()
        if extra_attrs:
            expected_attrs.update(extra_attrs)
        for key in self.scholar_required_attributes:
            if key not in expected_attrs:
                expected_attrs[key] = self.scholar_required_attributes[key]

        attrs = self.env.db.select('attributes', uid=self.uid, db='passportdbshard1')
        attrs = {get_attr_name(a['type']): a['value'] for a in attrs}
        self.assertEqual(attrs, expected_attrs)

    @property
    def scholar_required_attributes(self):
        return {
            'account.scholar_password': self.password_hash,
            'person.firstname': TEST_FIRSTNAME1.encode('utf8'),
            'person.lastname': TEST_LASTNAME1.encode('utf8'),
        }

    def assert_ok_change_shcolar_password_event_log(self):
        e = EventCompositor(uid=str(self.uid))

        e('info.scholar_password', self.password_hash)
        e('action', 'change_scholar_password')
        e('consumer', self.consumer)
        e('user_agent', self.http_headers.get('user_agent'))

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def assert_ok_change_scholar_password_statbox_log(self):
        lines = list()

        def req(name):
            lines.append(self.env.statbox.entry(name))

        req('submitted')
        req('account.scholar_password')
        req('scholar_password_changed')

        self.env.statbox.assert_equals(lines)

    def assert_ok_create_pwd_hash_request(self, request):
        request.assert_post_data_equals(
            dict(
                format='json',
                method='create_pwd_hash',
                password=smart_text(self.password),
                uid=str(self.uid),
                ver='6',
            ),
        )

    def test_ok(self):
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_change_scholar_password_db()
        self.assert_ok_change_shcolar_password_event_log()
        self.assert_ok_change_scholar_password_statbox_log()
        assert len(self.env.blackbox.requests) == 2
        self.assert_ok_create_pwd_hash_request(self.env.blackbox.requests[1])

    def test_strip_password(self):
        self.setup_environment()

        rv = self.make_request(query_args=dict(password=' %s ' % self.password))

        self.assert_ok_response(rv)
        self.assert_ok_change_scholar_password_db()
        self.assert_ok_create_pwd_hash_request(self.env.blackbox.requests[1])

    def test_bad_password(self):
        self.password = 'badpwd'
        self.password_hash = self.build_password_hash()
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(rv, ['password.prohibitedsymbols'])
        self.assert_ok_change_scholar_password_db()

    def test_completed(self):
        self.portal_alias = TEST_LOGIN1
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_change_scholar_password_db()

    def test_no_scholar_alias(self):
        self.portal_alias = TEST_LOGIN1
        self.scholar_alias = None
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_revoke_credentials(self):
        self.setup_environment()

        rv = self.make_request(query_args=dict(revoke_credentials='1'))

        self.assert_ok_response(rv)
        self.assert_ok_change_scholar_password_db(
            extra_attrs={
                'account.global_logout_datetime': TimeNow(),
            },
        )
