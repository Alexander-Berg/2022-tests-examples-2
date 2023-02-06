# -*- coding: utf-8 -*-
from collections import namedtuple
import socket

import mock
from six import iteritems


DEFAULT_COUNTER_SETTINGS = {
    u'REGKARMA_BAD_COUNTER': (
        # prefix
        u'regkarma:bad',
        # (buckets count, bucket duration, limit)
        (24, 3600, 3),
    ),
    u'REGKARMA_GOOD_COUNTER': (
        u'regkarma:good',
        (24, 3600, 1),
    ),
    u'SOCIALREG_PER_IP_CAPTCHA_LIMIT_COUNTER': (
        'asr:ip',
        (6, 600, 200),
    ),
    u'SOCIALREG_PER_PROVIDER_CAPTCHA_LIMIT_COUNTER': (
        'asr:pr',
        (6, 600, 100000),
    ),

    u'UNCOMPLETEDREG_CALLS_CAPTCHA_LIMIT_COUNTER': (
        'reguncompleted:calls',
        (6, 600, 200),
    ),
    u'UNCOMPLETEDREG_PER_IP_CAPTCHA_LIMIT_COUNTER': (
        'reguncompleted:ip',
        (6, 600, 10),
    ),

    u'REGISTRATION_EMAIL_PER_EMAIL_LIMIT_COUNTER': (
        'registration_email:email',
        (24, 3600, 5),
    ),

    u'REGISTRATION_EMAIL_PER_IP_LIMIT_COUNTER': (
        'registration_email:ip:trusted',
        (24, 3600, 5),
    ),
    u'REGISTRATION_EMAIL_PER_UNTRUSTED_IP_LIMIT_COUNTER': (
        'registration_email:ip:untrusted',
        (24, 3600, 3),
    ),

    u'PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER': (
        'sms:ip',
        (24, 3600, 10),
    ),
    u'UNTRUSTED_PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER': (
        'untrusted:sms:ip',
        (24, 3600, 10),
    ),

    u'PHONE_CONFIRMATION_CALLS_PER_IP_LIMIT_COUNTER': (
        'calls:ip',
        (24, 3600, 10),
    ),
    u'UNTRUSTED_PHONE_CONFIRMATION_CALLS_PER_IP_LIMIT_COUNTER': (
        'untrusted:calls:ip',
        (24, 3600, 10),
    ),

    u'REGISTRATION_COMPLETED_WITH_SMS_PER_IP_LIMIT_COUNTER': (
        'registration:sms:ip',
        (24, 3600, 5),
    ),
    u'UNTRUSTED_REGISTRATION_COMPLETED_WITH_SMS_PER_IP_LIMIT_COUNTER': (
        'untrusted:registration:sms:ip',
        (24, 3600, 5),
    ),

    u'AUTH_FORWARDING_SMS_PER_IP_LIMIT_COUNTER': (
        'auth_forwarding_by_sms:ip',
        (24, 3600, 10),
    ),
    u'UNTRUSTED_AUTH_FORWARDING_SMS_PER_IP_LIMIT_COUNTER': (
        'untrusted:auth_forwarding_by_sms:ip',
        (24, 3600, 10),
    ),

    u'CHECK_ANSWER_PER_IP_LIMIT_COUNTER': (
        'account:check_answer:ip',
        (24, 3600, 500),
    ),
    u'CHECK_ANSWER_PER_UID_LIMIT_COUNTER': (
        'account:check_answer:uid',
        (24, 3600, 5),
    ),
    u'CHECK_ANSWER_PER_IP_AND_UID_LIMIT_COUNTER': (
        'account:check_answer:ip_uid',
        (24, 3600, 5),
    ),

    u'CHANGE_PASSWORD_PER_PHONE_NUMBER_LIMIT_COUNTER': (
        'change_password:phone_number',
        (24, 3600, 5),
    ),
    u'CHANGE_PASSWORD_PER_USER_IP_LIMIT_COUNTER': (
        'change_password:user_ip',
        (24, 3600, 15),
    ),


    u'RESTORE_SEMI_AUTO_COMPARE_PER_IP_LIMIT_COUNTER': (
        'restore:semi_auto:compare:ip',
        (24, 3600, 500),
    ),
    u'RESTORE_SEMI_AUTO_COMPARE_PER_UID_LIMIT_COUNTER': (
        'restore:semi_auto:compare:uid',
        (6, 600, 5),
    ),

    u'RESTORE_PER_IP_LIMIT_COUNTER': (
        'restore:compare:ip',
        (24, 3600, 10),
    ),

    u'LOGIN_RESTORE_PER_IP_LIMIT_COUNTER': (
        'login_restore:ip',
        (24, 3600, 20),
    ),

    u'LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER': (
        'login_restore:phone',
        (24, 3600, 5),
    ),

    u'SHORT_USERINFO_COUNTER': (
        'userinfo_short',
        (24, 3600, 10),
    ),

    u'YAPIC_UPLOAD_PER_IP_LIMIT_COUNTER': (
        'yapic:upload:ip',
        (6, 600, 50),
    ),
    u'YAPIC_UPLOAD_PER_UID_LIMIT_COUNTER': (
        'yapic:upload:ip_uid',
        (2, 60, 13),
    ),
    u'YAPIC_DELETE_PER_IP_LIMIT_COUNTER': (
        'yapic:delete:ip',
        (6, 600, 100),
    ),
    u'YAPIC_DELETE_PER_UID_LIMIT_COUNTER': (
        'yapic:delete:ip_uid',
        (2, 60, 26),
    ),

    u'PROFILE_FAILS_COUNTER': (
        'profile:failed',
        (10, 1, 10),
    ),

    u'AUTH_CHALLENGE_PER_IP_LIMIT_COUNTER': (
        'auth_challenge:ip',
        (24, 3600, 10),
    ),
    u'AUTH_EMAIL_RECENTLY_SENT_COUNTER': (
        'auth:mail_sent',
        (1, 300, 1),
    ),

    u'PASSMAN_RECOVERY_KEY_ADD_COUNTER': (
        'passman_recovery_key:added',
        (24, 3600, 10),
    ),

    u'VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER': (
        'email_validator:total_sent',
        (24, 3600, 25),
    ),

    u'VALIDATOR_EMAIL_SENT_PER_UID_COUNTER': (
        'email_validator:total_sent_per_uid',
        (24, 3600, 100),
    ),

    u'SMS_PER_PHONE_LIMIT_COUNTER': (
        'sms:phone',
        (24, 3600, 10),
    ),

    u'CALLS_PER_PHONE_LIMIT_COUNTER': (
        'calls:phone',
        (24, 3600, 5),
    ),

    u'BAD_RFC_OTP_COUNTER': (
        'rfc_otp:failed',
        (6, 600, 5),
    ),

    u'SMS_PER_PHONE_ON_REGISTRATION_LIMIT_COUNTER': (
        'registration:sms:phone',
        (24, 3600, 5),
    ),

    u'REGISTRATION_SMS_SENT_PER_IP_LIMIT_COUNTER': (
        'registration_sms_sent:sms:ip',
        (24, 3600, 15),
    ),

    u'SMS_PER_PHONISH_ON_REGISTRATION_LIMIT_COUNTER': (
        'registration:sms:phonish',
        (24, 3600, 10),
    ),
    u'REGISTRATION_KOLONKISH_PER_CREATOR_UID_LONG_TERM': (
        'registration_kolonkish:creator_uid:long',
        (24, 60, 10),
    ),
    u'REGISTRATION_KOLONKISH_PER_CREATOR_UID_SHORT_TERM': (
        'registration_kolonkish:creator_uid:short',
        (1, 60, 10),
    ),
    u'REGISTER_PHONISH_BY_PHONE_PER_CONSUMER_COUNTER': (
        'register:phonish:consumer',
        (60, 60, 5),
    ),
    u'REGISTER_MAILISH_PER_CONSUMER_COUNTER': (
        'register:mailish:consumer',
        (60, 60, 5),
    ),
    u'MIGRATE_MAILISH_PER_CONSUMER_COUNTER': (
        'migrate:mailish:consumer',
        (6, 10, 100),
    ),
    u'AUTH_MAGIC_LINK_EMAIL_SENT_PER_UID_COUNTER': (
        'auth_magic_link:uid',
        (1, 600, 10),
    ),
    u'AUTH_MAGIC_LINK_EMAIL_SENT_PER_IP_COUNTER': (
        'auth_magic_link:ip',
        (1, 600, 10),
    ),
    u'AUTH_MAGIC_LINK_EMAIL_SENT_PER_UNTRUSTED_IP_COUNTER': (
        'untrusted:auth_magic_link:ip',
        (1, 600, 3),
    ),
    u'QUESTION_CHANGE_EMAIL_NOTIFICATION_COUNTER': (
        'question_change:mail_sent',
        (1, 600, 10),
    ),
    u'DRIVE_CREATE_DEVICE_PUBLIC_KEY_RPD_COUNTER': ('drive_create_key', 4),
    u'DRIVE_CREATE_DEVICE_PUBLIC_KEY_RPS_COUNTER': ('drive_create_key_rps', 2),
    u'ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE': ('account_modification:%s:uid:%s', {
        'push:collector_add': 5,
    }),
    'EMAIL_CHECK_OWNERSHIP_SENT_COUNTER_1H': ('check_email_ownership:sent:1h:%s', 10),
    'EMAIL_CHECK_OWNERSHIP_SENT_COUNTER_24H': ('check_email_ownership:sent:24h:%s', 50),
    'YAKEY_2FA_PICTURES_SHOWN_COUNTER': ('2fa_pictures:shown:uid:%s', 5),
}

