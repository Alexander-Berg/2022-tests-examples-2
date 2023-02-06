# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    Blackbox,
)
from passport.backend.core.builders.blackbox.constants import SECURITY_IDENTITY
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import unixtime
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import TEST_TICKET
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.utils.common import merge_dicts

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
    TestPhoneArguments,
)


@with_settings(
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_ATTRIBUTES=[],
)
class TestBlackboxRequestOAuthParse(BaseBlackboxRequestTestCase):

    def test_basic_oauth(self):
        self.set_blackbox_response_value('''
        {
            "status": {"id": 0, "value": "VALID"},
            "karma_status": {"value": 75},
            "uid": {"lite": false, "value": "3000287318", "hosted": false},
            "karma": {"value": 75},
            "error": "OK",
            "oauth": {
                "uid": "3000287318",
                "client_name": "test-client", "client_icon": "", "meta": "",
                "issue_time": "2013-07-01 17:05:01",
                "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3b",
                "scope": "login:birthday login:info login:email",
                "client_homepage": "",
                "ctime": "2013-07-01 17:05:01"
            },
            "login": "testlogin",
            "aliases": {
                "1": "testlogin"
            },
            "attributes": {
                "%d": "browser_key"
            }
        }
        ''' % AT['account.browser_key'])
        response = self.blackbox.oauth('token')
        eq_(response['uid'], 3000287318)
        eq_(response['aliases'], {'1': 'testlogin'})
        eq_(response['hosted'], False)
        eq_(response['karma'], 75)
        eq_(response['domid'], None)
        eq_(response['domain'], None)
        eq_(response['error'], 'OK')
        eq_(response['status'], 'VALID')
        eq_(response['browser_key'], 'browser_key')
        ok_('subscriptions' not in response)
        eq_(
            response['oauth'],
            {
                'uid': 3000287318,
                'client_name': 'test-client',
                'client_icon': '',
                'meta': '',
                'issue_time': '2013-07-01 17:05:01',
                'client_id': '3050e7abe75f4b29b2e3cceaee7e9b3b',
                'scope': ['login:birthday', 'login:info', 'login:email'],
                'client_homepage': '',
                'ctime': '2013-07-01 17:05:01',
            },
        )

    def test_basic_oauth_by_header(self):
        self.set_blackbox_response_value('''
        {
            "status": {"id": 0, "value": "VALID"},
            "karma_status": {"value": 75},
            "uid": {"lite": false, "value": "3000287318", "hosted": false},
            "karma": {"value": 75},
            "error": "OK",
            "oauth": {
                "uid": "3000287318",
                "client_name": "test-client", "client_icon": "", "meta": "",
                "issue_time": "2013-07-01 17:05:01",
                "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3b",
                "scope": "login:birthday login:info login:email",
                "client_homepage": "",
                "ctime": "2013-07-01 17:05:01"
            },
            "login": "testlogin",
            "attributes": {
                "%d": "browser_key"
            }
        }
        ''' % AT['account.browser_key'])
        response = self.blackbox.oauth(headers=dict(authorization='oauth 1234'))
        eq_(response['uid'], 3000287318)
        eq_(response['hosted'], False)
        eq_(response['karma'], 75)
        eq_(response['domid'], None)
        eq_(response['domain'], None)
        eq_(response['error'], 'OK')
        eq_(response['status'], 'VALID')
        eq_(response['browser_key'], 'browser_key')
        ok_('subscriptions' not in response)
        eq_(
            response['oauth'],
            {
                'uid': 3000287318,
                'client_name': 'test-client',
                'client_icon': '',
                'meta': '',
                'issue_time': '2013-07-01 17:05:01',
                'client_id': '3050e7abe75f4b29b2e3cceaee7e9b3b',
                'scope': ['login:birthday', 'login:info', 'login:email'],
                'client_homepage': '',
                'ctime': '2013-07-01 17:05:01',
            },
        )

    def test_oauth_without_user(self):
        self.set_blackbox_response_value('''
            {
                "connection_id" : "t:999003",
                "status" : {
                    "value" : "VALID",
                    "id" : 0
                },
                "error" : "OK",
                "oauth" : {
                    "client_is_yandex" : false,
                    "client_homepage" : "http://yandex.ru/",
                    "meta" : "",
                    "device_name" : "",
                    "is_ttl_refreshable" : false,
                    "scope" : "passport:check-email",
                    "ctime" : "2016-09-06 14:36:26",
                    "uid" : null,
                    "client_id" : "c9812151af4a432e9ccd8081ddff50e6",
                    "token_id" : "999003",
                    "device_id" : "",
                    "client_ctime" : "2016-08-11 14:50:56",
                    "client_icon" : "",
                    "issue_time" : "2016-09-06 14:36:26",
                    "expire_time" : null,
                    "client_name" : "WG Test app"
                }
            }''')
        response = self.blackbox.oauth(headers=dict(authorization='oauth 1234'))
        eq_(response['uid'], None)
        eq_(response['error'], 'OK')
        eq_(response['status'], 'VALID')
        eq_(
            response['oauth'],
            {
                'client_is_yandex': False,
                'client_homepage': 'http://yandex.ru/',
                'meta': '',
                'device_name': '',
                'is_ttl_refreshable': False,
                'scope': ['passport:check-email'],
                'ctime': '2016-09-06 14:36:26',
                'uid': None,
                'client_id': 'c9812151af4a432e9ccd8081ddff50e6',
                'token_id': '999003',
                'device_id': '',
                'client_ctime': '2016-08-11 14:50:56',
                'client_icon': '',
                'issue_time': '2016-09-06 14:36:26',
                'expire_time': None,
                'client_name': 'WG Test app',
            },
        )

    def test_oauth_dbfields(self):
        self.set_blackbox_response_value('''
        {
            "status": {"id": 0, "value": "VALID"},
            "karma_status": {"value": 0},
            "uid": {"lite": false, "value": "3000287318", "hosted": false},
            "login": "test",
            "dbfields": {
                "accounts.ena.uid": "1",
                "userinfo.sex.uid": "1",
                "subscription.login.8": "testlogin",
                "subscription.suid.8": "1120000000113443"
            },
            "error": "OK",
            "oauth": {
                "uid": "3000287318",
                "client_name": "test-client",
                "client_icon": "",
                "meta": "",
                "issue_time": "2013-07-01 17:05:01",
                "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3b",
                "scope": "login:birthday login:info login:email",
                "client_homepage": "",
                "ctime": "2013-07-01 17:05:01"
            },
            "display_name" : {
               "name" : ""
            }
        }
        ''')
        response = self.blackbox.oauth('token')
        eq_(response['userinfo.sex.uid'], 1)
        eq_(
            response['subscriptions'],
            {
                8: {'sid': 8, 'suid': 1120000000113443, 'login': 'testlogin'},
            }
        )
        eq_(response['display_name']['name'], '')

    def test_invalid_token(self):
        self.set_blackbox_response_value('''
        {
            "status": {"id": 5, "value": "INVALID"},
            "error": "expired_token"
        }''')
        response = self.blackbox.oauth('token')
        wait_for = {
            'status': 'INVALID',
            'error': 'expired_token',
        }
        eq_(response, wait_for)

    def test_disabled_token(self):
        self.set_blackbox_response_value('''
        {
            "status": {"id": 4, "value": "DISABLED"},
            "error": "account is disabled"
        }
        ''')
        response = self.blackbox.oauth('token')
        wait_for = {
            'status': 'DISABLED',
            'error': 'account is disabled',
        }
        eq_(response, wait_for)

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value('''{"exception":{"value":"ACCESS_DENIED","id":21},
                       "error":"BlackBox error: Access denied: OAuth"}''')
        self.blackbox.oauth('token')

    def test_oauth_parse_is_disabled_always_there(self):
        self.set_blackbox_response_value('''
        {
            "status": {"id": 0, "value": "VALID"},
            "karma_status": {"value": 75},
            "uid": {"lite": false, "value": "3000287318", "hosted": false},
            "karma": {"value": 75},
            "error": "OK",
            "oauth": {
                "uid": "3000287318",
                "client_name": "test-client", "client_icon": "", "meta": "",
                "issue_time": "2013-07-01 17:05:01",
                "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3b",
                "scope": "login:birthday login:info login:email",
                "client_homepage": "",
                "ctime": "2013-07-01 17:05:01"
            },
            "login": "testlogin",
            "aliases": {
                "1": "testlogin"
            },
            "attributes": {
                "%d": "browser_key"
            }
        }
        ''' % AT['account.browser_key'])

        response = self.blackbox.oauth(
            'token',
            attributes=[],
        )
        ok_(str(AT['account.is_disabled']) not in response['attributes'])

        response = self.blackbox.oauth(
            'token',
            attributes=[
                'account.is_disabled',
            ],
        )
        eq_(response['attributes'][str(AT['account.is_disabled'])], '0')

    def test_oauth_with_family_info(self):
        self.set_blackbox_response_value('''
        {
            "status": {"id": 0, "value": "VALID"},
            "karma_status": {"value": 75},
            "uid": {"lite": false, "value": "3000287318", "hosted": false},
            "karma": {"value": 75},
            "error": "OK",
            "oauth": {
                "uid": "3000287318",
                "client_name": "test-client", "client_icon": "", "meta": "",
                "issue_time": "2013-07-01 17:05:01",
                "client_id": "3050e7abe75f4b29b2e3cceaee7e9b3b",
                "scope": "login:birthday login:info login:email",
                "client_homepage": "",
                "ctime": "2013-07-01 17:05:01"
            },
            "login": "testlogin",
            "aliases": {
                "1": "testlogin"
            },
            "attributes": {
                "%d": "browser_key"
            },
            "family_info" : {
                "admin_uid" : "3000287318",
                "family_id" : "f1"
            }
        }
        ''' % AT['account.browser_key'])

        response = self.blackbox.oauth(
            'token',
            attributes=[],
            get_family_info=True,
        )

        eq_(response['family_info'], {'admin_uid': '3000287318', 'family_id': 'f1'})


