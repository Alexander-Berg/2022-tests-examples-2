# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_CITY,
    TEST_COUNTRY_CODE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_FIRSTNAME,
    TEST_GENDER,
    TEST_HINT_ANSWER,
    TEST_HINT_QUESTION,
    TEST_HOST,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_NEOPHONISH_LOGIN1,
    TEST_PASSWORD_HASH,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PHONISH_LOGIN1,
    TEST_TZ,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.avatars_mds_api import AvatarsMdsApiTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import (
    clean_web_api_simple_response_user_data,
)
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING
from passport.backend.core.models.account import Account
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import deep_merge
from passport.backend.utils.string import (
    smart_str,
    smart_text,
)
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)


TEST_DISPLAY_NAME_PASSPORT_PREFIX = 'p'
TEST_OLD_AVATAR_KEY = 'oldavakey/asd'


@with_settings_hosts(
    AVATARS_WRITE_URL='http://localhost-write/',
    AVATARS_READ_URL='http://localhost-read/',
    AVATARS_TIMEOUT=1,
    AVATARS_RETRIES=2,
    AVATARS_YAPIC_NAMESPACE='yapic',
)
class TestResetAvatar(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/account/reset/avatar/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        uid=TEST_UID,
        avatar_key=TEST_OLD_AVATAR_KEY,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['reset_avatar'],
        }))

        self.setup_statbox_templates()
        self.env.avatars_mds_api.set_response_value('delete', 'ok')

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='avatar_reset',
            ip=TEST_USER_IP,
            uid=str(TEST_UID),
            consumer='dev',
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from='local_base',
            _exclude=['mode'],
            event='account_modification',
        )
        self.env.statbox.bind_entry(
            'avatar_reset',
            _inherit_from='local_base',
            action='avatar_reset',
        )

    def set_blackbox_response(self, default_avatar_key=TEST_OLD_AVATAR_KEY,
                              **kwargs):
        kwargs.update(
            uid=TEST_UID,
            default_avatar_key=default_avatar_key,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        userinfo_response = blackbox_userinfo_response(**kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.db.serialize(userinfo_response)

    def check_emails_sent(self, language='ru', tld='ru'):
        def build_email(address):
            return {
                'language': language,
                'addresses': [address],
                'subject': 'change.avatar.notify.subject',
                'tanker_keys': {
                    'greeting.noname': {},
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.{}/\'>'.format(tld),
                        'FEEDBACK_URL_END': '</a>',
                    },
                    'change.avatar.notify': {},
                },
            }

        self.assert_emails_sent([
            build_email(address='%s@%s' % (TEST_LOGIN, 'gmail.com')),
            build_email(address='%s@%s' % (TEST_LOGIN, 'yandex.ru')),
        ])

    def test_ok(self):
        self.set_blackbox_response(
            default_avatar_key=TEST_OLD_AVATAR_KEY,
        )

        response = self.make_request()
        self.assert_ok_response(response)

        shard = 'passportdbshard1'
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count(shard), 1)
        self.env.db.check_missing('attributes', 'avatar.default', uid=TEST_UID, db=shard)

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'action': 'delete_default_avatar',
                'info.default_avatar': '-',
                'consumer': 'dev',
                'user_agent': TEST_USER_AGENT,
            },
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                old=TEST_OLD_AVATAR_KEY,
                new='-',
                operation='deleted',
            ),
            self.env.statbox.entry('avatar_reset'),
        ])
        eq_(len(self.env.avatars_mds_api.requests), 1)
        self.check_emails_sent()

    def test_disabled_ok(self):
        self.set_blackbox_response(
            default_avatar_key=TEST_OLD_AVATAR_KEY,
            enabled=False,
        )

        response = self.make_request()
        self.assert_ok_response(response)
        eq_(len(self.env.avatars_mds_api.requests), 1)
        self.check_emails_sent()

    def test_other_language_ok(self):
        self.set_blackbox_response(language='en')
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_emails_sent(language='en', tld='com')
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_mds_error(self):
        self.set_blackbox_response(
            default_avatar_key=TEST_OLD_AVATAR_KEY,
        )
        self.env.avatars_mds_api.set_response_side_effect('delete', AvatarsMdsApiTemporaryError())

        response = self.make_request()
        self.assert_error_response(response, ['backend.avatars_mds_api_failed'])

    def test_no_default(self):
        self.set_blackbox_response(
            default_avatar_key=None,
        )
        response = self.make_request()
        self.assert_ok_response(response)
        eq_(len(self.env.avatars_mds_api.requests), 0)

    def test_wrong_avatar_key(self):
        self.set_blackbox_response(
            default_avatar_key='someotheravatarkey/qwe',
        )
        response = self.make_request()
        self.assert_ok_response(response)
        eq_(len(self.env.avatars_mds_api.requests), 0)

    def test_grant_missing_error(self):
        self.env.grants.set_grant_list([])
        resp = self.make_request()
        self.assert_error_response(resp, ['access.denied'], status_code=403)


