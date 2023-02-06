# -*- coding: utf-8 -*-

import base64
from contextlib import contextmanager
from email import message_from_string
from email.header import decode_header
import json
import re
import time
import uuid

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.api.templatetags import (
    span,
    T,
    yandex_login,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_data_equals
from passport.backend.core.builders.clean_web_api.clean_web_api import BaseCleanWebError
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import (
    clean_web_api_response_bad_verdicts,
    clean_web_api_simple_response,
)
from passport.backend.core.builders.tensornet.faker.tensornet import tensornet_eval_response
from passport.backend.core.builders.ufo_api.faker import ufo_api_profile_response
from passport.backend.core.conf import settings
from passport.backend.core.env_profile.helpers import make_profile_from_raw_data
from passport.backend.core.env_profile.profiles import UfoProfile
from passport.backend.core.geobase.faker.fake_geobase import FakeRegion
from passport.backend.core.mailer.faker.mail_utils import (
    create_native_email,
    create_validated_external_email,
)
from passport.backend.core.test.test_utils.utils import (
    AnyMatcher,
    check_data_contains_params,
    pseudo_diff,
)
from passport.backend.core.types.login.login import masked_login
from passport.backend.core.types.phone_number.phone_number import mask_phone_number
from passport.backend.utils.string import smart_text
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)
import six


_JINJA_SUBST_FMT = re.compile(r'%\(([^)]+)\)s')
TEST_NOW = 1645513170


class AccountHistoryTestMixin(object):
    def _assert_parsed_events(self, event_type, actions):
        parsed_events = self.env.event_logger.parse_events()
        eq_(len(parsed_events), 1)
        parsed_event = parsed_events[0]
        eq_(parsed_event.event_type, event_type)
        eq_(parsed_event.actions, actions)

    def assert_account_history_parses_phone_bind(self, phone_number):
        self._assert_parsed_events(
            'phone_bind',
            [{
                'type': 'phone_bind',
                'phone_bind': mask_phone_number(phone_number.international),
            }],
        )

    def assert_account_history_parses_secure_phone_set(self, phone_number):
        self._assert_parsed_events(
            'secure_phone_set',
            [{
                'type': 'secure_phone_set',
                'phone_set': mask_phone_number(phone_number.international),
            }],
        )

    def assert_account_history_parses_secure_phone_replace(self, phone_number_old, phone_number_new, quarantine=None):
        actions = [{
            'type': 'secure_phone_replace',
            'phone_set': mask_phone_number(phone_number_new.international),
            'phone_unset': mask_phone_number(phone_number_old.international),
        }]
        if quarantine is not None:
            actions[0]['delayed_until'] = quarantine
        self._assert_parsed_events('secure_phone_replace', actions)


class OAuthTestMixin(object):
    def assert_oauth_call_args(self, method, params, callnum):
        """
        Проверяем, что OAuth вызван с нужным нам методом и параметрами.
        """
        assert_builder_data_equals(
            self.env.oauth,
            params,
            callnum=callnum,
        )

    def assert_oauth_not_called(self):
        eq_(self.env.oauth._mock.call_count, 0)


