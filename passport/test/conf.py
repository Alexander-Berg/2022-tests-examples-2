# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from contextlib import contextmanager
from itertools import imap
from re import compile as re_compile

import mock
from passport.backend.core.db.query import split_query_and_callback
from passport.backend.social.common.application import ApplicationDatabaseSerializer
from passport.backend.social.common.db.schemas import (
    application_attribute_table,
    application_index_attribute_table,
    application_table,
)
from passport.backend.social.common.provider_settings import providers as provider_settings
from passport.backend.social.common.providers.Deezer import Deezer
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.providers.Kinopoisk import Kinopoisk
from passport.backend.social.common.providers.Lastfm import Lastfm
from passport.backend.social.common.providers.MailRu import MailRu
from passport.backend.social.common.providers.Microsoft import Microsoft
from passport.backend.social.common.providers.Mts import Mts
from passport.backend.social.common.providers.MtsBelarus import MtsBelarus
from passport.backend.social.common.providers.Odnoklassniki import Odnoklassniki
from passport.backend.social.common.providers.Twitter import Twitter
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yahoo import Yahoo
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.social_config import social_config as _social_config

from .consts import (
    APPLICATION_SECRET1,
    DEEZER_APPLICATION_ID1,
    DEEZER_APPLICATION_NAME1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    FACEBOOK_APPLICATION_ID1,
    FACEBOOK_APPLICATION_NAME1,
    GOOGLE_APPLICATION_ID1,
    GOOGLE_APPLICATION_NAME1,
    KINOPOISK_APPLICATION_ID1,
    KINOPOISK_APPLICATION_NAME1,
    MAIL_RU_APPLICATION_ID1,
    MAIL_RU_APPLICATION_ID2,
    MAIL_RU_APPLICATION_NAME1,
    MAIL_RU_APPLICATION_NAME2,
    MICROSOFT_APPLICATION_ID1,
    MICROSOFT_APPLICATION_NAME1,
    MTS_APPLICATION_ID1,
    MTS_APPLICATION_NAME1,
    MTS_BELARUS_APPLICATION_ID1,
    MTS_BELARUS_APPLICATION_NAME1,
    ODNOKLASSNIKI_APPLICATION_ID1,
    ODNOKLASSNIKI_APPLICATION_NAME1,
    TWITTER_APPLICATION_ID1,
    TWITTER_APPLICATION_NAME1,
    VKONTAKTE_APPLICATION_ID1,
    VKONTAKTE_APPLICATION_NAME1,
    YAHOO_APPLICATION_ID1,
    YAHOO_APPLICATION_NAME1,
    YANDEX_APPLICATION_ID1,
    YANDEX_APPLICATION_NAME1,
)


DEFAULT_PROVIDERS = [
    {
        'id': Deezer.id,
        'code': Deezer.code,
        'name': 'deezer',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'default': 'Deezer',
        },
    },
    {
        'id': Facebook.id,
        'code': Facebook.code,
        'name': 'facebook',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Лицокнига',
            'en': 'Facebook',
            'default': 'Facebook',
        },
    },
    {
        'id': Twitter.id,
        'code': Twitter.code,
        'name': 'twitter',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Щебетун',
            'en': 'Twitter',
            'default': 'Twitter',
        },
    },
    {
        'id': Mts.id,
        'code': Mts.code,
        'name': 'mts',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'МТС',
            'en': 'MTS',
            'default': 'МТС',
        },
    },
    {
        'id': MtsBelarus.id,
        'code': MtsBelarus.code,
        'name': 'mts_belarus',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'МТС',
            'en': 'MTS',
            'default': 'МТС',
        },
    },
    {
        'id': MailRu.id,
        'code': MailRu.code,
        'name': 'mailru',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Mail.ru',
            'en': 'Mail.ru',
            'default': 'Mail.ru',
        },
    },
    {
        'id': Google.id,
        'code': Google.code,
        'name': 'google',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Google',
            'en': 'Google',
            'default': 'Google',
        },
    },
    {
        'id': Microsoft.id,
        'code': Microsoft.code,
        'name': 'microsoft',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Микрософт',
            'en': 'Microsoft',
            'default': 'Microsoft',
        },
    },
    {
        'id': Vkontakte.id,
        'code': Vkontakte.code,
        'name': 'vkontakte',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'default': 'Vkontakte',
        },
    },
    {
        'id': Yahoo.id,
        'code': Yahoo.code,
        'name': 'yahoo',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Yahoo',
            'en': 'Yahoo',
            'default': 'Yahoo',
        },
    },
    {
        'id': Yandex.id,
        'code': Yandex.code,
        'name': 'yandex',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Яндекс',
            'en': 'Yandex',
            'default': 'Яндекс',
        },
    },
    {
        'id': Kinopoisk.id,
        'code': Kinopoisk.code,
        'name': 'kinopoisk',
        'timeout': 1,
        'retries': 1,
        'display_name': {
            'ru': 'Кинопоиск',
            'en': 'Kinopoisk',
            'default': 'Кинопоиск',
        },
    },
    {
        'id': Odnoklassniki.id,
        'code': Odnoklassniki.code,
        'name': 'odnoklassniki',
        'display_name': {
            'default': 'Одноклассники',
        },
    },
    {
        'id': Lastfm.id,
        'code': Lastfm.code,
        'name': 'lastfm',
        'display_name': {
            'default': 'LastFM',
        },
    },
]