COUNTER_NAMES = {
    python_name: db_name
    for python_name, (db_name, _) in iteritems(DEFAULT_COUNTER_SETTINGS)
}

_host = namedtuple('host', 'name id dc')


def mock_hosts():
    return [_host(name=socket.getfqdn(), id=0x7F, dc='myt')]


def mock_redis_config(hosts=None):
    hosts = hosts or mock_hosts()
    return dict((host.id, {'master': {'host': '127.0.0.1', 'port': 6379, 'type': 'master'}}) for host in hosts)


def mock_counters(REGKARMA_BAD_ENABLED=True,
                  REGKARMA_GOOD_ENABLED=True,
                  COUNTERS_REDIS_MANAGERS={'myt': 0x7F},
                  DB_NAME_TO_COUNTER=None,
                  **kwargs):
    COUNTERS = DB_NAME_TO_COUNTER.copy() if DB_NAME_TO_COUNTER else {}

    for python_name in DEFAULT_COUNTER_SETTINGS:
        db_name, default_value = DEFAULT_COUNTER_SETTINGS[python_name]
        if db_name not in COUNTERS:
            COUNTERS[db_name] = kwargs.get(python_name, default_value)

    counter_settings = {}
    counter_settings.update(COUNTER_NAMES)
    counter_settings.update(dict(
        COUNTERS=COUNTERS,
        REGKARMA_BAD_ENABLED=REGKARMA_BAD_ENABLED,
        REGKARMA_GOOD_ENABLED=REGKARMA_GOOD_ENABLED,
        COUNTERS_REDIS_MANAGERS=COUNTERS_REDIS_MANAGERS,
    ))
    return counter_settings