class EmailTestToolkit(object):
    def __init__(self, mailer_faker):
        self._mailer_faker = mailer_faker

    def create_native_email(self, *args, **kwargs):
        return create_native_email(*args, **kwargs)

    def create_validated_external_email(self, *args, **kwargs):
        return create_validated_external_email(*args, **kwargs)

    def check_email_body(
        self,
        # Справочник с переводами
        translations,
        # Словарь, где ключи это идентификаторы переводов, а значения это
        # справочник, из которого будут подставляться значения в соотвествующий
        # перевод
        keys_to_check,
        # Проверяемое тело письма
        body,
        recipients,
        # Список слов, которые должны всчтреться в письме
        words=None,
    ):
        if not isinstance(body, six.text_type):
            body = body.decode('utf-8')

        for key, context in keys_to_check.items():
            if not isinstance(key, six.text_type):
                # Ключи в translations хранятся в unicode
                key = key.decode('utf-8')
            ok_(key in translations, 'Translation not found: %s' % key)
            translation = translations[key]

            translation = self._jinja_to_passport_format(translation)
            translation = T(context, translation)

            ok_(
                translation in body,
                u'\nRecipients: %s\n\nKey: %s\n\nValue: %s\n\nBody: %s\n' % (
                    recipients, key, translation, body,
                ),
            )

        for word in words or list():
            if not isinstance(word, six.text_type):
                word = word.decode('utf-8')
            assert word in body, u'\nRecipients: %s\n\nValue: %s\n\nBody: %s\n' % (
                recipients, word, body,
            )

    def assert_emails_sent(self, emails):
        eq_(self._mailer_faker.message_count, len(emails))

        for i in range(self._mailer_faker.message_count):
            # Для assert'ов, которые сами умеют проверять высылалось письмо или
            # нет.
            if callable(emails[i]):
                emails[i]()
                continue

            raw_message = self._mailer_faker.get_message_content(message_index=i)
            message = message_from_string(smart_text(raw_message))
            message_body = base64.b64decode(message.get_payload())
            message_recipients = [address for address, _ in decode_header(message['To'])]
            message_subject = smart_text(decode_header(message['Subject'])[0][0])

            language = emails[i]['language']
            translations = settings.translations.NOTIFICATIONS[language]
            email_info = emails[i]
            eq_(message_recipients, email_info['addresses'])

            expected_message_subject = T(email_info.get('context', {}), translations[email_info['subject']])
            assert message_subject == expected_message_subject, '%s (index=%s)' % (
                pseudo_diff(message_subject, expected_message_subject),
                i,
            )

            if 'tanker_keys' in email_info:
                self.check_email_body(
                    translations,
                    email_info['tanker_keys'],
                    message_body,
                    message_recipients,
                    email_info.get('body_words'),
                )
            else:
                eq_(email_info['message_body'], message_body)

    def assert_email_sent(
        self,
        language,
        email_address,
        # Идентификатор перевода, который будет использоваться в теме
        subject,
        # Справочник из которого будут подставляться значения в переводы
        context=None,
        # Список идентификаторов тех переводов, которые нужно проверить
        tanker_keys=None,
        # Список слов, которые должны всчтреться в теле письма
        body_words=None,
    ):
        context = context or dict()
        tanker_keys = tanker_keys or dict()
        phrases = settings.translations.NOTIFICATIONS[language]

        user_messages = []
        for message in self._mailer_faker.messages:
            if ('', email_address) in message.recipients:
                user_messages.append(message)

        ok_(user_messages, 'No messages sent to ' + email_address)

        subject = T(context, self._jinja_to_passport_format(phrases[subject]))
        subject_messages = [m for m in user_messages if m.subject == subject]

        user_subjects = ', '.join([m.subject for m in user_messages])
        ok_(subject_messages, 'No messages found with subject "%s": %s' % (subject, user_subjects))

        eq_(len(subject_messages), 1, 'Duplicate messages found: %s' % subject_messages)
        message = subject_messages[0]

        tanker_keys_in_context = {key: context for key in tanker_keys}

        self.check_email_body(
            phrases,
            tanker_keys_in_context,
            message.body,
            [email_address],
            body_words,
        )

    def assert_no_emails_sent(self):
        eq_(self._mailer_faker.message_count, 0)

    def get_portal_login_markup(self, login):
        return span(yandex_login(login), 'font-weight: bold; word-break: break-all;')

    def _jinja_to_passport_format(self, s):
        return _JINJA_SUBST_FMT.sub(r'%\1%', s)


class EmailTestMixin(object):
    def create_native_email(self, *args, **kwargs):
        return self.env.email_toolkit.create_native_email(*args, **kwargs)

    def create_validated_external_email(self, *args, **kwargs):
        return self.env.email_toolkit.create_validated_external_email(*args, **kwargs)

    def check_email_body(self, *args, **kwargs):
        return self.env.email_toolkit.check_email_body(*args, **kwargs)

    def assert_emails_sent(self, *args, **kwargs):
        return self.env.email_toolkit.assert_emails_sent(*args, **kwargs)

    def assert_no_emails_sent(self, *args, **kwargs):
        return self.env.email_toolkit.assert_no_emails_sent(*args, **kwargs)

    def get_portal_login_markup(self, *args, **kwargs):
        return self.env.email_toolkit.get_portal_login_markup(*args, **kwargs)


