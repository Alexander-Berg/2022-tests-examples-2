# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.core.test.consts import TEST_TRACK_ID1
from passport.backend.core.test.time_utils.time_utils import TimeSpan

from .base_test_data import *


def setup_statbox_templates(statbox):
    statbox.bind_base(
        mode='social',
        consumer='dev',
    )
    statbox.bind_entry(
        'local_base',
        ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
    )
    statbox.bind_entry(
        'submitted',
        _inherit_from='local_base',
        action='submitted',
        type='social',
        provider=TEST_PROVIDER['code'],
        retpath=TEST_RETPATH,
        yandexuid=TEST_YANDEXUID_COOKIE,
        host=TEST_HOST,
        application=TEST_APPLICATION,
        broker_consumer=TEST_BROKER_CONSUMER,
        track_id=TEST_TRACK_ID1,
    )
    statbox.bind_entry(
        'account_modification',
        _exclude=['mode'],
        _inherit_from=['account_modification', 'local_base'],
    )
    statbox.bind_entry(
        'frodo_karma',
        _exclude=['mode'],
        _inherit_from=['frodo_karma', 'local_base'],
    )
    statbox.bind_entry(
        'subscriptions',
        _exclude=['mode'],
        _inherit_from=['subscriptions', 'local_base'],
        operation='added',
    )
    statbox.bind_entry(
        'auth',
        action='auth',
        uid=str(TEST_SOCIAL_UID),
        track_id=TEST_TRACK_ID1,
        profile_id=str(TEST_PROFILE_ID),
        provider=TEST_PROVIDER['name'],
        login=TEST_LOGIN,
        userid=TEST_USERID,
        ip=TEST_USER_IP,
    )
    statbox.bind_entry(
        'callback_begin',
        action='callback_begin',
        task_id=TEST_TASK_ID,
        track_id=TEST_TRACK_ID1,
        broker_status='ok',
    )
    statbox.bind_entry(
        'defined_validation_method',
        _exclude=['consumer'],
        action='defined_validation_method',
        mode='change_password_force',
        validation_method='captcha',
        uid=str(TEST_SOCIAL_UID),
    )
    statbox.bind_entry(
        'callback_end',
        action='callback_end',
        provider=TEST_PROVIDER['name'],
        application='google-oauth2',
        third_party_app='0',
        userid=TEST_USERID,
        track_id=TEST_TRACK_ID1,
    )
    statbox.bind_entry(
        'account_created',
        _inherit_from=['account_created', 'local_base'],
        is_voice_generated='0',
        captcha_generation_number='0',
        provider=TEST_PROVIDER['name'],
        login=TEST_GENERATED_LOGIN,
        karma='0',
        retpath=TEST_RETPATH,
        country='en',
    )
    statbox.bind_entry(
        'cookie_set',
        _inherit_from=['cookie_set', 'local_base'],
        _exclude=['consumer'],
        mode='any_auth',
        track_id=TEST_TRACK_ID1,
        yandexuid=TEST_YANDEXUID_COOKIE,
        ip_country='ru',
        retpath=TEST_RETPATH,
    )
    statbox.bind_entry(
        'multibrowser_set',
        _inherit_from='local_base',
        _exclude=['consumer'],
        uid=str(TEST_UID),
        mode='any_auth',
        action='multibrowser_update',
        old_multibrowser='0',
        new_multibrowser='1',
        yandexuid=TEST_YANDEXUID_COOKIE,
    )
    statbox.bind_entry(
        'antifraud_denied_social_auth',
        action='antifraud_denied_social_auth',
        track_id=TEST_TRACK_ID1,
        uid=str(TEST_SOCIAL_UID),
    )
    statbox.bind_entry(
        'user_notified_about_authentication',
        action='auth_notification',
        consumer='dev',
        counter_exceeded='0',
        email_sent='1',
        is_challenged='1',
        mode='social',
        track_id=TEST_TRACK_ID1,
        uid=str(TEST_SOCIAL_UID),
    )
    statbox.bind_entry(
        'profile_threshold_exceeded',
        action='profile_threshold_exceeded',
        consumer='dev',
        decision_source='ufo',
        email_sent='1',
        ip=str(TEST_USER_IP),
        is_mobile='0',
        is_password_change_required='0',
        kind='ufo',
        mode='any_auth',
        track_id=TEST_TRACK_ID1,
        uid=str(TEST_SOCIAL_UID),
        user_agent=TEST_USER_AGENT,
        was_online_sec_ago=TimeSpan(0),
    )