@with_settings_hosts(
    CLEAN_WEB_API_ENABLED=True,
    CLEAN_WEB_API_URL='http://localhost/',
    CLEAN_WEB_API_TIMEOUT=1,
    CLEAN_WEB_API_RETRIES=2,
)
class TestResetDisplayName(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/account/reset/display_name/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        uid=TEST_UID,
        public_name=TEST_DISPLAY_NAME,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['reset_display_name']}))
        self.initial_data = {
            'uid': TEST_UID,
            'login': TEST_LOGIN,
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            'birthdate': '1970-01-01',
            'gender': TEST_GENDER,
            'language': TEST_LANGUAGE,
            'country': TEST_COUNTRY_CODE,
            'city': TEST_CITY,
            'timezone': TEST_TZ,
            'display_name': TEST_DISPLAY_NAME_DATA,
            'emails': [
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        }
        self.setup_statbox_templates()
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response_user_data(True))

    def set_db_fields_and_bb_response(self, **kwargs):
        if 'display_name' in kwargs:
            kwargs['display_name'] = {
                u'default_avatar': u'',
                u'name': kwargs['display_name'],
            }
        blackbox_response = blackbox_userinfo_response(**dict(self.initial_data, **kwargs))
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.account = Account().parse(get_parsed_blackbox_response('userinfo', blackbox_response))
        self.env.db._serialize_to_eav(self.account)

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='display_name_reset',
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode'],
            event='account_modification',
            operation='updated',
        )
        self.env.statbox.bind_entry(
            'display_name_reset',
            _inherit_from='local_base',
            action='display_name_reset',
        )

    def check_statbox_entries(self, display_name_prefix=TEST_DISPLAY_NAME_PASSPORT_PREFIX,
                              display_name=TEST_DISPLAY_NAME):
        expected_entries = []
        new_display_name = smart_text(display_name_prefix + ':' + display_name)
        old_display_name = smart_text(self.account.person.display_name)
        if old_display_name != new_display_name:
            expected_entries.append(
                self.env.statbox.entry(
                    'local_account_modification',
                    entity='person.display_name',
                    old=old_display_name,
                    new=new_display_name,
                ),
            )
        expected_entries.append(
            self.env.statbox.entry('display_name_reset')
        )
        self.env.statbox.assert_has_written(expected_entries)

    def check_db_entries(self, display_name_prefix=TEST_DISPLAY_NAME_PASSPORT_PREFIX,
                         display_name=TEST_DISPLAY_NAME, lastname=TEST_LASTNAME, query_count=1):
        for predicate, attribute_name, value in (
            (True, 'person.firstname', TEST_FIRSTNAME),
            (lastname, 'person.lastname', lastname),
            (display_name, 'account.display_name', smart_str(u'%s:%s' % (display_name_prefix, display_name))),
        ):
            if predicate:
                self.env.db.check_db_attr(
                    TEST_UID,
                    attribute_name,
                    value,
                )
            else:
                self.env.db.check_db_attr_missing(
                    TEST_UID,
                    attribute_name,
                )
        for db_name, expected_count in (
            ('passportdbcentral', 0),
            ('passportdbshard1', query_count),
            ('passportdbshard2', 0),
        ):
            actual_count = self.env.db.query_count(db_name)
            eq_(
                actual_count,
                expected_count,
                'Expected %d queries into "%s", found %d.' % (
                    expected_count, db_name, actual_count,
                ),
            )
        self.env.db.check_db_attr_missing(
            TEST_UID,
            'person.dont_use_displayname_as_public_name',
        )

    def check_historydb_entries(self, display_name_prefix=TEST_DISPLAY_NAME_PASSPORT_PREFIX, display_name=TEST_DISPLAY_NAME):
        base_entries = {
            'consumer': 'dev',
            'action': 'reset_display_name',
            'info.display_name': smart_str(u'%s:%s' % (display_name_prefix, display_name)),
            'user_agent': 'curl',
        }
        expected_entries = {
            k: v
            for k, v in base_entries.items()
            if v is not None
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

    def check_emails_sent(self, new_display_name, language='ru', tld='ru'):
        def build_email(address):
            return {
                'language': language,
                'addresses': [address],
                'subject': 'change.displayname.notify.subject',
                'tanker_keys': {
                    'greeting.noname': {},
                    'feedback': {
                        'FEEDBACK_URL_BEGIN': '<a href=\'https://feedback2.yandex.{}/\'>'.format(tld),
                        'FEEDBACK_URL_END': '</a>',
                    },
                    'change.displayname.notify': {
                        'last_displayname': self.account.person.display_name.public_name,
                        'new_username': new_display_name,
                    },
                },
            }

        self.assert_emails_sent([
            build_email(address='%s@%s' % (TEST_LOGIN, 'gmail.com')),
            build_email(address='%s@%s' % (TEST_LOGIN, 'yandex.ru')),
        ])

    def test_ok(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries(display_name=u'Пользователь M.')
        self.check_historydb_entries(display_name=u'Пользователь M.')
        self.check_statbox_entries(display_name=u'Пользователь M.')
        self.check_emails_sent(new_display_name=u'Пользователь M.')
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_full_name_for_user_w_display_name(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                'full_name': u'{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME),
            },
            exclude_args=['public_name']
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])
        self.env.email_toolkit.assert_no_emails_sent()
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_full_name_for_user_wo_display_name_ok(self):
        self.set_db_fields_and_bb_response(
            display_name=None,
            public_name=u'{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME),
            is_display_name_empty=True,
        )
        resp = self.make_request(
            query_args={
                'full_name': u'{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME),
            },
            exclude_args=['public_name']
        )
        self.assert_ok_response(resp)
        self.check_db_entries(display_name=u'Пользователь M.')
        self.check_historydb_entries(display_name=u'Пользователь M.')
        self.check_statbox_entries(display_name=u'Пользователь M.')
        self.check_emails_sent(new_display_name=u'Пользователь M.')
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_full_name_swap_first_and_last_name_in_query_ok(self):
        self.set_db_fields_and_bb_response(
            display_name=None,
            public_name=u'{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME),
            is_display_name_empty=True,
        )
        resp = self.make_request(
            query_args={
                'full_name': u'{} {}'.format(TEST_LASTNAME, TEST_FIRSTNAME),
            },
            exclude_args=['public_name']
        )
        self.assert_ok_response(resp)
        self.check_db_entries(display_name=u'Пользователь M.')
        self.check_historydb_entries(display_name=u'Пользователь M.')
        self.check_statbox_entries(display_name=u'Пользователь M.')
        self.check_emails_sent(new_display_name=u'Пользователь M.')
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_full_name_for_user_wo_display_name_request_cleanweb(self):
        self.set_db_fields_and_bb_response(
            display_name=None,
            public_name=u'Elon M.',
            is_display_name_empty=True,
        )
        resp = self.make_request(
            query_args={
                'full_name': u'{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME),
            },
            exclude_args=['public_name']
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(display_name=None, query_count=0)
        self.env.email_toolkit.assert_no_emails_sent()
        eq_(len(self.env.clean_web_api.requests), 1)
        self.env.clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=(
                dict(
                    jsonrpc='2.0',
                    method='process',
                    id=1234,
                    params={
                        'type': 'user_data',
                        'service': 'passport',
                        'body': dict(
                            display_name='Elon M.',
                            auto_only=False,
                            verdict_data='{"uid": 1, "value": "Elon M."}',
                        ),
                        'puid': str(TEST_UID),
                        'key': 'public_name_cl_check_{}'.format(TEST_UID),
                    },
                )
            )
        )

    def test_full_name_for_user_wo_display_name_request_cleanweb_bad_autoverdict(self):
        self.env.clean_web_api.set_response_value('', clean_web_api_simple_response_user_data(['text_auto_obscene']))
        self.set_db_fields_and_bb_response(
            display_name=None,
            public_name=u'Elon M.',
            is_display_name_empty=True,
        )
        resp = self.make_request(
            query_args={
                'full_name': u'{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME),
            },
            exclude_args=['public_name']
        )
        self.assert_ok_response(resp)
        self.check_db_entries(display_name=u'Пользователь M.')
        self.check_historydb_entries(display_name=u'Пользователь M.')
        self.check_statbox_entries(display_name=u'Пользователь M.')
        self.check_emails_sent(new_display_name=u'Пользователь M.')
        eq_(len(self.env.clean_web_api.requests), 1)
        self.env.clean_web_api.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/',
            headers={'Content-Type': 'application/json'},
            json_data=(
                dict(
                    jsonrpc='2.0',
                    method='process',
                    id=1234,
                    params={
                        'type': 'user_data',
                        'service': 'passport',
                        'body': dict(
                            display_name='Elon M.',
                            auto_only=False,
                            verdict_data='{"uid": 1, "value": "Elon M."}',
                        ),
                        'puid': str(TEST_UID),
                        'key': 'public_name_cl_check_{}'.format(TEST_UID),
                    },
                )
            )
        )

    def test_wrong_display_name(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                'public_name': 'WTF',
            },
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])
        self.env.email_toolkit.assert_no_emails_sent()
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_wrong_full_name(self):
        self.set_db_fields_and_bb_response(display_name=None, public_name='Elon M.', is_display_name_empty=True)
        resp = self.make_request(
            query_args={
                'full_name': 'WTF',
            },
            exclude_args=['public_name']
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(display_name=None, query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])
        self.env.email_toolkit.assert_no_emails_sent()
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_no_lastname_ok(self):
        self.set_db_fields_and_bb_response(lastname=None)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries(display_name=u'Пользователь', lastname=None)
        self.check_historydb_entries(display_name=u'Пользователь')
        self.check_statbox_entries(display_name=u'Пользователь')
        self.check_emails_sent(new_display_name=u'Пользователь')
        eq_(len(self.env.clean_web_api.requests), 0)

    def test_other_language_ok(self):
        self.set_db_fields_and_bb_response(language='en')
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries(display_name='User M.')
        self.check_historydb_entries(display_name='User M.')
        self.check_statbox_entries(display_name='User M.')
        self.check_emails_sent(new_display_name='User M.', language='en', tld='com')
        eq_(len(self.env.clean_web_api.requests), 0)