class ProfileTestMixin(object):
    """
    Общий код для тестирования вещей, связанных с профилем пользователя
    """
    def setup_profile_patches(self):
        # Патчи для отслеживания значений при создании профиля для текущего окружения
        self.new_uuid1 = uuid.uuid1()
        self.new_uuid1_patch = mock.patch('passport.backend.core.env_profile.profile.uuid.uuid1', lambda: self.new_uuid1)
        self.new_time = time.time()
        self.new_time_patch = mock.patch('passport.backend.core.env_profile.profile.time', lambda: self.new_time)
        self.new_uuid1_patch.start()
        self.new_time_patch.start()

    def teardown_profile_patches(self):
        self.new_time_patch.stop()
        self.new_uuid1_patch.stop()
        del self.new_time_patch
        del self.new_uuid1_patch

    def setup_profile_responses(self, ufo_items=None, estimate=0.1):
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(items=ufo_items),
            ),
        )
        self.env.tensornet.set_tensornet_response_value(tensornet_eval_response(estimate))

    def assert_profile_written_to_auth_challenge_log(self, profile=None, uid=1, comment='-'):
        if profile is None:
            profile = self.make_user_profile()
        profile_pb2_base64 = '-'
        self.check_auth_challenge_log_entry(
            version='1',
            action='updated',
            uid=str(uid),
            env_profile_id=str(uuid.UUID(bytes=profile.timeuuid)),
            env_profile_pb2_base64=profile_pb2_base64,
            env_json=profile.raw_env,
            comment=comment,
        )

    def assert_ufo_api_not_called(self):
        eq_(len(self.env.ufo_api.requests), 0)

    def assert_ufo_api_called(self, call_count=1, url='http://localhost/1/profile/?uid=1'):
        eq_(len(self.env.ufo_api.requests), call_count)
        request = self.env.ufo_api.requests[0]
        request.assert_properties_equal(url=url)

    def check_auth_challenge_log_entry(self, **kwargs):
        eq_(self.env.auth_challenge_handle_mock.call_count, 1)
        log_entry = self.env.auth_challenge_handle_mock.call_args_list[0][0][0]

        for field, value in sorted(kwargs.items(), key=lambda item: item[0] == 'env_profile_pb2_base64'):
            actual = self._get_log_field(field, log_type='auth_challenge', log_msg=log_entry)
            if field == 'env_json':
                actual = json.loads(actual)
            eq_(
                actual,
                value,
                (field, actual, value),
            )

    def make_existing_fresh_profile(self, ufo_fresh_item):
        """
        Создает fresh-профиль на основе данных записи, прочитанной из UfoApi.
        """
        ufo_profile = UfoProfile(profile_items=[ufo_fresh_item])
        return next(ufo_profile.fresh_profiles)

    def make_user_profile(self, raw_env=None, **kwargs):
        """
        Создает микропрофиль текущего пользователя.
        """
        raw_env = raw_env.copy() if raw_env else {'ip': '3.3.3.3', 'yandexuid': None, 'user_agent_info': {}}
        raw_env.update(**kwargs)
        return make_profile_from_raw_data(
            timeuuid=self.new_uuid1.bytes,
            timestamp=int(self.new_time),
            **raw_env
        )