@with_settings(
    BLACKBOX_URL='http://test.local/',
    BLACKBOX_FIELDS=[],
    BLACKBOX_ATTRIBUTES=['account.normalized_login'],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[u'number', u'created', u'bound'],
)
class TestBlackboxRequestOAuthUrl(BaseBlackboxRequestTestCase):

    base_params = {
        'userip': '127.0.0.1',
        'regname': 'yes',
        'get_public_name': 'yes',
        'is_display_name_empty': 'yes',
        'method': 'oauth',
        'format': 'json',
        'aliases': 'all_with_hidden',
        'attributes': '1008',
    }

    def setUp(self):
        super(TestBlackboxRequestOAuthUrl, self).setUp()
        self._phone_args_assertions = TestPhoneArguments(self._build_request_info)

    def test_basic_oauth(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(self.base_params, {'oauth_token': oauth_token}),
        )
        eq_(request_info.headers, {})

    def test_basic_oauth_with_request_id(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            request_id='req-id',
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'oauth_token': oauth_token,
                    'request_id': 'req-id',
                },
            ),
        )
        eq_(request_info.headers, {})

    def test_oauth_wo_hidden_aliases(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            get_hidden_aliases=False,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(self.base_params, {
                'oauth_token': oauth_token,
                'aliases': 'all',
            }),
        )
        eq_(request_info.headers, {})

    def test_oauth_no_token(self):
        request_info = Blackbox().build_oauth_request(
            ip='127.0.0.1',
        )

        check_all_url_params_match(
            request_info.url,
            self.base_params,
        )

    def test_oauth_dbfields(self):
        oauth_token = '123'
        dbfields = ['field1', 'field2']
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            dbfields=dbfields,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {'oauth_token': oauth_token, 'dbfields': u','.join(dbfields)},
            ),
        )

    def test_oauth_attributes_empty(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            attributes=[],
        )

        expected = merge_dicts(self.base_params, {'oauth_token': oauth_token})
        del expected['attributes']

        check_all_url_params_match(
            request_info.url,
            expected,
        )

    def test_oauth_emails(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            emails=True,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(self.base_params, {'oauth_token': oauth_token, 'emails': 'getall'}),
        )

    def test_oauth_browser_key(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            attributes=['account.browser_key'],
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'oauth_token': oauth_token,
                    'attributes': str(AT['account.browser_key']),
                },
            ),
        )

    def test_oauth_no_aliases(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            need_aliases=False,
        )

        expected_params = merge_dicts(self.base_params, {'oauth_token': oauth_token})
        del expected_params['aliases']
        check_all_url_params_match(
            request_info.url,
            expected_params,
        )

    def test_oauth_with_get_user_ticket(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            get_user_ticket=True,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'oauth_token': oauth_token,
                    'get_user_ticket': 'yes',
                },
            ),
        )
        eq_(
            request_info.headers,
            {'X-Ya-Service-Ticket': TEST_TICKET},
        )

    def test_oauth_token_and_client_attributes(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            need_token_attributes=True,
            need_client_attributes=True,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'oauth_token': oauth_token,
                    'oauth_token_attributes': 'all',
                    'oauth_client_attributes': 'all',
                },
            ),
        )

    def test_oauth_family_info(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            get_family_info=True,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'oauth_token': oauth_token,
                    'get_family_info': 'yes',
                },
            ),
        )

    def test_oauth_public_id(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            get_public_id=True,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'oauth_token': oauth_token,
                    'get_public_id': 'yes',
                },
            ),
        )

    def test_oauth_force_show_mail_subscription(self):
        oauth_token = '123'
        request_info = Blackbox().build_oauth_request(
            oauth_token=oauth_token,
            ip='127.0.0.1',
            force_show_mail_subscription=True,
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'oauth_token': oauth_token,
                    'force_show_mail_subscription': 'yes',
                },
            ),
        )

    def test_request_phones_is_all_when_phones_arg_value_is_all(self):
        self._phone_args_assertions.assert_request_phones_is_all_when_phones_arg_value_is_all()

    def test_request_has_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_not_empty(self):
        self._phone_args_assertions.assert_request_has_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_not_empty()

    def test_request_has_no_phone_attributes_when_phone_attributes_is_empty(self):
        self._phone_args_assertions.assert_request_has_no_phone_attributes_when_phone_attributes_is_empty()

    def test_request_has_no_phone_attributes_when_phones_is_none_and_phone_attributes_is_not_empty(self):
        self._phone_args_assertions.assert_request_has_no_phone_attributes_when_phones_is_none_and_phone_attributes_is_not_empty()

    def test_request_has_default_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_none(self):
        self._phone_args_assertions.assert_request_has_default_phone_attributes_when_phones_is_not_empty_and_phone_attributes_is_none()

    def test_request_get_phone_operations_is_one_when_need_phone_operations_is_true(self):
        self._phone_args_assertions.assert_request_get_phone_operations_is_one_when_need_phone_operations_is_true()

    def test_request_has_no_phone_operations_when_need_phone_operations_is_false(self):
        self._phone_args_assertions.assert_request_has_no_phone_operations_when_need_phone_operations_is_false()

    def test_phone_bindings(self):
        self._phone_args_assertions.test_phone_bindings()

    def _build_request_info(self, **kwargs):
        return Blackbox().build_oauth_request(**kwargs)


