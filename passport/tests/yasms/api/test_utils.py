# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import TestCase

from flask import request
import mock
from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
    raises,
)
from passport.backend.api.test.emails import (
    assert_user_notified_about_alias_as_login_and_email_disabled,
    assert_user_notified_about_alias_as_login_and_email_enabled,
    assert_user_notified_about_alias_as_login_and_email_owner_changed,
)
from passport.backend.api.yasms import exceptions as yasms_exceptions
from passport.backend.api.yasms.utils import (
    aliasify,
    build_default_restricter,
    build_send_confirmation_code,
    does_binding_allow_washing,
    get_account_by_uid,
    get_operation_id_by_phone_number,
    remove_equal_phone_bindings,
)
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms import exceptions as yasms_builder_exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import (
    sms_per_ip,
    sms_per_ip_for_consumer,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.env import Environment
from passport.backend.core.models.phones.faker import (
    assert_phonenumber_alias_removed,
    build_account,
    build_phone_secured,
    build_remove_operation,
)
from passport.backend.core.models.phones.phones import (
    _ConfirmationInfo,
    TrackedConfirmationInfo,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.ip.ip import IP
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime

from .base import BaseYasmsTestCase


UID_ALPHA = 2233
UID_BETA = 1001
UID_GAMMA = 4000
TEST_DATE = datetime(2014, 2, 16, 0, 1, 0)
TEST_TIMESTAMP = to_unixtime(TEST_DATE)
PHONE_NUMBER = PhoneNumber.parse(u'+79023344555')
PHONE_NUMBER_EXTRA = PhoneNumber.parse(u'+79026411724')
CONFIRMATION_CODE = u'3232'
LOGIN = u'testlogin'
PHONISH_LOGIN1 = 'phne-test1'
EMAIL = LOGIN + u'@yandex-team.ru'
LOGIN_EXTRA = u'testloginextra'
EMAIL_EXTRA = LOGIN_EXTRA + u'@yandex-team.ru'
CONSUMER = u'hathaway'
ALIAS_SID = 65
USER_IP = u'1.2.3.4'
PHONE_ID = 1
PHONE_ID2 = 2
OPERATION_ID = 3
TEST_DISPLAY_LANGUAGE = 'ru'


@with_settings()
class TestGetAccountByUid(BaseYasmsTestCase):
    def setUp(self):
        super(TestGetAccountByUid, self).setUp()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=UID_ALPHA),
        )

    def test_ok(self):
        with self._default_settings():
            account = get_account_by_uid(UID_ALPHA, self._blackbox_builder)

        eq_(len(self.env.blackbox.requests), 1)
        eq_(account.uid, UID_ALPHA)