@with_settings_hosts()
class TestResetQuestion(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/account/reset/question/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        uid=TEST_UID,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['reset_question']}))
        self.initial_data = {
            'uid': TEST_UID,
            'login': TEST_LOGIN,
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            'dbfields': {
                'userinfo_safe.hinta.uid': TEST_HINT_ANSWER,
                'userinfo_safe.hintq.uid': TEST_HINT_QUESTION,
            },
        }
        self.setup_statbox_templates()

    def set_db_fields_and_bb_response(self, **kwargs):
        blackbox_response = blackbox_userinfo_response(**dict(self.initial_data, **kwargs))
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.account = Account().parse(get_parsed_blackbox_response('userinfo', blackbox_response))
        self.env.db._serialize_to_eav(self.account)

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='question_reset',
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'question_reset',
            _inherit_from='local_base',
            action='question_reset',
        )

    def check_statbox_entries(self):
        self.env.statbox.assert_has_written([self.env.statbox.entry('question_reset')])

    def check_db_entries(self, query_count=1):
        for db_name, expected_count in (
            ('passportdbcentral', 0),
            ('passportdbshard1', query_count),
            ('passportdbshard2', 0),
        ):
            actual_count = self.env.db.query_count(db_name)
            eq_(
                actual_count,
                expected_count,
                'Expected %d queries into "%s", found %d.' % (
                    expected_count, db_name, actual_count,
                ),
            )

    def check_historydb_entries(self):
        base_entries = {
            'consumer': 'dev',
            'action': 'reset_question',
            'user_agent': 'curl',
            'info.hinta': '-',
            'info.hintq': '-',
        }
        expected_entries = {
            k: v
            for k, v in base_entries.items()
            if v is not None
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

    def test_ok(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries()
        self.check_statbox_entries()

    def test_no_hint_error(self):
        self.set_db_fields_and_bb_response(dbfields={})
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])