def make_clean_web_test_mixin(
    base_test_case_name,
    fields,
    statbox_action='account_created',
    statbox_filter=None,
    is_bundle=True,
    has_force_parameter=True,
):
    if statbox_filter is None:
        if statbox_action is not None:
            statbox_filter = {
                'action': statbox_action,
            }

    class CleanWebTestSuccessfulError(Exception):
        pass

    if 'firstname' in fields and 'lastname' in fields:
        fields.insert(fields.index('lastname') + 1, 'fullname')

    field_to_cw_field = {
        'firstname': 'first_name',
        'lastname': 'last_name',
        'fullname': 'full_name',
        'display_name': 'display_name',
        'public_id': 'public_id',
    }

    bad_parameters = [
        ([field_to_cw_field[f] for f in fields], fields[:]),
    ]
    if 'display_name' in fields:
        bad_parameters.append(([field_to_cw_field['display_name']], ['display_name']))
    if 'fullname' in fields:
        bad_parameters.append(([field_to_cw_field['fullname']], ['fullname']))

    @contextmanager
    def enable_clean_web():
        # TODO переписать это, когда with_settings научится наследовать предыдущие замоканные сеттинги
        from passport.backend.core.conf import settings
        assert settings.CLEAN_WEB_API_ENABLED is False
        settings.CLEAN_WEB_API_ENABLED = True
        settings.CLEAN_WEB_API_URL = 'http://localhost/'
        settings.CLEAN_WEB_API_TIMEOUT = 1
        settings.CLEAN_WEB_API_RETRIES = 2
        try:
            yield
        finally:
            settings.CLEAN_WEB_API_ENABLED = False

    def is_good_entry(entry):
        for k in statbox_filter:
            if k not in entry:
                return False
            if entry[k] != statbox_filter[k]:
                return False
        return True

    def make_statbox_faker_mock(self, clean_web_response):
        assert_equals = self.env.statbox.assert_equals

        def statbox_faker_mock(entries):
            entries = [
                dict(
                    e,
                    clean_web_check_fields=','.join(fields),
                    clean_web_response=','.join(sorted(clean_web_response)) if type(clean_web_response) == list else str(clean_web_response),
                )
                if is_good_entry(e) else e for e in entries
            ]
            assert_equals(entries)

        return statbox_faker_mock

    def check_statbox(self, clean_web_response):
        if statbox_filter is None:
            eq_(self.env.statbox.write_handler_mock._mock_call_args_list, [])
            return
        expected = self.env.statbox.entry(
            'base',
            action='clean_web_check_failed',
            clean_web_check_fields=','.join(fields),
            clean_web_response=','.join(sorted(clean_web_response)) if type(clean_web_response) == list else str(clean_web_response),
        )
        for tag in self.env.statbox.entry_templates:
            entry = self.env.statbox.entry(tag)
            if is_good_entry(entry):
                for field in ['track_id']:
                    if field in entry:
                        expected[field] = entry[field]

        actual = self.env.statbox._parse_lines(self.env.statbox.write_handler_mock._mock_call_args_list)[-1]
        check_data_contains_params(actual, expected)

    class CleanWebTestMixin(object):
        def test_clean_web_good(self):

            self.env.clean_web_api.set_response_value(
                '',
                clean_web_api_simple_response(True)
            )
            with enable_clean_web():
                with mock.patch.object(self.env.statbox, 'assert_equals', make_statbox_faker_mock(self, True)):
                    getattr(self, base_test_case_name)()
            eq_(len(self.env.clean_web_api.requests), 1)

        def test_clean_web_fail(self):
            self.env.clean_web_api.set_response_side_effect('', BaseCleanWebError)
            with enable_clean_web():
                with mock.patch.object(self.env.statbox, 'assert_equals', make_statbox_faker_mock(self, None)):
                    getattr(self, base_test_case_name)()
            eq_(len(self.env.clean_web_api.requests), 1)

        @parameterized.expand(bad_parameters)
        @raises(CleanWebTestSuccessfulError)
        def test_clean_web_bad(self, clean_web_response, error_fields):
            self.env.clean_web_api.set_response_value(
                '',
                clean_web_api_response_bad_verdicts(clean_web_response)
            )

            post = self.env.client.post
            get = self.env.client.get

            if 'fullname' in error_fields:
                error_fields.remove('fullname')
                error_fields += [f for f in ['firstname', 'lastname'] if f not in error_fields]

            def assert_error_response(response):
                eq_(response.status_code, 200 if is_bundle else 400)
                original_response = json.loads(response.data)
                eq_(original_response.get('status'), 'error')
                expected_errors = [
                    '{}.invalid'.format(f) if is_bundle else {'field': f, 'message': 'Invalid value', 'code': 'invalid'}
                    for f in error_fields
                ]
                eq_(
                    sorted(original_response.get('errors'), key=lambda err: err if is_bundle else err['field']),
                    sorted(expected_errors, key=lambda err: err if is_bundle else err['field']),
                )

            def make_mock(method):
                def _mock(*args, **kwargs):
                    response = method(*args, **kwargs)
                    assert_error_response(response)
                    check_statbox(self, clean_web_response)
                    raise CleanWebTestSuccessfulError
                return _mock

            with enable_clean_web():
                with mock.patch.object(self.env.client, 'get', make_mock(get)):
                    with mock.patch.object(self.env.client, 'post', make_mock(post)):
                        getattr(self, base_test_case_name)()

    def test_clean_web_good_by_parameter(self):
        from passport.backend.core.conf import settings
        assert settings.CLEAN_WEB_API_ENABLED is False
        settings.CLEAN_WEB_API_URL = 'http://localhost/'
        settings.CLEAN_WEB_API_TIMEOUT = 1
        settings.CLEAN_WEB_API_RETRIES = 2
        self.env.clean_web_api.set_response_value(
            '',
            clean_web_api_simple_response(True)
        )
        post = self.env.client.post

        def post_mock(*args, **kwargs):
            kwargs['data'] = dict(kwargs.get('data', {}), force_clean_web=True)
            return post(*args, **kwargs)

        with mock.patch.object(self.env.client, 'post', post_mock):
            with mock.patch.object(self.env.statbox, 'assert_has_written',
                                   make_statbox_faker_mock(self, True)):
                getattr(self, base_test_case_name)()
        eq_(len(self.env.clean_web_api.requests), 1)

    if has_force_parameter:
        CleanWebTestMixin.test_clean_web_good_by_parameter = test_clean_web_good_by_parameter

    return CleanWebTestMixin


