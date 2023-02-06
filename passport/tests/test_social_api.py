# -*- coding: utf-8 -*-

import json

from mock import (
    ANY as MockAny,
    Mock,
)
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.social_api import (
    BaseSocialApiError,
    ProfileNotFoundError,
    SocialApi,
    SocialApiRequestError,
    SocialApiTemporaryError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
    TaskNotFoundError,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    FakeSocialApi,
    get_ok_response,
    get_profile_info,
    get_subscription_info,
    profile_not_found_error,
    social_api_v3_error_response,
    subscription_not_found_error,
    task_not_found_error,
)
from passport.backend.core.builders.social_api.profiles import convert_task_profile
from passport.backend.core.test.consts import TEST_CONSUMER1
from passport.backend.core.test.test_utils import (
    check_url_equals,
    PassportTestCase,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.social_business_info import BusinessInfo
from passport.backend.core.useragent.sync import (
    RequestError,
    UserAgent,
)


DEFAULT_CA_CERT = 'default-ca-cert-path'

task_id = '87a34cb5c9d9478593b9df14f1212aab'

response_task_normal = '''{
  "provider_id": "5",
  "application_id": "52",
  "app_name": "google-oauth2",
  "requested_scope": "https://www.googleapis.com/auth/userinfo.profile,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/plus.login",
  "retpath": "https://flider.passportdev.yandex.ru/callback?consumer=dev&track_id=423ddbbad0422428ce81e193f51d9b747f",
  "yandexuid": "1272660251379517491",
  "final_timestamp": "1380194218.01",
  "consumer_id": "95",
  "frontend_url": "https://socialdev-1.yandex.ru/broker2/",
  "provider_code": "gg",
  "task_id": "87a34cb5c9d9478593b9df14f1212aab",
  "created": "1380194217.17",
  "access_token": {
    "expires": 1380183417.0,
    "value": "ya29.AHES6ZSwwT17bSwREvwodzvwawV33F22SfvSfcugFbonPRspy000000"
  },
  "hostname": "socialdev-1.yandex.ru",
  "place": "None",
  "profile": {
    "username": "username",
    "firstname": "Anton",
    "lastname": "Kirilenko",
    "email": "user@gmail.com",
    "birthday": null,
    "gender": "m",
    "id": "112913562853868300000"
  },
  "tld": "ru",
  "scope": "[]"
}
'''

error_response = '''
{
  "error": {
    "description": "Missed required attribute `uid` or `uids` or both `userid` and `provider_id`",
    "name": "missing-attributes",
    "request_id": "7b240321-3"
  }
}
'''

userid = '112913562853868300000'
provider_id = 8
provider = 'gg'
uid = 111110000
sid = 2
profile_id = 600
response_profiles_normal = '''{
  "profiles": [
    {
      "username": "some.username",
      "uid": 111110000,
      "profile_id": 600,
      "userid": "112913562853868300000",
      "allow_auth": true,
      "provider": "google",
      "provider_code": "gg",
      "addresses": []
    },
    {
      "username": "another.username",
      "uid": 111110001,
      "profile_id": 601,
      "userid": "112913562853868300000",
      "allow_auth": false,
      "provider": "google",
      "provider_code": "gg",
      "addresses": []
    }
  ]
}
'''
response_profiles_normal_with_uid = '''{
  "profiles": [
    {
      "username": "some.username",
      "uid": 111110000,
      "profile_id": 600,
      "userid": "112913562853868300000",
      "allow_auth": true,
      "provider": "google",
      "provider_code": "gg",
      "addresses": []
    }
  ]
}
'''
response_profiles_normal_with_uid_with_provider = '''{
  "profiles": [
    {
      "username": "some.username",
      "uid": 111110000,
      "profile_id": 600,
      "userid": "112913562853868300000",
      "allow_auth": true,
      "provider": {
        "name": "google",
        "id": 5,
        "code": "gg"
      },
      "addresses": []
    }
  ]
}
'''
response_profiles_normal_with_uid_with_person_template = '''{
  "profiles": [
    {
      "username": "some.username",
      "uid": 111110000,
      "profile_id": 600,
      "userid": "112913562853868300000",
      "person": {
        "firstname": "Ivan",
        "lastname": "Ivanov",
        "profile_id": 100996,
        "birthday": "%s",
        "gender": "",
        "nickname": "",
        "email": ""
      },
      "allow_auth": true,
      "provider": "google",
      "provider_code": "gg",
      "addresses": []
    }
  ]
}
'''
response_profiles_with_uid_with_person = response_profiles_normal_with_uid_with_person_template % '2010-10-10'
response_profiles_with_uid_with_person_no_birthday = response_profiles_normal_with_uid_with_person_template % 'None'
response_profiles_normal_with_uid_without_person_template = '''{
  "profiles": [
    {
      "username": "some.username",
      "uid": 111110000,
      "profile_id": 600,
      "userid": "112913562853868300000",
      "allow_auth": true,
      "provider": "google",
      "provider_code": "gg",
      "addresses": []
    }
  ]
}
'''
response_profiles_normal_with_uid_with_subscriptions = '''{
  "profiles": [
    {
      "username": "IvanIva08506451",
      "uid": 3000453623,
      "subscriptions": [
        {
          "sid": 2
        },
        {
          "sid": 58
        }
      ],
      "profile_id": 100996,
      "userid": "2483443826",
      "allow_auth": false,
      "provider": "twitter",
      "provider_code": "tw",
      "addresses": [
        "http://twitter.com/IvanIva08506451/"
      ]
    }
  ]
}
'''
response_profiles_normal_with_uid_with_tokens = '''{
  "profiles": [
    {
      "username": "IvanIva08506451",
      "uid": 3000453623,
      "profile_id": 100996,
      "userid": "2483443826",
      "tokens": [
        {
          "profile_id": 100996,
          "created_ts": 1399544624,
          "token_id": 8551,
          "expired": null,
          "confirmed": "2014-05-08 14:23:44",
          "expired_ts": null,
          "verified": "2014-05-08 14:23:44",
          "created": "2014-05-08 14:23:44",
          "value": "2483443826-PxTGwUK2iadDtnI2ipkF0oRlbjYTzr7fbVNQKvD",
          "application": "twitter",
          "secret": "FJCtukLsodOBAGAs2DtRaVsM4a8TgKbyRh470iebpAjbK",
          "confirmed_ts": 1399544624,
          "scope": "read",
          "verified_ts": 1399544624
        }
      ],
      "allow_auth": false,
      "provider": "twitter",
      "provider_code": "tw",
      "addresses": [
        "http://twitter.com/IvanIva08506451/"
      ]
    }
  ]
}
'''
response_profiles_normal_with_uid_with_all_data = '''{
  "profiles": [
    {
      "username": "IvanIva08506451",
      "uid": 3000453623,
      "subscriptions": [
        {
          "sid": 2
        },
        {
          "sid": 58
        }
      ],
      "profile_id": 100996,
      "userid": "2483443826",
      "tokens": [
        {
          "profile_id": 100996,
          "created_ts": 1399544624,
          "token_id": 8551,
          "expired": null,
          "confirmed": "2014-05-08 14:23:44",
          "expired_ts": null,
          "verified": "2014-05-08 14:23:44",
          "created": "2014-05-08 14:23:44",
          "value": "2483443826-PxTGwUK2iadDtnI2ipkF0oRlbjYTzr7fbVNQKvD",
          "application": "twitter",
          "secret": "FJCtukLsodOBAGAs2DtRaVsM4a8TgKbyRh470iebpAjbK",
          "confirmed_ts": 1399544624,
          "scope": "read",
          "verified_ts": 1399544624
        }
      ],
      "person": {
        "firstname": "Ivan",
        "lastname": "Ivanov",
        "profile_id": 100996,
        "birthday": "None",
        "gender": "",
        "nickname": "",
        "email": ""
      },
      "allow_auth": false,
      "provider": "twitter",
      "provider_code": "tw",
      "addresses": [
        "http://twitter.com/IvanIva08506451/"
      ]
    }
  ]
}
'''
response_update_or_create_profile_normal = '''
{
  "status": "ok",
  "profile_id": 600,
  "uid": "111110000"
}
'''


@with_settings(
    SOCIAL_API_URL='http://none.yandex.ru/api/',
    SOCIAL_API_CONSUMER=TEST_CONSUMER1,
    SOCIAL_API_RETRIES=2,
    SOCIAL_API_TIMEOUT=1,
    SSL_CA_CERT=DEFAULT_CA_CERT,
)
class TestSocialApi(PassportTestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'social_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.useragent = UserAgent()
        self.response = Mock()
        self.useragent.request = Mock(return_value=self.response)
        self.social_api = SocialApi(useragent=self.useragent)

    def tearDown(self):
        del self.useragent
        del self.response
        del self.social_api
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_get_task_data_ok(self):
        self.response.content = response_task_normal
        self.social_api.get_task_data(task_id)

    def check_http_call(self, url):
        self.useragent.request.assert_called_once_with(
            'GET',
            MockAny,
            timeout=self.social_api.timeout,
            graphite_logger=self.social_api.graphite_logger,
            statbox_logger=self.social_api.statbox_logger,
            reconnect=False,
            verify=DEFAULT_CA_CERT,
            headers={'X-Ya-Service-Ticket': TEST_TICKET},
        )

        actual_url = self.useragent.request.call_args[0][1]
        check_url_equals(actual_url, url)

    @raises(BaseSocialApiError)
    def test_error_response(self):
        self.useragent.request.side_effect = RequestError('text')
        self.social_api.get_task_data(task_id)

    @raises(TaskNotFoundError)
    def test_get_tast_data__task_not_found(self):
        self.response.content = json.dumps(task_not_found_error())
        self.social_api.get_task_data(task_id)

    @raises(BaseSocialApiError)
    def test_get_task_data_error(self):
        self.response.content = error_response
        self.social_api.get_task_data(task_id)

    @raises(TaskNotFoundError)
    def test_get_tast_data__no_task(self):
        self.response.content = response_task_normal
        self.social_api.get_task_data('')

    def test_get_profiles_ok(self):
        self.response.content = response_profiles_normal
        profiles = self.social_api.get_profiles(userid, provider_id=provider_id)
        eq_(len(profiles), 2)

        self.response.content = response_profiles_normal
        profiles = self.social_api.get_profiles(userid, provider=provider)
        eq_(len(profiles), 2)

        self.response.content = response_profiles_normal_with_uid
        profiles = self.social_api.get_profiles(userid, provider_id, uid=uid)
        eq_(len(profiles), 1)

        self.response.content = response_profiles_normal_with_uid
        profiles = self.social_api.get_profiles(uids='%s,12345678' % uid)
        eq_(len(profiles), 1)

    def test_get_profiles_with_person(self):
        self.response.content = response_profiles_with_uid_with_person
        profiles = self.social_api.get_profiles(userid, provider_id=provider_id, person=True)
        self.check_http_call(
            'http://none.yandex.ru/api/profiles?consumer=%s&provider_id=%s&include=person&userid=%s' % (TEST_CONSUMER1, provider_id, userid),
        )
        eq_(len(profiles), 1)

    def test_get_profiles_with_subscriptions(self):
        self.response.content = response_profiles_normal_with_uid_with_subscriptions
        profiles = self.social_api.get_profiles(userid, provider_id=provider_id, subscriptions=True)
        self.check_http_call(
            'http://none.yandex.ru/api/profiles?consumer=%s&provider_id=%s&include=subscriptions&userid=%s' % (TEST_CONSUMER1, provider_id, userid),
        )
        eq_(len(profiles), 1)

    def test_get_profiles_with_tokens(self):
        self.response.content = response_profiles_normal_with_uid_with_tokens
        profiles = self.social_api.get_profiles(userid, provider_id=provider_id, tokens=True)
        self.check_http_call(
            'http://none.yandex.ru/api/profiles?provider_id=%s&include=tokens&userid=%s&consumer=%s' % (provider_id, userid, TEST_CONSUMER1),
        )
        eq_(len(profiles), 1)

    def test_get_profiles_with_business_info(self):

        self.response.content = response_profiles_normal_with_uid_with_tokens
        profiles = self.social_api.get_profiles(
            userid,
            provider_id=provider_id,
            business_info=BusinessInfo(1, 'abc'),
        )
        self.check_http_call(
            'http://none.yandex.ru/api/profiles?consumer=%s&provider_id=%s&userid=%s&business_token=abc&business_id=1' % (TEST_CONSUMER1, provider_id, userid),
        )
        eq_(len(profiles), 1)

    def test_get_profiles_with_all_data(self):
        self.response.content = response_profiles_normal_with_uid_with_all_data
        profiles = self.social_api.get_profiles(
            userid,
            provider_id=provider_id,
            subscriptions=True,
            tokens=True,
            person=True,
        )
        self.check_http_call(
            'http://none.yandex.ru/api/profiles?consumer=%s&provider_id=%s&include=subscriptions%%2Ctokens%%2Cperson&userid=%s' % (TEST_CONSUMER1, provider_id, userid),
        )
        eq_(len(profiles), 1)

    @raises(ValueError)
    def test_get_profile_raises(self):
        self.social_api.get_profiles(userid)

    def test_get_profiles_by_uid(self):
        self.response.content = response_profiles_normal_with_uid
        profiles = self.social_api.get_profiles_by_uid(uid)
        self.check_http_call(
            'http://none.yandex.ru/api/user/111110000/profile?consumer=%s' % TEST_CONSUMER1,
        )
        eq_(len(profiles), 1)

    def test_get_profiles_by_uid_with_provider(self):
        self.response.content = response_profiles_normal_with_uid_with_provider
        profiles = self.social_api.get_profiles_by_uid(uid, expand_provider=True)
        self.check_http_call(
            'http://none.yandex.ru/api/user/111110000/profile?consumer=%s&expand=provider' % TEST_CONSUMER1,
        )
        eq_(len(profiles), 1)

    def test_get_profiles_by_uid_with_person(self):
        self.response.content = response_profiles_with_uid_with_person
        profiles = self.social_api.get_profiles_by_uid(uid, person=True)
        self.check_http_call(
            'http://none.yandex.ru/api/user/111110000/profile?consumer=%s&include=person' % TEST_CONSUMER1,
        )
        eq_(len(profiles), 1)

    def test_get_profiles_by_uid_with_subscriptions(self):
        self.response.content = response_profiles_normal_with_uid_with_subscriptions
        profiles = self.social_api.get_profiles_by_uid(uid, subscriptions=True)
        self.check_http_call(
            'http://none.yandex.ru/api/user/111110000/profile?consumer=%s&include=subscriptions' % TEST_CONSUMER1,
        )
        eq_(len(profiles), 1)

    def test_get_profiles_by_uid_with_tokens(self):
        self.response.content = response_profiles_normal_with_uid_with_tokens
        profiles = self.social_api.get_profiles_by_uid(uid, tokens=True)
        self.check_http_call(
            'http://none.yandex.ru/api/user/111110000/profile?consumer=%s&include=tokens' % TEST_CONSUMER1,
        )
        eq_(len(profiles), 1)

    def test_get_profiles_by_uid_with_all_data(self):
        self.response.content = response_profiles_normal_with_uid_with_all_data
        profiles = self.social_api.get_profiles_by_uid(uid, subscriptions=True, tokens=True, person=True)
        self.check_http_call(
            'http://none.yandex.ru/api/user/111110000/profile?consumer=%s&include=subscriptions%%2Ctokens%%2Cperson' % TEST_CONSUMER1,
        )
        eq_(len(profiles), 1)

    def test_bind_task_profile_ok(self):
        self.response.content = response_update_or_create_profile_normal
        result_profile_id = self.social_api.bind_task_profile(task_id, uid)
        eq_(result_profile_id, profile_id)

    def test_delete_all_profiles_by_uid_ok(self):
        self.response.content = ''
        response = self.social_api.delete_all_profiles_by_uid(uid)
        assert_is_none(response)

    def test_delete_profile_ok(self):
        self.response.content = ''
        response = self.social_api.delete_profile(profile_id)
        assert_is_none(response)

    @raises(ProfileNotFoundError)
    def test_delete_profile_not_found(self):
        self.response.content = json.dumps(profile_not_found_error())
        self.social_api.delete_profile(profile_id)

    def test_set_authentificate_profile_ok(self):
        self.response.content = json.dumps(get_profile_info(uid, profile_id, 1))
        response = self.social_api.set_authentificate_profile(profile_id, 1)
        ok_(response['profile']['auth_allow'])
        eq_(response['profile']['profile_id'], profile_id)

    @raises(ProfileNotFoundError)
    def test_set_authentificate_profile_not_found(self):
        self.response.content = json.dumps(profile_not_found_error())
        self.social_api.set_authentificate_profile(profile_id, 1)

    def test_delete_subscription_ok(self):
        self.response.content = ''
        response = self.social_api.delete_subscription(profile_id, sid)
        assert_is_none(response)

    @raises(ProfileNotFoundError)
    def test_delete_subscription_profile_not_found(self):
        self.response.content = json.dumps(profile_not_found_error())
        self.social_api.delete_subscription(profile_id, sid)

    @raises(SubscriptionNotFoundError)
    def test_delete_subscription_not_found(self):
        self.response.content = json.dumps(subscription_not_found_error())
        self.social_api.delete_subscription(profile_id, 0)

    @raises(SubscriptionAlreadyExistsError)
    def test_create_subscription_already_exists(self):
        self.response.status_code = 409
        self.social_api.create_subscription(profile_id, sid)

    def test_create_subscription_ok(self):
        self.response.content = json.dumps(get_subscription_info(profile_id, sid))
        response = self.social_api.create_subscription(profile_id, sid)
        eq_(response['subscription']['sid'], sid)

    @raises(SocialApiRequestError)
    def test_invalid_json_data(self):
        self.response.content = 'not json'
        profiles = self.social_api.get_profiles(userid, provider_id=provider_id)
        eq_(len(profiles), 2)

    def test_error_response_parsing(self):
        data = {'error': {'name': 'internal-exception', 'description': 'descr'}}
        with assert_raises(SocialApiTemporaryError):
            self.social_api.check_response_for_errors(data, Mock())

        data = {'error': {'name': 'external', 'description': 'descr'}}
        try:
            self.social_api.check_response_for_errors(data, Mock())
        except Exception as ex:
            ok_(isinstance(ex, BaseSocialApiError))
            ok_(not isinstance(ex, SocialApiTemporaryError))

    def test_retries_after_network_error(self):

        def _temporary_request_method(method, url, counter=[0], **kwargs):
            counter[0] += 1
            if counter[0] == 1:
                raise RequestError()
            else:
                return Mock(content=response_task_normal)

        self.useragent.request.side_effect = _temporary_request_method
        response = self.social_api.get_task_data(task_id)
        eq_(response['application_id'], '52')

    def test_retries_after_logical_error(self):
        def _temporary_request_method(method, url, counter=[0], **kwargs):
            counter[0] += 1
            if counter[0] == 1:
                return Mock(content='{"error": {"name": "internal-exception"}}')
            else:
                return Mock(content=response_task_normal)

        self.useragent.request.side_effect = _temporary_request_method
        response = self.social_api.get_task_data(task_id)
        eq_(response['application_id'], '52')


@with_settings(
    SOCIAL_API_URL='https://social/api/',
    SOCIAL_API_CONSUMER=TEST_CONSUMER1,
    SOCIAL_API_RETRIES=1,
    SOCIAL_API_TIMEOUT=1,
)
class TestSocialApiV2(PassportTestCase):
    def setUp(self):
        super(TestSocialApiV2, self).setUp()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'social_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self._faker = FakeSocialApi()
        self._faker.start()
        self._social_api = SocialApi()

    def tearDown(self):
        del self._social_api
        self._faker.stop()
        del self._faker
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager
        super(TestSocialApiV2, self).tearDown()

    def _check_for_errors(self, response_dict):
        self._social_api.check_response_v3_for_errors(response_dict, json.dumps(response_dict))

    def _assert_error_code_raises_exception(self, error_code, exception):
        with assert_raises(exception) as assertion:
            self._check_for_errors(social_api_v3_error_response(error_code))
        eq_(assertion.exception.args[0], error_code)

    def test_check_response_v3_for_errors__not_error(self):
        self._check_for_errors(get_ok_response())

    def test_check_response_v3_for_errors__unknown_error(self):
        self._assert_error_code_raises_exception('unknown', BaseSocialApiError)

    def test_check_response_v3_for_errors_database_failed(self):
        self._assert_error_code_raises_exception('database.failed', SocialApiTemporaryError)

    def test_check_response_v3_for_errors_exception_unhandled(self):
        self._assert_error_code_raises_exception('exception.unhandled', SocialApiTemporaryError)

    def test_delete_social_data__ok(self):
        self._faker.set_response_side_effect(
            'delete_social_data',
            [
                json.dumps(get_ok_response()),
            ],
        )

        rv = self._social_api.delete_social_data([1, 2])

        eq_(rv, {'status': 'ok'})

        eq_(len(self._faker.requests), 1)
        self._faker.requests[0].assert_properties_equal(
            method='POST',
            url='https://social/api/delete_social_data?consumer=%s' % TEST_CONSUMER1,
            post_args={'profile_ids': '1,2'},
        )

    def test_delete_social_data__fail(self):
        self._faker.set_response_side_effect(
            'delete_social_data',
            [
                json.dumps(social_api_v3_error_response('fail')),
            ],
        )

        with assert_raises(BaseSocialApiError) as assertion:
            self._social_api.delete_social_data([])
        eq_(assertion.exception.args[0], 'fail')

    def test_delete_tokens_from_account(self):
        self._faker.set_response_side_effect('delete_tokens_from_account', [''])

        self._social_api.delete_tokens_from_account(uid=uid, provider_name='apl', revoke=True)

        eq_(len(self._faker.requests), 1)
        self._faker.requests[0].assert_properties_equal(
            method='POST',
            url='https://social/api/token/delete_from_account?consumer=%s' % TEST_CONSUMER1,
            post_args=dict(
                provider_name='apl',
                revoke='1',
                uid=str(uid),
            ),
        )


def test_convert_task_profile():
    def _single_test(field, data, valid):
        args = {field: data}
        args = convert_task_profile(args)
        if valid:
            ok_(field in args)
        else:
            ok_(field not in args)

    _single_test('birthday', '0000-02-30', False)
    _single_test('birthday', '9999-02-29', False)
    _single_test('gender', 'unexpected_gender', False)

    _single_test('birthday', '0000-02-29', True)
    _single_test('birthday', '1989-12-28', True)
    _single_test('gender', 'm', True)