@with_settings_hosts()
class TestResetEmail(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/account/reset/email/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        uid=TEST_UID,
        email=TEST_LOGIN + '@gmail.com',
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['reset_email']}))
        self.initial_data = {
            'uid': TEST_UID,
            'login': TEST_LOGIN,
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            'emails': [
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            'email_attributes': [
                {
                    'id': 1,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_LOGIN + '@gmail.com',
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                        EMAIL_NAME_MAPPING['confirmed']: '2',
                    },
                },
                {
                    'id': 2,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_LOGIN + '@mail.ru',
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                        EMAIL_NAME_MAPPING['confirmed']: '2',
                    },
                },
                {
                    'id': 3,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_LOGIN + '@silent.ru',
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                        EMAIL_NAME_MAPPING['confirmed']: '2',
                    },
                },
            ],
        }
        self.setup_statbox_templates()

    def set_db_fields_and_bb_response(self, **kwargs):
        blackbox_response = blackbox_userinfo_response(**dict(self.initial_data, **kwargs))
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.account = Account().parse(get_parsed_blackbox_response('userinfo', blackbox_response))
        self.env.db._serialize_to_eav(self.account)

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='email_reset',
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode'],
            event='account_modification',
            operation='deleted',
        )
        self.env.statbox.bind_entry(
            'email_reset',
            _inherit_from='local_base',
            action='email_reset',
        )

    def check_statbox_entries(self, mail_domain, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'local_account_modification',
                entity='account.emails',
                old='*****@' + mail_domain,
                new='-',
                operation='deleted',
                is_suitable_for_restore='0',
                is_unsafe='1',
                **kwargs
            ),
            self.env.statbox.entry('email_reset'),
        ])

    def check_db_entries(self, query_count=2):
        for db_name, expected_count in (
            ('passportdbcentral', 0),
            ('passportdbshard1', query_count),
            ('passportdbshard2', 0),
        ):
            actual_count = self.env.db.query_count(db_name)
            eq_(
                actual_count,
                expected_count,
                'Expected %d queries into "%s", found %d.' % (
                    expected_count, db_name, actual_count,
                ),
            )

    def check_historydb_entries(self, mail_id, mail_address):
        base_entries = {
            'consumer': 'dev',
            'action': 'reset_email',
            'user_agent': 'curl',
            'email.{}'.format(mail_id): 'deleted',
            'email.{}.address'.format(mail_id): mail_address,

        }
        expected_entries = {
            k: v
            for k, v in base_entries.items()
            if v is not None
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

    def test_ok(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries(mail_id=1, mail_address=TEST_LOGIN + '@gmail.com')
        self.check_statbox_entries(
            mail_domain='gmail.com',
            email_id='1',
            confirmed_at=datetime_to_string(unixtime_to_datetime(2)),
        )

    def test_another_case_email_ok(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                'email': TEST_LOGIN.upper() + '@gmail.com',
            },
        )
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries(mail_id=1, mail_address=TEST_LOGIN + '@gmail.com')
        self.check_statbox_entries(
            mail_domain='gmail.com',
            email_id='1',
            confirmed_at=datetime_to_string(unixtime_to_datetime(2)),
        )

    def test_rpop_email_ok(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                'email': TEST_LOGIN + '@mail.ru',
            },
        )
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries(mail_id=2, mail_address=TEST_LOGIN + '@mail.ru')
        self.check_statbox_entries(
            mail_domain='mail.ru',
            email_id='2',
            confirmed_at=datetime_to_string(unixtime_to_datetime(2)),
        )

    def test_silent_email_ok(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                'email': TEST_LOGIN + '@silent.ru',
            },
        )
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries(mail_id=3, mail_address=TEST_LOGIN + '@silent.ru')
        self.check_statbox_entries(
            mail_domain='silent.ru',
            email_id='3',
            confirmed_at=datetime_to_string(unixtime_to_datetime(2)),
        )

    def test_native_email_error(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                'email': TEST_LOGIN + '@yandex.ru',
            },
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])

    def test_lite_account_reset_email_not_alias_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login='login@gmail.com',
                aliases={'lite': 'login@gmail.com'},
                crypt_password=TEST_PASSWORD_HASH,
                emails=[
                    self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                ],
                email_attributes=[
                    {
                        'id': 1,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_LOGIN + '@mail.ru',
                            EMAIL_NAME_MAPPING['is_unsafe']: '1',
                            EMAIL_NAME_MAPPING['confirmed']: '2',
                        },
                    },
                ]
            ),
        )
        resp = self.make_request(
            query_args={
                'email': TEST_LOGIN + '@mail.ru',
            },
        )
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries(mail_id=1, mail_address=TEST_LOGIN + '@mail.ru')
        self.check_statbox_entries(
            mail_domain='mail.ru',
            email_id='1',
            confirmed_at=datetime_to_string(unixtime_to_datetime(2)),
        )

    def test_lite_account_reset_alias_email_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login='login@gmail.com',
                aliases={'lite': 'login@gmail.com'},
                crypt_password=TEST_PASSWORD_HASH,
            ),
        )
        resp = self.make_request(
            query_args={
                'email': 'login@gmail.com',
            },
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])

    def test_empty_mails_error(self):
        self.set_db_fields_and_bb_response(emails=[], email_attributes=[])
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])

    def test_not_existed_email_error(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                'email': TEST_LOGIN + TEST_LOGIN + '@mail.ru',
            },
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])


