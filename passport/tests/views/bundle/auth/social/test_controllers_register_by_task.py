# -*- coding: utf-8 -*-

import json

from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    get_bind_response,
    get_delete_task_response,
    profile_item,
    task_not_found_error,
)
from passport.backend.core.models.phones.faker import (
    assert_no_phone_in_db,
    assert_simple_phone_bound,
    build_phone_bound,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts

from .base_test_data import (
    TEST_CONSUMER_IP1,
    TEST_PHONE_ID,
    TEST_PHONE_NUMBER,
    TEST_SOCIAL_ALIAS,
    TEST_SOCIAL_UID,
)
from .test_base import (
    build_headers,
    EXISTING_TASK_ID,
)
from .test_controllers_register import BaseAuthSocialRegister


def get_mts_task_id_response(task_id=EXISTING_TASK_ID):
    response = {
        'requested_scope': 'user_birthday,email',
        'retpath': 'https://passportdev.yandex.ru/callback?consumer=dev',
        'yandexuid': '1272660251379517491',
        'final_timestamp': '1380284913.23',
        'consumer': 'dev',
        'frontend_url': 'https://socialdev-1.yandex.ru/broker2/',
        'task_id': task_id,
        'created': '1380284907.99',
        'access_token': {
            'application': 'mts',
            'expires': 1385454509.0,
            'value': 'abcdef87654321',
        },
        'profile': {
            'provider': {'code': 'mt', 'name': 'mts', 'id': 12},
            'username': 'some.user',
            'city': None,
            'firstname': 'Some',
            'lastname': 'User',
            'userid': '1526553000',
            'birthday': '1963-12-28',
            'gender': 'm',
        },
        'tld': 'ru',
        'scope': '[]',
    }
    return response


@with_settings_hosts(
    AUTH_ALLOWED_PROVIDERS=['fb'],
    REGISTER_BY_TASK_PROVIDERS=['mt', 'mr'],
    SOCIAL_TRUSTED_SIMPLE_PHONE=['mt'],
    OAUTH_APPLICATIONS_FOR_MUSIC={
        'mt': {
            'client_id': 'mts_client_id',
            'client_secret': 'mts_client_secret',
        },
        'mr': {
            'client_id': 'mail_ru_client_id',
            'client_secret': 'mail_ru_client_secret',
        },
    },
)
class TestAuthSocialRegisterByTask(BaseAuthSocialRegister):
    def setUp(self):
        super(TestAuthSocialRegisterByTask, self).setUp()

        self.env.social_api.set_response_value(
            'get_task_data',
            json.dumps(get_mts_task_id_response()),
        )
        self.env.social_api.set_response_value(
            'get_profiles',
            json.dumps({'profiles': []}),
        )
        self.env.social_api.set_response_value(
            'bind_task_profile',
            json.dumps(get_bind_response()),
        )
        self.env.social_api.set_response_value(
            'delete_task',
            json.dumps(get_delete_task_response()),
        )

    def setup_grants(self, **kwargs):
        self.env.grants.set_grants_return_value(
            {
                'dev': {
                    'grants': {'auth_social': ['register_by_task_id']},
                    'networks': [TEST_CONSUMER_IP1],
                },
            },
        )

    def auth_social_create_account_request(self, data=None, headers=None):
        return self.env.client.post(
            '/1/bundle/auth/social/register_by_task/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        return merge_dicts({'task_id': EXISTING_TASK_ID}, kwargs)

    def test_ok(self):
        rv = self.auth_social_create_account_request(data=self.query_params(), headers=build_headers())

        self.assert_ok_response(rv, check_all=False)

    def test_error_invalid_provider(self):
        """
        Принимаем только провайдеров из REGISTER_BY_TASK_PROVIDERS
        """
        task_data = get_mts_task_id_response()
        task_data['profile']['provider'] = {'code': 'fb', 'name': 'facebook', 'id': 2}
        self.env.social_api.set_response_value(
            'get_task_data',
            json.dumps(task_data),
        )

        rv = self.auth_social_create_account_request(data=self.query_params(), headers=build_headers())

        self.assert_error_response(
            rv,
            ['provider.invalid'],
            profile=task_data['profile'],
            provider=task_data['profile']['provider'],
        )

    def test_not_yandex_host(self):
        """
        Т.к. ручка не выписывает и не проверяет куки, то HOST можно не
        проврять.
        Кроме того у домена music.mts.ru с этим проблемы, т.к. это не домен
        Яндекса.
        """
        rv = self.auth_social_create_account_request(
            data=self.query_params(),
            headers=build_headers(host='music.mts.ru'),
        )

        self.assert_ok_response(rv, check_all=False)

    def test_bind_simple_phone__to_new_account(self):
        task_id_response = get_mts_task_id_response()
        task_id_response['profile']['phone'] = TEST_PHONE_NUMBER.e164
        self.env.social_api.set_response_value(
            'get_task_data',
            json.dumps(task_id_response),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        rv = self.auth_social_create_account_request(
            data=self.query_params(),
            headers=build_headers(),
        )

        self.assert_ok_response(rv, check_all=False)
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=1,
            phone_attributes={'id': 1, 'number': TEST_PHONE_NUMBER.e164},
        )

    def test_bind_simple_phone__to_existent_account(self):
        task_id_response = get_mts_task_id_response()
        task_id_response['profile']['phone'] = TEST_PHONE_NUMBER.e164
        self.env.social_api.set_response_value(
            'get_task_data',
            json.dumps(task_id_response),
        )

        response = {'profiles': [profile_item(uid=TEST_SOCIAL_UID)]}
        self.env.social_api.set_response_value(
            'get_profiles',
            json.dumps(response),
        )

        response = blackbox_userinfo_response(
            uid=TEST_SOCIAL_UID,
            login=TEST_SOCIAL_ALIAS,
            aliases={'social': TEST_SOCIAL_ALIAS},
        )
        self.env.blackbox.set_response_value('userinfo', response)
        self.env.db.serialize(response)

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        rv = self.auth_social_create_account_request(
            data=self.query_params(),
            headers=build_headers(),
        )

        self.assert_ok_response(rv, check_all=False)
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_SOCIAL_UID,
            phone_attributes={'id': 1, 'number': TEST_PHONE_NUMBER.e164},
        )

        self._assert_phones_requested_from_blackbox()

    def test_dont_bind_simple_phone__untrusted_provider(self):
        task_id_response = get_mts_task_id_response()
        task_id_response['profile']['phone'] = TEST_PHONE_NUMBER.e164
        task_id_response['profile']['provider'] = {
            'code': 'mr',
            'name': 'mailru',
            'id': 13,
        }
        self.env.social_api.set_response_value(
            'get_task_data',
            json.dumps(task_id_response),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        rv = self.auth_social_create_account_request(
            data=self.query_params(),
            headers=build_headers(),
        )

        self.assert_ok_response(rv, check_all=False)
        assert_no_phone_in_db(
            db_faker=self.env.db,
            uid=1,
            phone_id=1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )

    def test_simple_phone_already_bound(self):
        task_id_response = get_mts_task_id_response()
        task_id_response['profile']['phone'] = TEST_PHONE_NUMBER.e164
        self.env.social_api.set_response_value(
            'get_task_data',
            json.dumps(task_id_response),
        )

        response = {'profiles': [profile_item(uid=TEST_SOCIAL_UID)]}
        self.env.social_api.set_response_value(
            'get_profiles',
            json.dumps(response),
        )

        response = blackbox_userinfo_response(
            uid=TEST_SOCIAL_UID,
            login=TEST_SOCIAL_ALIAS,
            aliases={'social': TEST_SOCIAL_ALIAS},
            **build_phone_bound(TEST_PHONE_ID, TEST_PHONE_NUMBER.e164)
        )
        self.env.blackbox.set_response_value('userinfo', response)
        self.env.db.serialize(response)

        rv = self.auth_social_create_account_request(
            data=self.query_params(),
            headers=build_headers(),
        )

        self.assert_ok_response(rv, check_all=False)
        assert_simple_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_SOCIAL_UID,
            phone_attributes={'id': TEST_PHONE_ID},
        )

        self._assert_phones_requested_from_blackbox()

    def test_task_not_found(self):
        self.env.social_api.set_response_value(
            'get_task_data',
            json.dumps(task_not_found_error()),
        )

        rv = self.auth_social_create_account_request(
            data=self.query_params(),
            headers=build_headers(),
        )

        self.assert_error_response(rv, ['task.not_found'])

    def test_task_not_found_race(self):
        # Когда читали таск в первый раз, он ещё был, но когда стали создавать
        # профиль, таска не оказалась.
        self.env.social_api.set_response_side_effect('bind_task_profile', [json.dumps(task_not_found_error())])

        rv = self.auth_social_create_account_request(data=self.query_params(), headers=build_headers())

        self.assert_error_response(rv, ['task.not_found'], check_content=False)

    def _assert_phones_requested_from_blackbox(self):
        userinfo_request = self.env.blackbox.requests[0]
        userinfo_request.assert_post_data_contains({
            'method': 'userinfo',
            'aliases': 'all_with_hidden',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        userinfo_request.assert_contains_attributes({
            'account.2fa_on',
            'phones.secure',
            'phones.default',
        })