class TestSendConfirmationCode(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        **mock_counters(
            PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, 2),
            UNTRUSTED_PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, 2),
        )
    )

    def setUp(self):
        super(TestSendConfirmationCode, self).setUp()
        self.setup_statbox_templates()

    def _build_args(self, **kwargs):
        kwargs.setdefault(u'phone_number', u'+79010000001')
        confirmation_info = _ConfirmationInfo(
            code_value=CONFIRMATION_CODE,
            code_last_sent=None,
            code_send_count=0,
            code_checks_count=0,
            code_confirmed=None,
        )
        kwargs.setdefault(
            u'confirmation_info',
            confirmation_info,
        )
        kwargs.setdefault(u'account', build_account(uid=UID_ALPHA, language=u'ru'))
        kwargs.setdefault(u'env', self._build_env())
        kwargs.setdefault(u'consumer', u'tester')
        kwargs.setdefault(u'yasms_builder', self._yasms_builder)
        kwargs.setdefault(u'statbox', self._statbox)
        kwargs.setdefault(
            u'restricter',
            build_default_restricter(
                confirmation_info=kwargs[u'confirmation_info'],
                env=kwargs[u'env'],
                phone_number=[u'phone_number'],
                statbox=self._statbox,
                consumer=u'tester',
            ),
        )
        return kwargs

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            u'send_confirmation_code',
            action=u'send_confirmation_code',
            number=u'+79010******',
            uid=str(UID_ALPHA),
        )

    @staticmethod
    def _build_env(user_ip=USER_IP, user_agent='curl'):
        return Environment(
            user_agent=user_agent,
            user_ip=user_ip,
        )

    def test_yasms_called(self):
        """
        Вызывается Я.Смс.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args()
        )
        send_confirmation_code()

        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        ok_(requests[0].method_equals(u'send_sms', self.env.yasms))

    def test_phone_number(self):
        """
        Передаётся номер телефона.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(phone_number=u'+79026411724')
        )
        send_confirmation_code()

        self.env.yasms.requests[0].assert_query_contains({
            u'phone': u'+79026411724',
        })

    def test_russian_message(self):
        """
        Отправляется сообщение на русском языке.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(
                account=build_account(uid=UID_ALPHA, language=u'ru'),
                confirmation_info=_ConfirmationInfo(
                    code_value=CONFIRMATION_CODE,
                    code_last_sent=None,
                    code_send_count=0,
                    code_checks_count=0,
                    code_confirmed=None,
                ),
            )
        )
        send_confirmation_code()

        self.env.yasms.requests[0].assert_query_contains({
            u'text': u'Ваш код подтверждения: {{code}}. Наберите его в поле ввода.',
        })
        self.env.yasms.requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % CONFIRMATION_CODE,
        })

    def test_english_message(self):
        """
        Отправляется сообщение на английском языке.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(
                account=build_account(uid=UID_ALPHA, language=u'en'),
                confirmation_info=_ConfirmationInfo(
                    code_value=u'1234',
                    code_last_sent=None,
                    code_send_count=0,
                    code_checks_count=0,
                    code_confirmed=None,
                ),
            )
        )
        send_confirmation_code()

        self.env.yasms.requests[0].assert_query_contains({
            u'text': u'Your confirmation code is {{code}}. Please enter it in the text field.',
        })
        self.env.yasms.requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "1234"}',
        })

    def test_uid(self):
        """
        Передаётся uid.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(account=build_account(uid=1919))
        )
        send_confirmation_code()

        self.env.yasms.requests[0].assert_query_contains({
            u'from_uid': u'1919',
        })

    def test_consumer(self):
        """
        Передаётся consumer.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(consumer=u'oops')
        )
        send_confirmation_code()

        self.env.yasms.requests[0].assert_query_contains({
            u'caller': u'oops',
        })

    def test_action(self):
        """
        Передаётся идентификтор действия в контексте, которого высылается код
        для подтверждения.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        with self._statbox.make_context(action=u'reaction'):
            send_confirmation_code = build_send_confirmation_code(
                **self._build_args(statbox=self._statbox)
            )
            send_confirmation_code()

        self.env.yasms.requests[0].assert_query_contains({
            u'identity': u'reaction.send_confirmation_code',
        })

    def test_log_success_to_statbox(self):
        """
        Делаем запись в статбоксе об успешной отправке кода.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(
                account=build_account(uid=UID_BETA, language=u'ru'),
                phone_number=u'+79023344555',
                env=self._build_env(user_ip=u'4.3.2.1'),
                statbox=self._statbox,
            )
        )
        send_confirmation_code()
        self._statbox.dump_stashes(operation_id=913)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                action=u'send_confirmation_code.code_sent',
                number=u'+79023******',
                ip=u'4.3.2.1',
                uid=str(UID_BETA),
                operation_id=u'913',
                sms_count=u'1',
                sms_id=u'1',
            ),
        ])

    def test_possible__counters_not_hit_limit(self):
        """
        Действие разрешается, когда счётчики не достигли предела.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        user_ip = u'1.1.1.1'
        sms_per_ip.get_counter(user_ip).incr(user_ip)

        eq_(sms_per_ip.get_counter(user_ip).get(user_ip), 1)
        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(env=self._build_env(user_ip=user_ip))
        )
        send_confirmation_code()

    def test_confirmation_code_message_counter_hit_limit__fail(self):
        """
        Действие запрещается, когда счётчик отправленных сообщений с кодом
        для подтверждения достиг предела.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        user_ip = u'2.2.2.2'
        for _ in range(2):
            sms_per_ip.get_counter(user_ip).incr(user_ip)

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(
                env=self._build_env(user_ip=user_ip),
                statbox=self._statbox,
            )
        )
        with self.assertRaises(yasms_exceptions.YaSmsIpLimitExceeded):
            send_confirmation_code()

        self._statbox.dump_stashes()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                error=u'sms_limit.exceeded',
                reason='ip_limit',
            ),
        ])

    def test_confirmation_code_consumer_message_counter_not_hit_limit(self):
        """
        Действие разрешается, когда счётчик отправленных кодов подтверждения через
        потребителя не достиг предела.
        Даже если глобальный счётчик достиг предела.
        """
        self.env.yasms.set_response_value(u'send_sms', yasms_send_sms_response(sms_id=1))
        user_ip = u'2.2.2.2'

        with settings_context(
            **mock_counters(
                DB_NAME_TO_COUNTER={u'sms:ip_and_consumer:tester': (24, 3600, 5)},
                UNTRUSTED_PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, 2),
            )
        ):
            for _ in range(2):
                sms_per_ip.get_counter(user_ip).incr(user_ip)

            send_confirmation_code = build_send_confirmation_code(
                **self._build_args(
                    env=self._build_env(user_ip=user_ip),
                    statbox=self._statbox,
                )
            )
            send_confirmation_code()

            eq_(sms_per_ip.get_counter(user_ip).get(user_ip), 2)
            eq_(sms_per_ip_for_consumer.get_counter('tester').get(user_ip), 1)

    def test_confirmation_code_message_for_consumer_counter_hit_limit__fail(self):
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response(sms_id=1))
        user_ip = u'2.2.2.2'

        with settings_context(
            **mock_counters(
                DB_NAME_TO_COUNTER={u'sms:ip_and_consumer:tester': (24, 3600, 2)},
                UNTRUSTED_PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 30, 5),
            )
        ):
            for _ in range(2):
                sms_per_ip_for_consumer.get_counter(u'tester').incr(user_ip)

            send_confirmation_code = build_send_confirmation_code(
                **self._build_args(
                    env=self._build_env(user_ip=user_ip),
                    statbox=self._statbox,
                )
            )
            with self.assertRaises(yasms_exceptions.YaSmsIpLimitExceeded):
                send_confirmation_code()

            self._statbox.dump_stashes()
            self.env.statbox.assert_has_written([
                self.env.statbox.entry(
                    u'send_confirmation_code',
                    error=u'sms_limit.exceeded',
                    reason=u'ip_and_consumer_limit',
                ),
            ])

    def test_increase_confirmation_code_message_counter(self):
        """
        Увеличается счётчик отправленных сообщений с кодом для подтверждения.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        user_ip = u'1.1.1.1'
        eq_(sms_per_ip.get_counter(user_ip).get(user_ip), 0)

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(env=self._build_env(user_ip=user_ip))
        )
        send_confirmation_code()

        eq_(sms_per_ip.get_counter(user_ip).get(user_ip), 1)

    def test_typed_ip(self):
        """
        Адрес можно передавать как объект класса IP.
        """
        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(env=self._build_env(user_ip=IP(u'4.3.2.1')))
        )
        eq_(send_confirmation_code._user_ip, u'4.3.2.1')

    def test_typed_phone_number(self):
        """
        Номер телефона можно передавать как объект класса PhoneNumber.
        """
        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(phone_number=PhoneNumber.parse(u'+79020000002'))
        )
        eq_(
            send_confirmation_code._phone_number,
            PhoneNumber.parse(u'+79020000002'),
        )

    def test_string_phone_number(self):
        """
        Номер телефона можно передавать как строку.
        """
        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(phone_number=u'+79020000002')
        )
        eq_(
            send_confirmation_code._phone_number,
            PhoneNumber.parse(u'+79020000002'),
        )

    @raises(yasms_exceptions.YaSmsTemporaryError)
    def test_temporary_error(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsTemporaryError,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args()
        )
        send_confirmation_code()

    def test_log_temporary_error_to_statbox(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsTemporaryError,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(statbox=self._statbox)
        )
        try:
            send_confirmation_code()
        except yasms_exceptions.YaSmsTemporaryError:
            self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                error=u'sms.isnt_sent',
            ),
        ])

    @raises(yasms_exceptions.YaSmsLimitExceeded)
    def test_limit_exceeded(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsLimitExceeded,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args()
        )
        send_confirmation_code()

    def test_log_limit_exceeded_to_statbox(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsLimitExceeded,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(statbox=self._statbox)
        )
        try:
            send_confirmation_code()
        except yasms_exceptions.YaSmsLimitExceeded:
            self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                error=u'sms_limit.exceeded',
                reason='yasms_phone_limit',
            ),
        ])

    @raises(yasms_exceptions.YaSmsDeliveryError)
    def test_delivery_error(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsDeliveryError,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args()
        )
        send_confirmation_code()

    def test_log_delivery_error_to_statbox(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsDeliveryError,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(statbox=self._statbox)
        )
        try:
            send_confirmation_code()
        except yasms_exceptions.YaSmsDeliveryError:
            self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                error=u'sms.isnt_sent',
            ),
        ])

    @raises(yasms_exceptions.YaSmsPermanentBlock)
    def test_permanent_block(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsPermanentBlock,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args()
        )
        send_confirmation_code()

    def test_log_permanent_block_to_statbox(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsPermanentBlock,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(statbox=self._statbox)
        )
        try:
            send_confirmation_code()
        except yasms_exceptions.YaSmsPermanentBlock:
            self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                error=u'phone.blocked',
            ),
        ])

    @raises(yasms_exceptions.YaSmsTemporaryBlock)
    def test_temporary_block(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsTemporaryBlock,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args()
        )
        send_confirmation_code()

    def test_log_temporary_block_to_statbox(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsTemporaryBlock,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(statbox=self._statbox)
        )
        try:
            send_confirmation_code()
        except yasms_exceptions.YaSmsTemporaryBlock:
            self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                error=u'sms_limit.exceeded',
                reason='yasms_rate_limit',
            ),
        ])

    @raises(yasms_exceptions.YaSmsUidLimitExceeded)
    def test_uid_limit_exceeded(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsUidLimitExceeded,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args()
        )
        send_confirmation_code()

    def test_log_uid_limit_exceeded_to_statbox(self):
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            yasms_builder_exceptions.YaSmsUidLimitExceeded,
        )

        send_confirmation_code = build_send_confirmation_code(
            **self._build_args(statbox=self._statbox)
        )
        try:
            send_confirmation_code()
        except yasms_exceptions.YaSmsUidLimitExceeded:
            self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'send_confirmation_code',
                error=u'sms_limit.exceeded',
                reason='yasms_uid_limit',
            ),
        ])

    def test_tracked_confirmation_info(self):
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        track_manager, track_id = self.env.track_manager.get_manager_and_trackid()
        with track_manager.transaction(track_id).commit_on_error() as track:
            track.phone_confirmation_code = CONFIRMATION_CODE

        track = track_manager.read(track_id)
        confirm_info = TrackedConfirmationInfo(track)

        with track_manager.transaction(track=track).commit_on_error():
            send_confirmation_code = build_send_confirmation_code(
                **self._build_args(
                    account=None,
                    confirmation_info=confirm_info,
                    language=TEST_DISPLAY_LANGUAGE,
                )
            )
            send_confirmation_code()
            confirm_info.save()

        eq_(track.phone_confirmation_last_send_at, TimeNow())
        eq_(track.phone_confirmation_sms_count.get(), 1)
        eq_(track.phone_confirmation_code, CONFIRMATION_CODE)

        self.env.yasms.requests[0].assert_query_contains({
            u'text': u'Ваш код подтверждения: {{code}}. Наберите его в поле ввода.',
        })
        self.env.yasms.requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % CONFIRMATION_CODE,
        })

    def test_empty_confirmation_code(self):
        with mock.patch(
                'passport.backend.utils.common._generate_random_code',
                mock.Mock(return_value=CONFIRMATION_CODE),
        ):
            self.env.yasms.set_response_value(
                'send_sms',
                yasms_send_sms_response(),
            )
            track_manager, track_id = self.env.track_manager.get_manager_and_trackid()
            track = track_manager.read(track_id)
            confirm_info = TrackedConfirmationInfo(track)

            with track_manager.transaction(track=track).commit_on_error():
                send_confirmation_code = build_send_confirmation_code(
                    **self._build_args(
                        account=None,
                        confirmation_info=confirm_info,
                        language=TEST_DISPLAY_LANGUAGE,
                    )
                )
                send_confirmation_code()
                confirm_info.save()

            eq_(track.phone_confirmation_last_send_at, TimeNow())
            eq_(track.phone_confirmation_sms_count.get(), 1)
            eq_(track.phone_confirmation_code, CONFIRMATION_CODE)

            self.env.yasms.requests[0].assert_query_contains({
                u'text': u'Ваш код подтверждения: {{code}}. Наберите его в поле ввода.',
            })
            self.env.yasms.requests[0].assert_post_data_contains({
                u'text_template_params': u'{"code": "%s"}' % CONFIRMATION_CODE,
            })


class BaseTestAliasification(BaseYasmsTestCase):
    def setUp(self):
        super(BaseTestAliasification, self).setUp()
        request.env = Environment(user_ip=USER_IP)
        self._setup_statbox_templates()

    def _setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base',
            consumer=CONSUMER,
            ip=USER_IP,
            user_agent='-',
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_enabled',
            _inherit_from=['phonenumber_alias_search_enabled', 'base'],
            uid=str(UID_ALPHA),
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_removed',
            _inherit_from=['phonenumber_alias_removed', 'base'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_added',
            _inherit_from=['phonenumber_alias_added', 'base'],
        )

    def _build_alpha_account(
        self,
        blackbox_faker=None,
        db_faker=Undefined,
        descriptor=None,
        **kwargs
    ):
        if db_faker is Undefined:
            db_faker = self.env.db
        if descriptor is None:
            descriptor = self._build_alpha_account_descriptor(**kwargs)
        return build_account(
            db_faker=db_faker,
            blackbox_faker=blackbox_faker,
            **descriptor
        )

    def _build_alpha_account_descriptor(
        self,
        login=LOGIN,
        phone_number=None,
        **kwargs
    ):
        if 'emails' not in kwargs:
            mail = self.env.email_toolkit.create_native_email(
                login=EMAIL.split(u'@')[0],
                domain=EMAIL.split(u'@')[1],
            )
            kwargs.update(emails=[mail])

        if phone_number is None:
            phone_number = PHONE_NUMBER

        return dict(
            uid=UID_ALPHA,
            login=login,
            language=u'ru',
            firstname=LOGIN,
            **deep_merge(
                build_phone_secured(PHONE_ID, phone_number.e164),
                kwargs,
            )
        )

    def _build_beta_account(self, **kwargs):
        descriptor = self._build_beta_account_descriptor(**kwargs)
        return build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **descriptor
        )

    def _build_beta_account_descriptor(self, phone_number=None, **kwargs):
        if phone_number is None:
            phone_number = PHONE_NUMBER
        if 'emails' not in kwargs:
            mail = self.env.email_toolkit.create_native_email(
                login=EMAIL_EXTRA.split(u'@')[0],
                domain=EMAIL_EXTRA.split(u'@')[1],
            )
            kwargs.update(emails=[mail])
        return dict(
            uid=UID_BETA,
            login=LOGIN_EXTRA,
            firstname=LOGIN_EXTRA,
            language=u'ru',
            aliases={
                u'portal': LOGIN_EXTRA,
                u'phonenumber': phone_number.digital,
            },
            attributes={u'account.enable_search_by_phone_alias': u'1'},
            **kwargs
        )

    def _statbox_line_phone_alias_subscription(self, **kwargs):
        return self.env.statbox.entry(
            'subscriptions',
            ip=USER_IP,
            sid=str(ALIAS_SID),
            consumer=CONSUMER,
            **kwargs
        )

    def _assert_account_has_alias(self, account, phone_number=None):
        if phone_number is None:
            phone_number = PHONE_NUMBER
        eq_(account.phonenumber_alias.alias, phone_number.digital)
        self.env.db.check(u'aliases', u'phonenumber', phone_number.digital, uid=account.uid, db='passportdbcentral')

    def _assert_account_does_not_have_alias(self, account):
        ok_(not account.phonenumber_alias)
        self.env.db.check_missing(u'aliases', u'phonenumber', uid=account.uid, db='passportdbcentral')

    def _assert_alias_asked_from_blackbox(self):
        self.env.blackbox.requests[0].assert_post_data_contains({
            u'method': u'userinfo',
            u'login': PHONE_NUMBER.digital,
            u'aliases': u'all_with_hidden',
            u'emails': u'getall',
        })

    def _assert_alpha_notified_about_dealiasify(self, message):
        assert_user_notified_about_alias_as_login_and_email_disabled(
            mailer_faker=self.env.mailer,
            language='en',
            email_address=EMAIL,
            firstname=LOGIN,
            login=LOGIN,
            portal_email=EMAIL,
            phonenumber_alias=PHONE_NUMBER_EXTRA.digital,
        )

    def _assert_beta_notified_about_dealiasify(self, message):
        assert_user_notified_about_alias_as_login_and_email_owner_changed(
            mailer_faker=self.env.mailer,
            language='ru',
            email_address=EMAIL_EXTRA,
            firstname=LOGIN_EXTRA,
            login=LOGIN_EXTRA,
            portal_email=EMAIL_EXTRA,
            phonenumber_alias=PHONE_NUMBER.digital,
        )

    def _assert_alpha_notified_about_aliasify(self, message, language):
        assert_user_notified_about_alias_as_login_and_email_enabled(
            self.env.mailer,
            language,
            EMAIL,
            firstname=LOGIN,
            login=LOGIN,
            portal_email=EMAIL,
            phonenumber_alias=PHONE_NUMBER.digital,
        )

    def _event_lines_alpha_dealiasified(self):
        return (
            {
                u'uid': str(UID_ALPHA),
                u'name': u'alias.phonenumber.rm',
                u'value': PHONE_NUMBER_EXTRA.international,
            },
            {u'uid': str(UID_ALPHA), u'name': u'action', u'value': u'action'},
            {u'uid': str(UID_ALPHA), u'name': u'consumer', u'value': CONSUMER},

        )

    def _event_lines_beta_dealiasified(self):
        return (
            {
                u'uid': str(UID_BETA),
                u'name': u'alias.phonenumber.rm',
                u'value': PHONE_NUMBER.international,
            },
            {u'uid': str(UID_BETA), u'name': u'action', u'value': u'action'},
            {u'uid': str(UID_BETA), u'name': u'consumer', u'value': CONSUMER},
        )

    def _event_lines_alpha_aliasified(self):
        return (
            {
                u'uid': str(UID_ALPHA),
                u'name': u'alias.phonenumber.add',
                u'value': PHONE_NUMBER.international,
            },
            {u'uid': str(UID_ALPHA), u'name': u'action', u'value': u'action'},
            {u'uid': str(UID_ALPHA), u'name': u'consumer', u'value': CONSUMER},
        )


class TestAliasify(BaseTestAliasification):
    def test_realiasify_with_notification(self):
        # Удаляется старый алиас
        # Удаляется алиас с другой учётной записи
        # Создаётся алиас
        # Учитывается переданный язык
        # Рассылаются почтовые уведомления

        account = self._build_alpha_account(
            aliases={
                u'portal': LOGIN,
                u'phonenumber': PHONE_NUMBER_EXTRA.digital,
            },
            attributes={u'account.enable_search_by_phone_alias': u'1'},
        )
        self._build_beta_account()

        prev_owner = aliasify(
            account,
            PHONE_NUMBER,
            self._blackbox_builder,
            self._statbox,
            CONSUMER,
            u'action',
            u'en',
        )

        self._assert_account_has_alias(account)
        assert_phonenumber_alias_removed(self.env.db, UID_ALPHA, PHONE_NUMBER_EXTRA.digital)

        eq_(prev_owner.phonenumber_alias, None)
        assert_phonenumber_alias_removed(self.env.db, UID_BETA, PHONE_NUMBER.digital)

        self._assert_alias_asked_from_blackbox()

        self._assert_alpha_notified_about_dealiasify(self.env.mailer.messages[0])
        self._assert_beta_notified_about_dealiasify(self.env.mailer.messages[1])
        self._assert_alpha_notified_about_aliasify(self.env.mailer.messages[2], u'en')

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('phonenumber_alias_removed', uid=str(UID_ALPHA)),
            self._statbox_line_phone_alias_subscription(
                operation=u'removed',
                uid=str(UID_ALPHA),
            ),
            self.env.statbox.entry('phonenumber_alias_removed', uid=str(UID_BETA)),
            self._statbox_line_phone_alias_subscription(
                operation=u'removed',
                uid=str(UID_BETA),
            ),
            self.env.statbox.entry('phonenumber_alias_added', uid=str(UID_ALPHA)),
            self._statbox_line_phone_alias_subscription(
                operation=u'added',
                uid=str(UID_ALPHA),
            ),
            self.env.statbox.entry('phonenumber_alias_search_enabled'),
        ])

        self.env.event_logger.assert_contains(
            self._event_lines_alpha_dealiasified() +
            self._event_lines_beta_dealiasified() +
            self._event_lines_alpha_aliasified()
        )

    def test_create_alias(self):
        # Создаётся алиас
        # Алиас не назначён другой учётной записи
        # Высылается уведомление
        # Берётся язык учётной записи

        account = self._build_alpha_account(
            aliases={
                u'portal': LOGIN,
            },
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        prev_owner = aliasify(
            account,
            PHONE_NUMBER,
            self._blackbox_builder,
            self._statbox,
            CONSUMER,
            u'action',
        )

        self._assert_account_has_alias(account)
        ok_(not prev_owner)

        self._assert_alias_asked_from_blackbox()

        self._assert_alpha_notified_about_aliasify(self.env.mailer.messages[0], u'ru')

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('phonenumber_alias_added', uid=str(UID_ALPHA)),
            self._statbox_line_phone_alias_subscription(
                operation=u'added',
                uid=str(UID_ALPHA),
            ),
            self.env.statbox.entry('phonenumber_alias_search_enabled'),
        ])

        self.env.event_logger.assert_contains(self._event_lines_alpha_aliasified())

    def test_has_alias(self):
        # Учётной записи уже назначен данный алиас

        account = self._build_alpha_account(
            aliases={
                u'portal': LOGIN,
                u'phonenumber': PHONE_NUMBER.digital,
            },
            attributes={u'account.enable_search_by_phone_alias': u'1'},
        )

        prev_owner = aliasify(
            account,
            PHONE_NUMBER,
            self._blackbox_builder,
            self._statbox,
            CONSUMER,
            u'action',
        )

        self._assert_account_has_alias(account)
        ok_(not prev_owner)

        eq_(self.env.blackbox.requests, [])
        eq_(self.env.mailer.messages, [])
        self.env.statbox.assert_has_written([])
        self.env.event_logger.assert_events_are_logged([])

    def test_alias_not_allowed(self):
        # Учётной записи не позволяется назначать телефонный алиас

        account = self._build_alpha_account(
            # Социальным пользователям нельзя заводить телефонный алиас
            login=u'uid-' + str(UID_ALPHA),
            aliases={
                u'social': u'uid-' + str(UID_ALPHA),
            },
        )

        prev_owner = aliasify(
            account,
            PHONE_NUMBER,
            self._blackbox_builder,
            self._statbox,
            CONSUMER,
            u'action',
        )

        ok_(not account.phonenumber_alias.number)
        ok_(not prev_owner)

        eq_(self.env.blackbox.requests, [])
        eq_(self.env.mailer.messages, [])
        self.env.statbox.assert_has_written([])
        self.env.event_logger.assert_events_are_logged([])

    @raises(DBError)
    def test_account_alias__true__race(self):
        # Нам известно что на учётной записи нет алиаса
        # ЧЯ говорит, что на учётной записи есть алиас, и это правда

        emails = [self.env.email_toolkit.create_native_email(LOGIN, 'yandex.ru')]
        account = self._build_alpha_account(
            db_faker=None,
            emails=emails,
            aliases={
                u'portal': LOGIN,
            },
        )
        self._build_alpha_account(
            blackbox_faker=self.env.blackbox,
            emails=emails,
            aliases={
                u'portal': LOGIN_EXTRA,
                u'phonenumber': PHONE_NUMBER.digital,
            },
            attributes={u'account.enable_search_by_phone_alias': u'1'},
        )

        aliasify(
            account,
            PHONE_NUMBER,
            self._blackbox_builder,
            self._statbox,
            CONSUMER,
            u'action',
        )

    def test_account_alias__false__race(self):
        # Нам известно что на учётной записи нет алиаса
        # ЧЯ говорит, что на учётной записи есть алиас, и это неправда

        emails = [self.env.email_toolkit.create_native_email(LOGIN, 'yandex.ru')]
        account = self._build_alpha_account(
            db_faker=None,
            emails=emails,
            aliases={
                u'portal': LOGIN,
            },
        )
        self._build_alpha_account(
            db_faker=None,
            blackbox_faker=self.env.blackbox,
            emails=emails,
            aliases={
                u'portal': LOGIN_EXTRA,
                u'phonenumber': PHONE_NUMBER.digital,
            },
        )
        self._build_alpha_account(
            emails=emails,
            aliases={
                u'portal': u'%s_2' % LOGIN,
            },
        )

        prev_owner = aliasify(
            account,
            PHONE_NUMBER,
            self._blackbox_builder,
            self._statbox,
            CONSUMER,
            u'action',
        )

        self._assert_account_has_alias(account)
        ok_(not prev_owner)


class TestDoesBindingAllowWashing(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        YASMS_VALIDATION_LIMIT=2,
    )

    def test_count_binding(self):
        # Привязки нет в истории
        # Привязку нужно считатать
        # В истории limit привязок данного номера

        bindings_history = {
            u'status': u'ok',
            u'history': [
                {u'phone': PHONE_NUMBER.e164, u'uid': UID_BETA, u'ts': to_unixtime(TEST_DATE)},
                {u'phone': PHONE_NUMBER.e164, u'uid': UID_GAMMA, u'ts': to_unixtime(TEST_DATE)},
            ],
        }

        is_allowed = does_binding_allow_washing(
            account=build_account(uid=UID_ALPHA),
            phone_number=PHONE_NUMBER.e164,
            binding_time=TEST_DATE,
            should_ignore_binding_limit=False,
            bindings_history=bindings_history,
        )

        ok_(not is_allowed)

    def test_dont_count_binding_double(self):
        # Привязка есть в истории
        # Привязку нужно считатать
        # В истории limit привязок данного номера
        # В истории есть привязки других номеров

        bindings_history = {
            u'status': u'ok',
            u'history': [
                {u'phone': PHONE_NUMBER.e164, u'uid': UID_ALPHA, u'ts': to_unixtime(TEST_DATE)},
                {u'phone': PHONE_NUMBER.e164, u'uid': UID_BETA, u'ts': to_unixtime(TEST_DATE)},
                {u'phone': PHONE_NUMBER_EXTRA.e164, u'uid': UID_BETA, u'ts': to_unixtime(TEST_DATE)},
            ],
        }

        is_allowed = does_binding_allow_washing(
            account=build_account(uid=UID_ALPHA),
            phone_number=PHONE_NUMBER.e164,
            binding_time=TEST_DATE,
            should_ignore_binding_limit=False,
            bindings_history=bindings_history,
        )

        ok_(is_allowed)

    def test_dont_count_binding(self):
        # Привязки нет в истории
        # Привязку не нужно считатать
        # В истории limit привязок данного номера

        bindings_history = {
            u'status': u'ok',
            u'history': [
                {u'phone': PHONE_NUMBER.e164, u'uid': UID_BETA, u'ts': to_unixtime(TEST_DATE)},
                {u'phone': PHONE_NUMBER.e164, u'uid': UID_GAMMA, u'ts': to_unixtime(TEST_DATE)},
            ],
        }

        is_allowed = does_binding_allow_washing(
            account=build_account(uid=UID_ALPHA),
            phone_number=PHONE_NUMBER.e164,
            binding_time=TEST_DATE,
            should_ignore_binding_limit=True,
            bindings_history=bindings_history,
        )

        ok_(is_allowed)

    def test_empty_history(self):
        # История пуста
        # Привязку не нужно считатать

        bindings_history = {
            u'status': u'ok',
            u'history': [],
        }

        is_allowed = does_binding_allow_washing(
            account=build_account(uid=UID_ALPHA),
            phone_number=PHONE_NUMBER.e164,
            binding_time=TEST_DATE,
            should_ignore_binding_limit=True,
            bindings_history=bindings_history,
        )

        ok_(is_allowed)

    def test_karma_prefix_spammer(self):
        bindings_history = {
            u'status': u'ok',
            u'history': [],
        }
        account = build_account(uid=UID_ALPHA, karma='1000')

        is_allowed = does_binding_allow_washing(
            account=account,
            phone_number=PHONE_NUMBER.e164,
            binding_time=TEST_DATE,
            should_ignore_binding_limit=False,
            bindings_history=bindings_history,
        )

        ok_(not is_allowed)

    def test_karma_prefix_washed_by_support(self):
        bindings_history = {
            u'status': u'ok',
            u'history': [],
        }
        account = build_account(uid=UID_ALPHA, karma='2000')

        is_allowed = does_binding_allow_washing(
            account=account,
            phone_number=PHONE_NUMBER.e164,
            binding_time=TEST_DATE,
            should_ignore_binding_limit=False,
            bindings_history=bindings_history,
        )

        ok_(not is_allowed)

    def test_karma_value_sure_spammer_from_russia(self):
        bindings_history = {
            u'status': u'ok',
            u'history': [],
        }
        account = build_account(uid=UID_ALPHA, karma='0100')

        is_allowed = does_binding_allow_washing(
            account=account,
            phone_number='+79259164525',
            binding_time=TEST_DATE,
            should_ignore_binding_limit=False,
            bindings_history=bindings_history,
        )

        ok_(is_allowed)


class TestGetOperationIdByPhoneNumber(BaseYasmsTestCase):
    def test_ok(self):
        account = build_account(
            uid=UID_ALPHA,
            **deep_merge(
                build_phone_secured(PHONE_ID, PHONE_NUMBER.e164),
                build_remove_operation(OPERATION_ID, PHONE_ID),
            )
        )

        eq_(get_operation_id_by_phone_number(account, PHONE_NUMBER.e164), OPERATION_ID)

    def test_invalid_phone_number(self):
        account = build_account(uid=UID_ALPHA)
        assert_is_none(get_operation_id_by_phone_number(account, '12345'))

    def test_no_phone(self):
        account = build_account(uid=UID_ALPHA)
        assert_is_none(get_operation_id_by_phone_number(account, PHONE_NUMBER.e164))

    def test_no_operation(self):
        account = build_account(
            uid=UID_ALPHA,
            **build_phone_secured(PHONE_ID, PHONE_NUMBER.e164)
        )
        assert_is_none(get_operation_id_by_phone_number(account, PHONE_NUMBER.e164))


class TestRemoveEqualPhoneBindings(TestCase):
    def test_empty(self):
        eq_(remove_equal_phone_bindings([]), [])

    def test_single(self):
        eq_(
            remove_equal_phone_bindings([
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 1},
            ]),
            [{u'uid': 1, u'phone': u'+79010099888', u'ts': 1}],
        )

    def test_different(self):
        eq_(
            remove_equal_phone_bindings([
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 1},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 5},
            ]),
            [
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 1},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 5},
            ],
        )

    def test_equal(self):
        eq_(
            remove_equal_phone_bindings([
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 2},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 1},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 0},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 2},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 1},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 0},
            ]),
            [
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 0},
                {u'uid': 1, u'phone': u'+79010099888', u'ts': 2},
            ],
        )