@with_settings_hosts()
class TestResetPhone(BaseBundleTestViews, EmailTestMixin):
    default_url = '/1/bundle/account/reset/phone/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        uid=TEST_UID,
        phone_number=TEST_PHONE_NUMBER.e164,
    )
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIE,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['reset_phone']}))
        self.initial_data = deep_merge(
            {
                'uid': TEST_UID,
                'login': TEST_LOGIN,
                'firstname': TEST_FIRSTNAME,
                'lastname': TEST_LASTNAME,
            },
            build_phone_bound(phone_id=TEST_PHONE_ID1, phone_number=TEST_PHONE_NUMBER.e164),
        )
        self.setup_statbox_templates()

    def set_db_fields_and_bb_response(self, **kwargs):
        blackbox_response = blackbox_userinfo_response(**dict(self.initial_data, **kwargs))
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.account = Account().parse(get_parsed_blackbox_response('userinfo', blackbox_response))
        self.env.db._serialize_to_eav(self.account)

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='phone_reset',
            consumer='dev',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'phone_reset',
            _inherit_from='local_base',
            action='phone_reset',
            mode='phone_reset',
        )

    def check_statbox_entries(self):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('phone_reset'),
        ])

    def check_db_entries(self, query_count=2):
        for db_name, expected_count in (
            ('passportdbcentral', 0),
            ('passportdbshard1', query_count),
            ('passportdbshard2', 0),
        ):
            actual_count = self.env.db.query_count(db_name)
            eq_(
                actual_count,
                expected_count,
                'Expected %d queries into "%s", found %d.' % (
                    expected_count, db_name, actual_count,
                ),
            )

    def check_historydb_entries(self, phone_id, phone_numer):
        base_entries = {
            'consumer': 'dev',
            'action': 'reset_phone',
            'user_agent': 'curl',
            'phone.{}.action'.format(phone_id): 'deleted',
            'phone.{}.number'.format(phone_id): phone_numer,

        }
        expected_entries = {
            k: v
            for k, v in base_entries.items()
            if v is not None
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_entries,
        )

    def test_ok(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_entries()
        self.check_historydb_entries(phone_id=1, phone_numer=TEST_PHONE_NUMBER.e164)
        self.check_statbox_entries()

    def test_phonish_error(self):
        self.set_db_fields_and_bb_response(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    login=TEST_PHONISH_LOGIN1,
                    aliases={'phonish': TEST_PHONISH_LOGIN1},
                ),
                build_phone_bound(phone_id=TEST_PHONE_ID1, phone_number=TEST_PHONE_NUMBER.e164)
            )
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])

    def test_neophonish_error(self):
        self.set_db_fields_and_bb_response(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    aliases=dict(neophonish=TEST_NEOPHONISH_LOGIN1),
                    login=TEST_NEOPHONISH_LOGIN1,
                ),
                build_phone_bound(phone_id=TEST_PHONE_ID1, phone_number=TEST_PHONE_NUMBER.e164)
            )
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])

    def test_reset_not_existed_phone_error(self):
        self.set_db_fields_and_bb_response()
        resp = self.make_request(
            query_args={
                # изменим последнюю цифру чтоб номер наверняка отличался
                'phone_number': TEST_PHONE_NUMBER.e164[:-1] + str(9 - int(TEST_PHONE_NUMBER.e164[-1])),
            },
        )
        self.assert_error_response(resp, ['action.impossible'])
        self.check_db_entries(query_count=0)
        eq_(len(self.env.event_logger.events), 0)
        self.env.statbox.assert_has_written([])
