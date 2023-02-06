# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from functools import partial
import json

from furl import furl
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.test.test_utils.utils import iterdiff
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.exception import (
    BasicProxylibError,
    InvalidTokenProxylibError,
    PermissionProxylibError,
)
from passport.backend.social.common.misc import dump_to_json_string
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
    SIMPLE_USERID1,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import ApproximateInteger
import passport.backend.social.proxylib
from passport.backend.social.proxylib import get_proxy
from passport.backend.social.proxylib.test import facebook as facebook_test

from . import TestProxy


class TestProxyFacebook(TestProxy):
    provider_code = 'fb'
    error_profile_response = '{"error":{"message":"Invalid OAuth access token.","type":"OAuthException","code":190}}'

    def test_profile_ok(self):
        decoded_data = {
            'last_name': 'ln',
            'locale': 'en_US',
            'birthday': '12/28/1989',
            'timezone': 4,
            'id': '10206062428549536',
            'first_name': 'fn',
            'gender': 'male',
            'email': 'mail@example.com',
            'picture': {
                'data': {
                    'is_silhouette': False,
                    'url': 'https://fbcdn-profile-a.akamaihd.net',
                }
            },
            'token_for_business': 'abcdefg',
        }
        decoded_data = dump_to_json_string(decoded_data)

        expected_dict = {
            'firstname': 'fn',
            'lastname': 'ln',
            'userid': '10206062428549536',
            'birthday': '1989-12-28',
            'avatar': {
                '0x0': 'https://fbcdn-profile-a.akamaihd.net',
            },
            'gender': 'm',
            'email': 'mail@example.com',
            'token_for_business': 'abcdefg',
        }

        self._process_single_test(
            'get_profile',
            decoded_data,
            expected_dict=expected_dict,
        )

    def test_profile_error(self):
        self._tst_profile_error()

    def test_unicode_response(self):
        error_msg = ('{"error":{"message":"Error validating access token: Session has expired on 25'
                     ' \\u0444\\u0435\\u0432\\u0440\\u0430\\u043b\\u044f 2014 \\u0433. 4:52. The current time is '
                     '25 \\u0444\\u0435\\u0432\\u0440\\u0430\\u043b\\u044f 2014 \\u0433. 5:05.","type":"OAuthException"'
                     ',"code":190,"error_subcode":463}}')
        self._tst_profile_error(error_response=error_msg)

    def test_friends_ok(self):
        friends1 = [{'id': i} for i in xrange(100)]
        friends2 = [{'id': i} for i in xrange(100, 130)]

        self._process_single_test(
            'get_friends',
            [json.dumps({'data': f}) for f in [friends1, friends2]],
            expected_list=[{'userid': str(i)} for i in xrange(130)],
        )

    def test_parse_error_response(self):
        repo = self.proxy.r
        repo.context = {'data': {
            'error': {
                'message': ('(#200) The \'manage_notifications\' permission is required in order to read the user\'s '
                            'notifications or mark them as read.'),
                'type': 'OAuthException',
                'code': 200,
            },
        }}
        self.assertRaises(PermissionProxylibError, repo.parse_error_response)

        repo.context = {'data': {
            'error': {
                'message': ('Error validating access token: Session has expired at unix time 1382713200. The current'
                            ' unix time is 1383036581.'),
                'type': 'OAuthException',
                'code': 190,
                'error_subcode': 463,
            },
        }}
        self.assertRaises(InvalidTokenProxylibError, repo.parse_error_response)

        repo.context = {'data': {
            'error': {
                'message': 'Some other exception',
                'type': 'OAuthException',
                'code': 1,
            },
        }}
        self.assertRaises(BasicProxylibError, repo.parse_error_response)

    def test_get_profile_links(self):
        links = self.proxy.get_profile_links('12345', 'some_user')
        self.assertEqual(links, list())


class TestFacebook(TestCase):
    def setUp(self):
        super(TestFacebook, self).setUp()
        passport.backend.social.proxylib.init()
        self._proxy = facebook_test.FakeProxy().start()

    def tearDown(self):
        self._proxy.stop()
        super(TestFacebook, self).tearDown()

    def _assert_url_equals(self, url, expected):
        url = furl(url)
        eq_(url.origin + str(url.path), expected)

    def _assert_query_equals(self, url, expected):
        url = furl(url)

        query = dict(url.args)

        if 'fields' in query:
            fields = query['fields']
            fields = fields.split(',')
            fields.sort()
            query['fields'] = fields

        iterdiff(eq_)(query, expected)

    def test_token_info__ok(self):
        self._proxy.set_response_value(
            'get_token_info',
            facebook_test.GraphApi.get_token_info(),
        )

        rv = get_proxy().get_token_info()

        eq_(
            rv,
            {
                'userid': SIMPLE_USERID1,
                'scopes': ['user_birthday', 'email', 'public_profile'],
                'expires': 1477919606,
                'valid': True,
                'issued': 1472735606,
                'client_id': EXTERNAL_APPLICATION_ID1,
            },
        )

    def test_exchange_token__ok(self):
        self._proxy.set_response_value(
            'exchange_token',
            facebook_test.GraphApi.exchange_token(),
        )

        rv = get_proxy().exchange_token()

        eq_(
            rv,
            {
                'value': APPLICATION_TOKEN1,
                'expires': ApproximateInteger(now.f() + APPLICATION_TOKEN_TTL1),
            },
        )

    @raises(InvalidTokenProxylibError)
    def test_exchange_token__token_not_match_app(self):
        self._proxy.set_response_value(
            'exchange_token',
            facebook_test.GraphApi.build_error(code=190),
        )

        get_proxy().exchange_token()

    def test_get_profile__request(self):
        self._proxy.set_response_value(
            'get_profile',
            facebook_test.GraphApi.get_profile(),
        )

        get_proxy().get_profile()

        request = self._proxy.requests[0]
        self._assert_url_equals(request['url'], 'https://graph.facebook.com/v10.0/me')
        self._assert_query_equals(
            request['url'],
            dict(
                access_token=APPLICATION_TOKEN1,
                fields=[
                    'birthday',
                    'email',
                    'first_name',
                    'friends.limit(0)',
                    'gender',
                    'id',
                    'last_name',
                    'middle_name',
                    'picture.type(large)',
                    'token_for_business',
                ],
            ),
        )

    def test_get_friends__request(self):
        self._proxy.set_response_value(
            'get_friends',
            facebook_test.GraphApi.get_friends(users=[dict()]),
        )

        get_proxy().get_friends()

        request = self._proxy.requests[0]
        self._assert_url_equals(request['url'], 'https://graph.facebook.com/v10.0/me/friends')
        self._assert_query_equals(
            request['url'],
            dict(
                access_token=APPLICATION_TOKEN1,
                fields=[
                    'birthday',
                    'email',
                    'first_name',
                    'gender',
                    'id',
                    'last_name',
                    'middle_name',
                    'picture.type(large)',
                ],
                offset='0',
                limit='100',
            ),
        )


get_proxy = partial(
    get_proxy,
    Facebook.code,
    {'value': APPLICATION_TOKEN1},
    Application(
        id=EXTERNAL_APPLICATION_ID1,
        secret=APPLICATION_SECRET1,
    ),
)