DEFAULT_APPLICATIONS = [
    {
        'provider_id': Deezer.id,
        'application_id': DEEZER_APPLICATION_ID1,
        'application_name': DEEZER_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.net',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Facebook.id,
        'application_id': FACEBOOK_APPLICATION_ID1,
        'application_name': FACEBOOK_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': '.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Twitter.id,
        'application_id': TWITTER_APPLICATION_ID1,
        'application_name': TWITTER_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': '.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Mts.id,
        'application_id': MTS_APPLICATION_ID1,
        'application_name': MTS_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': MtsBelarus.id,
        'application_id': MTS_BELARUS_APPLICATION_ID1,
        'application_name': MTS_BELARUS_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.net',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': MailRu.id,
        'application_id': MAIL_RU_APPLICATION_ID1,
        'application_name': MAIL_RU_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': MailRu.id,
        'application_id': MAIL_RU_APPLICATION_ID2,
        'application_name': MAIL_RU_APPLICATION_NAME2,
        'provider_client_id': EXTERNAL_APPLICATION_ID2,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.ru',
        'engine_id': 'o2',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Google.id,
        'application_id': GOOGLE_APPLICATION_ID1,
        'application_name': GOOGLE_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Microsoft.id,
        'application_id': MICROSOFT_APPLICATION_ID1,
        'application_name': MICROSOFT_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.net',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Vkontakte.id,
        'application_id': VKONTAKTE_APPLICATION_ID1,
        'application_name': VKONTAKTE_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': 'social.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Yahoo.id,
        'application_id': YAHOO_APPLICATION_ID1,
        'application_name': YAHOO_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': '.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Yandex.id,
        'application_id': YANDEX_APPLICATION_ID1,
        'application_name': YANDEX_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': '.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Kinopoisk.id,
        'application_id': KINOPOISK_APPLICATION_ID1,
        'application_name': KINOPOISK_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': KINOPOISK_APPLICATION_NAME1,
        'secret': '',
        'domain': 'social.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
    {
        'provider_id': Odnoklassniki.id,
        'application_id': ODNOKLASSNIKI_APPLICATION_ID1,
        'application_name': ODNOKLASSNIKI_APPLICATION_NAME1,
        'default': '1',
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'secret': APPLICATION_SECRET1,
        'domain': '.yandex.ru',
        'request_from_intranet_allowed': '1',
    },
]


class KeyToAttrAdapter(object):
    def __init__(self, _dict):
        self._dict = _dict

    def __getitem__(self, key):
        return self._dict[key]

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def update(self, other):
        self._dict.update(other)

KA = KeyToAttrAdapter


DEFAULT_SOCIAL_CONFIG = dict(
    redis_task_expiration_time=10800,

    track_cookie_expiration_time=1200,
    track_cookie_secure_key='track_cookie_secure_key',

    connection_pool_limit=50,
    connection_pool_maxsize=100,
    connection_pool_timeout=1,

    useragent_default_timeout=1,
    useragent_default_retries=1,

    timeout=1,
    retries=1,

    oauth_scopes_required=['social:broker', 'yataxi:pay'],

    broker_stress_mode=False,

    broker_pool_recycle=600,

    allowed_retpath_schemes=map(
        re_compile,
        [
            '^yandex',
            r'^ru\.yandex\.',
            r'^com\.yandex\.',
        ],
    ),

    db_master_host='socialdb-master.yandex.net',
    db_master_database='socialdb',
    db_master_user='social_rw',
    db_master_password='db_master_password',
    db_master_port=3306,
    db_master_connect_timeout=1,
    db_master_read_timeout=1,
    db_master_write_timeout=1,
    db_master_reconnect_retries=1,
    db_master_pool_size=5,
    db_master_pool_timeout=1,

    db_slave_host='socialdb.yandex.net',
    db_slave_database='socialdb',
    db_slave_user='social_ro',
    db_slave_password='db_slave_password',
    db_slave_port=3306,
    db_slave_connect_timeout=1,
    db_slave_read_timeout=1,
    db_slave_write_timeout=1,
    db_slave_reconnect_retries=1,
    db_slave_pool_size=5,
    db_slave_pool_timeout=1,

    redis_pool_size=10000,
    redis_reconnect_retries=1,
    redis_reconnect_timeout=1,
    redis_connection_timeout=1,

    redis_master_host='socialdb-master.yandex.net',
    redis_master_port=6379,
    redis_master_password='r3d15p455w0rd',

    redis_slave_host='redis_master_host',
    redis_slave_port='redis_master_port',
    redis_slave_password='redis_master_password',

    blackbox_url='http://black.yandex.ru/blackbox',
    blackbox_timeout=1,
    blackbox_retries=1,

    ssl_certs_path='/etc/ssl/certs/ca-certificates.crt',

    api_tvm_keyring_config_name='2000382-social_api_production',
    api_tvm_cache_time=60,
    tvm_environment='production',

    proxy2_tvm_keyring_config_name='2000385-social_proxy2_production',
    proxy2_tvm_cache_time=60,

    broker_tvm_keyring_config_name='2000388-social_broker_production',
    broker_tvm_cache_time=60,

    counter_limit_for_process_request_by_consumer=dict(),
    consumer_translation_for_counters=dict(),

    kolmogor_url='https://kolmogor/',
    kolmogor_retries=1,
    kolmogor_timeout=1,

    zora_client_id='socialism',
    zora_url='http://zora/',
    zora_tvm_client_alias='zora',

    broker_retpath_grammars=[
        """
        domain = 'social.yandex.' yandex_tld
        path = '/broker2'
        """,

        """
        domain = 'passport.yandex.' yandex_tld |
            'passport-test.yandex.' yandex_tld
        path = '/auth/i-social__closer.html' |
            '/auth/social/callback'
        """,
    ],

    max_sql_in_function_values=5,

    social_broker_host='social.yandex.ru',
    yandex_oauth_authorize_url='https://oauth.yandex.ru/authorize',

    allowed_json_web_algorithms=frozenset(['RS256']),

    general_facebook_client_id=EXTERNAL_APPLICATION_ID1,
    not_yandex_facebook_client_ids=dict(toloka_fb_client_id='toloka'),

    time_zone='Europe/Moscow',

    environment_id=0,
    environment_from_id={
        0: 'production',
    },

    domain_to_redirect_url={
        '.yandex.net': 'https://social.yandex.net/broker/redirect',
        'social.yandex.net': 'https://social.yandex.net/broker/redirect',

        '.yandex.ru': 'https://social.yandex.ru/broker/redirect',
        'social.yandex.ru': 'https://social.yandex.ru/broker/redirect',

        '.kinopoisk.ru': 'https://www.kinopoisk.ru/social_redirect',
        'www.kinopoisk.ru': 'https://www.kinopoisk.ru/social_redirect',
    },
    social_broker_redirect_url_from_enviroment={
        'production': 'https://social.yandex.net/broker/redirect',
    },

    max_token_response_length=64000,
    find_token_by_value_hash=True,
)


DEFAULT_TVM_CREDENTIALS_CONFIG = {
    'passport': {
        'client_id': '1',
        'ticket': 'social_to_passport',
    },
    'zora': {
        'client_id': '2',
        'ticket': 'social_to_zora',
    },
    'blackbox': {
        'client_id': '3',
        'ticket': 'social_to_blackbox',
    },
}


class FakeSettings(object):
    def __init__(self, fake_db, providers=DEFAULT_PROVIDERS, applications=DEFAULT_APPLICATIONS,
                 social_config=DEFAULT_SOCIAL_CONFIG, in_context=False):
        self._fake_db = fake_db
        self._social_config = dict(DEFAULT_SOCIAL_CONFIG)
        self._social_config.update(social_config)
        self._social_config.update(
            dict(
                providers=providers,
                applications=applications,
                services=[],
            ),
        )

        self.__patches = [
            mock.patch.object(_social_config, 'init', side_effect=self._fake_init),
        ]
        if not in_context:
            self.__patches.extend([
                mock.patch.object(_social_config, '_settings', new=None),
                mock.patch.object(provider_settings, '_Providers__providers', new=None),
            ])

        self._provider_code_to_id = {p['code']: p['id'] for p in providers}

    def start(self):
        is_configured = _social_config.configured

        for patch in self.__patches:
            patch.start()

        if is_configured:
            # Т.к. приложение уже сконфигурировано, то подновим его настройки
            # on-line, не требуя переконфигурации.
            self._fake_init()
            provider_settings.init()

        return self

    def stop(self):
        for patch in reversed(self.__patches):
            patch.stop()

    def _fake_init(self):
        _social_config._settings = KA(self._social_config)

        with self._fake_db.no_recording() as db:
            db.execute(application_table.delete())
            db.execute(application_attribute_table.delete())
            db.execute(application_index_attribute_table.delete())
            apps = self._social_config.get('applications', [])
            for app in apps:
                self._serialize_app_to_db(db, app)

    def _serialize_app_to_db(self, db, app):
        s = ApplicationDatabaseSerializer()
        queries = s.serialize(None, app)
        for query, callback in imap(split_query_and_callback, queries):
            result = db.execute(query.to_query())
            if callback:
                callback(result)


@contextmanager
def settings_context(**kwargs):
    kwargs = dict(kwargs)
    kwargs.setdefault('in_context', True)
    fake_settings = FakeSettings(**kwargs).start()
    try:
        yield
    finally:
        fake_settings.stop()