@with_settings(
    BLACKBOX_URL=u'http://bl.ackb.ox/',
    BLACKBOX_ATTRIBUTES=[],
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=[],
)
class RequestTestOauthParsePhones(BaseBlackboxTestCase):
    def setUp(self):
        super(RequestTestOauthParsePhones, self).setUp()
        self._blackbox = Blackbox()
        self._faker = FakeBlackbox()
        self._faker.start()

    def tearDown(self):
        self._faker.stop()
        del self._faker
        super(RequestTestOauthParsePhones, self).tearDown()

    def test_phone_with_empty_attributes_when_response_has_phone_and_empty_attributes(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phones=[{u'id': 22}]),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=None,
        )

        eq_(response[u'phones'], {22: {u'id': 22, u'attributes': {}}})

    def test_phone_attribute_phone_number_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 1, u'number': u'+79036655444'}],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=[u'number'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'number'],
            u'+79036655444',
        )

    def test_phone_attribute_created_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 1, u'created': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=[u'created'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'created'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_bound_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 1, u'bound': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=[u'bound'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'bound'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_confirmed_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 1, u'confirmed': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=[u'confirmed'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'confirmed'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_admitted_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 1, u'admitted': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=[u'admitted'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'admitted'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_secured_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 1, u'secured': datetime(2005, 6, 1, 22, 5, 4)}],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=[u'secured'],
        )

        eq_(
            response[u'phones'][1][u'attributes'][u'secured'],
            unixtime(2005, 6, 1, 22, 5, 4),
        )

    def test_phone_attribute_is_default_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 1, u'is_default': 1}],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            phone_attributes=[u'is_default'],
        )

        ok_(response[u'phones'][1][u'attributes'][u'is_default'])

    def test_operation_id_equals_to_operation_id_from_response(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        ok_(5 in response[u'phone_operations'])
        eq_(response[u'phone_operations'][5][u'id'], 5)

    def test_single_operation_when_response_has_single_operations(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 1)

    def test_many_operations_when_response_has_many_operations(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[
                {u'id': 5, u'phone_number': u'+79047766555'},
                {u'id': 6, u'phone_number': u'+79036655444'},
            ]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(len(response[u'phone_operations']), 2)

    def test_operation_phone_id_equals_to_operation_phone_id_from_response(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_id': 7,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], 7)

    def test_operation_phone_is_none_when_response_has_not_operation_phone_id(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_id': None,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id'], None)

    def test_operation_security_identity_is_like_phone_number_when_operation_is_not_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'security_identity'], 79047766555)

    def test_operation_security_identity_is_predefined_value_when_operation_is_on_secure_phone_number(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'security_identity': SECURITY_IDENTITY,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'security_identity'],
            SECURITY_IDENTITY,
        )

    def test_phone_operation_started_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_started_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'started': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'started'],
            None,
        )

    def test_phone_operation_finished_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_finished_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'finished': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'finished'],
            None,
        )

    def test_phone_operation_code_last_sent_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_last_sent'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_last_sent_is_empty_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_last_sent': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_last_sent'], None)

    def test_phone_operation_code_confirmed_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_code_confirmed_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_confirmed': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'code_confirmed'],
            None,
        )

    def test_phone_operation_password_verified_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': datetime(2005, 10, 2, 12, 10, 10),
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            unixtime(2005, 10, 2, 12, 10, 10),
        )

    def test_phone_operation_password_verified_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'password_verified': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'password_verified'],
            None,
        )

    def test_phone_operation_code_send_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': 7,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 7)

    def test_phone_operation_code_send_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_send_count': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_send_count'], 0)

    def test_phone_operation_phone_id2_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': 31,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], 31)

    def test_phone_operation_phone_id2_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'phone_id2': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'phone_id2'], None)

    def test_phone_operation_flags_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': PhoneOperationFlags(1),
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(1)),
        )

    def test_phone_operation_flags_equals_to_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'flags': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(
            response[u'phone_operations'][5][u'flags'],
            int(PhoneOperationFlags(0)),
        )

    def test_phone_operation_code_checks_count_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': 16,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 16)

    def test_phone_operation_code_checks_count_is_zero_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_checks_count': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_checks_count'], 0)

    def test_phone_operation_code_value_equals_to_response_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': u'1234',
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], u'1234')

    def test_phone_operation_code_value_is_none_when_response_has_no_value(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[{
                u'id': 5,
                u'phone_number': u'+79047766555',
                u'code_value': None,
            }]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        eq_(response[u'phone_operations'][5][u'code_value'], None)

    def test_phone_operation_is_attached_to_phone(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{
                    u'id': 14,
                }],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 14,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.oauth()

        ok_(response[u'phones'][14][u'operation'] is response[u'phone_operations'][5])

    def test_no_phones_and_no_phone_operations_when_response_has_no_phone_and_no_phone_operations(self):
        self._faker.set_response_value(u'oauth', blackbox_oauth_response())

        response = self._blackbox.oauth()

        ok_(u'phones' not in response)
        ok_(u'phone_operations' not in response)

    def test_empty_phones_when_response_has_empty_phones(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phones=[]),
        )

        response = self._blackbox.oauth(phones=u'all')

        ok_(u'phones' in response)
        eq_(len(response[u'phones']), 0)

    def test_no_phones_and_empty_operations_when_response_has_no_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phone_operations=[]),
        )

        response = self._blackbox.oauth(need_phone_operations=True)

        ok_(u'phones' not in response)
        ok_(u'phone_operations' in response)
        eq_(len(response[u'phone_operations']), 0)

    def test_no_operation_in_phone_when_response_has_phone_and_no_operation(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(phones=[{u'id': 14}]),
        )

        response = self._blackbox.oauth(phones=u'all')

        ok_(u'phones' in response)
        ok_(u'phone_operations' not in response)
        ok_(u'operation' not in response[u'phones'][14])

    def test_phone_operation_is_on_phone_when_response_has_phone_and_operation_on_it(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 14,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(u'operation' in response[u'phones'][14])

    def test_phone_operation_on_phone_is_none_when_response_has_phones_and_empty_operations(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 14}],
                phone_operations=[],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(u'phones' in response)
        ok_(u'phone_operations' in response)
        ok_(response[u'phones'][14][u'operation'] is None)

    def test_phone_operation_is_in_phone_operations_and_phone_operation_on_phone_is_none_when_response_has_zombie_operation(self):
        self._faker.set_response_value(
            u'oauth',
            blackbox_oauth_response(
                phones=[{u'id': 14}],
                phone_operations=[{
                    u'id': 5,
                    u'phone_id': 15,
                    u'phone_number': u'+79047766555',
                }],
            ),
        )

        response = self._blackbox.oauth(
            phones=u'all',
            need_phone_operations=True,
        )

        ok_(response[u'phones'][14][u'operation'] is None)
        ok_(5 in response[u'phone_operations'])
