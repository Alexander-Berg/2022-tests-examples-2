# -*- coding: utf-8 -*-
import json

from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.core.builders.social_api.faker.social_api import EXISTING_TASK_ID
from passport.backend.core.test.consts import TEST_RETPATH1


TEST_USER_LOGIN = 'userlogin'
TEST_OTHER_LOGIN = 'other_login'
TEST_OTHER_UID = '1234'
TEST_SOCIAL_UID = 100000000
TEST_SOCIAL_OTHER_UID = 100000002
TEST_SOCIAL_USERID = 100000000
TEST_HOST = 'yandex.ru'
TEST_USER_IP = '176.213.140.30'
TEST_USER_AGENT = 'curl'

TEST_TASK_ID = EXISTING_TASK_ID
TEST_RETPATH = TEST_RETPATH1
TEST_RETPATH_NONSTANDARD_SCHEME = 'yandexmail://blah'
TEST_AUTH_ID = '123:1422501443:126'

TEST_ORIGIN = 'origin'
TEST_PROVIDER = {'code': 'gg', 'name': 'google', 'id': 5}
TEST_APPLICATION = 'social-app'
TEST_BROKER_CONSUMER = 'broker_consumer'
TEST_PROVIDER_JSON = json.dumps(TEST_PROVIDER)
TEST_CONSUMER = 'passport'
TEST_DISPLAY_NAME = {
    'name': 'Firstname Lastname',
    'social': {
        'provider': TEST_PROVIDER['code'],
        # Отличается от TEST_PROFILE_ID, чтобы видеть, что именно использовалось при создании куки.
        'profile_id': 123456,
    },
}

TEST_MAIL_SUBSCRIPTION_SERVICES = [
    {
        'id': 1,
        'origin_prefixes': [TEST_ORIGIN],
        'app_ids': [],
        'slug': None,
        'external_list_ids': [],
    },
    {
        'id': 2,
        'origin_prefixes': [],
        'app_ids': [],
        'slug': None,
        'external_list_ids': [],
    },
]

TEST_AVATAR_URL = 'https://lh3.googleusercontent.com/-XdUIqdskCWA/AAAAAAAAAAI/AAAAAAAAAAA/2252rscbv5M/photo.jpg'

TEST_GENERATED_LOGIN = 'uid-11111'
TEST_USERID = '57575757575'
TEST_PROFILE_ID = 123456789

TEST_EMAIL_VALIDATOR_EMAIL = 'user@example.com'

TEST_ACCESS_TOKEN = 'a68d97976a66444496148b694802b009'
TEST_PROVIDER_TOKEN = 'sdflkjdslkgjldskgjl333rf3f'
TEST_SCOPE = 'scope1,scope2'

TEST_CODE_CHALLENGE = 'challenge'
TEST_CODE_CHALLENGE_METHOD = 'S256'
TEST_AUTHORIZATION_CODE = '12345'