class AccountModificationNotifyTestMixin(object):
    def start_account_modification_notify_mocks(self, ip):
        self.fake_region = FakeRegion()
        self.fake_region.set_region_for_ip(ip, dict(
            lat=55.755833,
            lon=37.617222,
            linguistics=mock.Mock(
                return_value=mock.Mock(nominative='Москва'),
            ),
        ))
        self.fake_region.start()
        self.push_now_patch = mock.patch(
            'passport.backend.api.views.bundle.mixins.push.time',
            mock.Mock(time=mock.Mock(return_value=TEST_NOW)),
        )
        self.push_now_patch.start()
        self.email_now_patch = mock.patch(
            'passport.backend.api.views.bundle.mixins.mail.datetime',
            mock.Mock(datetime=mock.Mock(now=mock.Mock(return_value=unixtime_to_datetime(TEST_NOW)))),
        )
        self.email_now_patch.start()

    def stop_account_modification_notify_mocks(self):
        self.push_now_patch.stop()
        self.fake_region.stop()

    def check_account_modification_push_sent(
        self,
        ip,
        event_name,
        uid,
        title,
        body,
        track_id='11111111111111111111111111111111',
        context=None,
        index=0,
    ):
        webview_url = (
            'https://0.passportdev.yandex.ru/am/push/changesalert/?uid={}'
            '&timestamp={}&track_id={}'
            '&ip={}&location=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0'
            '&map_url=https%3A%2F%2Fstatic-maps.yandex.ru%2F1.x%2F%3Fsize'
            '%3D450%2C450%26z%3D8%26l%3Dmap%26ll%3D37.617222%2C55.755833'
            '%26lang%3Dru%26pt%3D37.617222%2C55.755833%2Cpmrdm&title_key={}'.format(
                uid, TEST_NOW, track_id, ip, event_name,
            )
        )

        assert len(self.env.lbw_challenge_pushes.dict_requests) >= index + 1
        recipient = {
            'uid': str(uid),
            'app_targeting_type': 'ONE_APP_PER_DEVICE',
            'required_am_capabilities': ['push:passport_protocol'],
        }
        if context:
            recipient['context'] = context
        self.assertEqual(
            self.env.lbw_challenge_pushes.dict_requests[index],
            {
                'push_message_request': {
                    'push_service': 'account_modification',
                    'event_name': event_name,
                    'recipients': [recipient],
                    'text_body': {
                        'title': title,
                        'body': body,
                    },
                    'webview_body': {
                        'webview_url': webview_url,
                        'require_web_auth': True,
                    },
                    'push_id': AnyMatcher(),
                },
            },
        )

    def check_account_modification_push_not_sent(self):
        assert len(self.env.lbw_challenge_pushes.dict_requests) == 0

    def create_account_modification_mail(
        self,
        event_name,
        email_address,
        context=None,
        is_native=True,
    ):
        context = dict() if context is None else context

        # Извлекаем из context те ключи, которые используются в переводах
        default_t10n_context = dict(
            login='test-user',
        )
        t10n_context = dict(context)
        for key in default_t10n_context:
            t10n_context.setdefault(key, default_t10n_context[key])

        if not is_native and 'login' in t10n_context:
            t10n_context['login'] = masked_login(t10n_context['login'])

        # Извлекаем из context те ключи, которые не используются переводах
        default_body_words = dict(
            LOCATION='Москва',
            TIMESTAMP=datetime_to_string(unixtime_to_datetime(TEST_NOW), '%d.%m.%Y %H:%M'),
            UID='1',
            USER_IP='3.3.3.3',
        )
        body_words = dict([i for i in t10n_context.items() if i[0] in default_body_words])
        for key in default_body_words:
            body_words.setdefault(key, default_body_words[key])
        body_words['UID'] = 'uid=' + str(body_words['UID'])

        warning_key = 'account_modification.%s.email.warning' % event_name

        return dict(
            addresses=[email_address],
            language='ru',
            subject=warning_key,
            context=t10n_context,
            tanker_keys={
                warning_key: t10n_context,
            },
            body_words=body_words.values(),
        )
