# -*- coding: utf-8 -*-

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.social_api import (
    SocialApi,
    SocialApiRequestError,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    FakeSocialApi,
    get_bind_response,
    get_delete_task_response,
    get_ok_response,
    get_profile_info,
    get_profiles_full_response,
    get_profiles_no_profiles,
    get_profiles_response,
    get_subscription_info,
    profile_item,
    profile_not_found_error,
    PROVIDERS_MAP,
    social_api_person_item,
    subscription_not_found_error,
    task_data_response,
    token_item,
)
from passport.backend.core.test.consts import TEST_CONSUMER1
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


@with_settings(
    SOCIAL_API_URL='http://none.yandex.ru/api/',
    SOCIAL_API_CONSUMER=TEST_CONSUMER1,
    SOCIAL_API_RETRIES=2,
    SOCIAL_API_TIMEOUT=1,
)
class FakeSocialApiTestCase(PassportTestCase):
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
        self.fake_social_api = FakeSocialApi()
        self.fake_social_api.start()
        self.task_id = '1234567890fedcba'

    def tearDown(self):
        self.fake_social_api.stop()
        del self.fake_social_api
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_set_register_response_value(self):
        ok_(not self.fake_social_api._mock.request.called)
        self.fake_social_api.set_social_api_response_value(
            task_data_response(task_id=self.task_id),
        )
        result = SocialApi().get_task_data(self.task_id)
        ok_(self.fake_social_api._mock.request.called)
        eq_(result['task_id'], self.task_id)

    def test_set_response_side_effect(self):
        ok_(not self.fake_social_api._mock.request.called)
        self.fake_social_api.set_social_api_response_side_effect(
            SocialApiRequestError('fake_message'),
        )
        with assert_raises(SocialApiRequestError):
            SocialApi().get_task_data(self.task_id)
        ok_(self.fake_social_api._mock.request.called)

    def test_fake_get_profiles_full_response(self):
        response = get_profiles_full_response()
        ok_('profiles' in response)

    def test_fake_get_profiles_no_profiles(self):
        response = get_profiles_no_profiles()
        ok_('profiles' in response)

    def test_fake_get_profile_info(self):
        response = get_profile_info(1, 1)
        ok_('profile' in response)

    def test_fake_get_subscription_info(self):
        response = get_subscription_info(1, 1)
        ok_('subscription' in response)

    def test_fake_profile_not_found_error(self):
        response = profile_not_found_error()
        ok_('error' in response)

    def test_fake_subscription_not_found_error(self):
        response = subscription_not_found_error()
        ok_('error' in response)

    def test_fake_get_bind_response(self):
        response = get_bind_response()
        eq_(
            response,
            {
                'status': 'ok',
                'uid': 100500,
                'profile_id': 123456789,
            },
        )

    def test_fake_get_ok_response(self):
        response = get_ok_response()
        eq_(
            response,
            {
                'status': 'ok',
            },
        )

    def test_fake_get_profiles_with_provider(self):
        self.fake_social_api.set_social_api_response_value(
            dict(profiles=[profile_item(provider='google', expand_provider=True)]),
        )
        response = SocialApi().get_profiles_by_uid(123, expand_provider=True)

        ok_(isinstance(response[0]['provider'], dict))
        eq_(response[0]['provider'], PROVIDERS_MAP['google'])

    def test_fake_profiles_with_person_response(self):
        self.fake_social_api.set_social_api_response_value(
            dict(profiles=[profile_item(person=social_api_person_item())]),
        )
        response = SocialApi().get_profiles_by_uid(123, person=True)

        ok_('person' in response[0])
        eq_(response[0]['person'], social_api_person_item())

    def test_fake_profiles_with_tokens_response(self):
        self.fake_social_api.set_social_api_response_value(
            dict(profiles=[profile_item(tokens=[token_item()])]),
        )
        response = SocialApi().get_profiles_by_uid(123, tokens=True)

        ok_('tokens' in response[0])
        eq_(response[0]['tokens'][0], token_item())

    def test_fake_profiles_with_subscriptions_response(self):
        self.fake_social_api.set_social_api_response_value(
            dict(profiles=[profile_item(subscriptions=[2, 4, 16])]),
        )
        response = SocialApi().get_profiles_by_uid(123, subscriptions=True)

        ok_('subscriptions' in response[0])
        eq_(
            response[0]['subscriptions'],
            [{'sid': 2}, {'sid': 4}, {'sid': 16}],
        )


class TestTaskDataResponse(PassportTestCase):
    def test_ok(self):
        response = task_data_response()
        ok_('profile' in response)

    def test_with_business(self):
        response = task_data_response(with_business=True)
        ok_('profile' in response)
        ok_('business' in response['profile'])
        ok_(response['profile']['business'].keys(), ['id', 'token'])

    def test_none_values(self):
        response = task_data_response(username=None)
        ok_('username' not in response['profile'])

    def test_related_yandex_client(self):
        response = task_data_response(
            related_yandex_client_id='client_id',
            related_yandex_client_secret='client_secret',
        )

        app_attrs = response['token']['application_attributes']
        eq_(app_attrs['related_yandex_client_id'], 'client_id')
        eq_(app_attrs['related_yandex_client_secret'], 'client_secret')


class TestGetProfilesResponse(PassportTestCase):
    def test_default(self):
        response = get_profiles_response()
        eq_(len(response['profiles']), 3)

    def test_none(self):
        response = get_profiles_response(None)
        eq_(response['profiles'], [])


class TestDeleteTaskResponse(PassportTestCase):
    def test_ok(self):
        eq_(
            get_delete_task_response(),
            dict(
                status='ok',
                deleted=True,
            ),
        )