def mock_env(cookies=None, user_ip='127.0.0.1', user_agent=None, host=None, accept_language=None):
    env = mock.Mock()
    env.user_ip = user_ip
    env.user_agent = user_agent
    env.host = host
    env.accept_language = accept_language

    env.cookies = cookies or {}

    return env


def mock_grants(consumer=None, grants=None, networks=None, client_id=None):
    if consumer is None:
        consumer = 'dev'

    if networks is None:
        networks = ['127.0.0.1']

    if grants is None:
        grants = {
            # гранты для новых ручек
            'karma': ['*'],
            'account': ['*'],
            'session': ['*'],
            'password': ['*'],
            'subscription': ['*'],
            'person': ['*'],
            'ignore_stoplist': ['*'],
            'captcha': ['*'],
            'cookies': ['*'],
            'control_questions': ['*'],
            'questions': ['*'],
            'country': ['*'],
            'timezone': ['*'],
            'gender': ['*'],
            'language': ['*'],
            'login': ['*'],
            'name': ['*'],
            'phone_number': ['*'],
            'retpath': ['*'],
            'statbox': ['*'],
            'track': ['*'],
            'phone_bundle': ['*'],
            'auth_password': ['*'],
            'auth_multi': ['*'],
            'auth_social': ['*'],
            'auth_oauth': ['*'],
            'auth_key': ['*'],
            'auth_by_token': ['*'],
            'auth_forwarding': ['*'],
            'auth_by_sms': ['*'],
            'restore': ['*'],
            'login_restore': ['*'],
            'internal': ['*'],
            'session_karma': ['*'],
            'otp': ['*'],
            'lastauth': ['*'],
            'social_profiles': ['*'],
            'security': ['*'],
            'allow_yakey_backup': ['*'],
            'billing': ['*'],
            'challenge': ['*'],
            'account_suggest': ['*'],
            'oauth_client': ['*'],
            'experiments': ['*'],
            'phonish': ['*'],
            'takeout': ['*'],
            # гранты для старых ручек
            'admchangereg': ['*'],
        }

    if client_id is None:
        client = {}
    else:
        client = {'client_id': client_id}

    return {consumer: {'grants': grants, 'networks': networks, 'client': client}}
