# -*- coding: utf-8 -*-

from passport.backend.api.common.phone_karma import PhoneKarma
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)
from passport.backend.core.test.time_utils.time_utils import TimeSpan


class StatboxTestMixin(object):
    def setup_statbox_templates(self, sms_retriever_kwargs=None, confirm_kwargs=None):
        # записи, которые относятся к форматированию SMS под SmsRetriever в Андроиде
        sms_retriever_kwargs = sms_retriever_kwargs or {}
        confirm_kwargs = confirm_kwargs or {}

        self.env.statbox.bind_base(
            track_id=self.track_id,
            step=self.step,
            mode=self.track_state,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            ip=TEST_USER_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            uid=str(TEST_UID) if self.has_uid else '-',
        )
        self.env.statbox.bind_entry(
            'local_base',
            ip=TEST_USER_IP,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'sanitize_phone_number',
            action='sanitize_phone_number',
            sanitize_phone_result=TEST_PHONE_NUMBER.masked_format_for_statbox,
            _exclude=['mode', 'step', 'uid', 'number', 'consumer', 'ip', 'user_agent'],
        )
        self.env.statbox.bind_entry(
            'send_code',
            action='send_code',
            operation='confirm',
            sms_count='1',
            sms_id='1',
            **sms_retriever_kwargs
        )
        self.env.statbox.bind_entry(
            'call_with_code',
            action='call_with_code',
            call_session_id='fed-123-qwe',
            operation='confirm',
            calls_count='1',
        )
        self.env.statbox.bind_entry(
            'flash_call',
            action='flash_call',
            call_session_id='fed-123-qwe',
            operation='confirm',
            calls_count='1',
        )
        self.env.statbox.bind_entry(
            'send_code_error',
            operation='confirm',
            error='sms.isnt_sent',
        )
        self.env.statbox.bind_entry(
            'call_with_code_error',
            operation='confirm',
            error='call.not_made',
        )
        self.env.statbox.bind_entry(
            'flash_call_error',
            operation='confirm',
            error='call.not_made',
        )
        self.env.statbox.bind_entry(
            'check_phone_karma',
            action='check_phone_karma',
            karma=str(PhoneKarma.white),
        )
        self.env.statbox.bind_entry(
            'enter_code',
            time_passed=TimeSpan(0),
            good='1',
            action='enter_code',
            operation='confirm',
        )
        self.env.statbox.bind_entry(
            'code_invalid',
            _inherit_from='enter_code',
            good='0',
            error='code.invalid',
        )
        self.env.statbox.bind_entry(
            'enter_code_error',
            operation='confirm',
            error='1',
        )
        self.env.statbox.bind_entry(
            'submit_phone_confirmation_limit_exceeded',
            action='submit_phone_confirmation',
            operation='confirm',
            error='registration_sms_sent_per_ip_limit_has_exceeded',
            user_ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'phone_compromised',
            operation='confirm',
            error='phone.compromised',
        )
        self.env.statbox.bind_entry(
            'update_phone',
            operation='update',
        )
        self.env.statbox.bind_entry(
            'password_not_matched',
            operation='check_password',
            error='password.not_matched',
        )
        self.env.statbox.bind_entry(
            'save_phone_base',
            operation='save',
        )
        self.env.statbox.bind_entry(
            'save_phone_error',
            _inherit_from='save_phone_base',
            error='phone.isnt_saved',
        )
        self.env.statbox.bind_entry(
            'success',
            ok='1',
            **confirm_kwargs
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_removed',
            _inherit_from=['phonenumber_alias_subscription_removed', 'local_base'],
            _exclude=['mode', 'number', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_taken_away',
            _inherit_from=['phonenumber_alias_taken_away', 'local_base'],
            reason='off',
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_base'],
        )
        self.env.statbox.bind_entry(
            'phone_operation_applied',
            _inherit_from=['phone_operation_applied', 'local_base'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_added',
            _inherit_from=['phonenumber_alias_subscription_added', 'local_base'],
            _exclude=['mode', 'number', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_given_out',
            _inherit_from=['phonenumber_alias_given_out', 'local_base'],
            _exclude=['login'],
            validation_period=TimeSpan(0),
        )
        self.env.statbox.bind_entry(
            'aliasify_secure_operation_created',
            _inherit_from=['aliasify_secure_operation_created', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'securify_operation_created',
            _inherit_from=['securify_operation_created', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'secure_bind_operation_created',
            _inherit_from=['secure_bind_operation_created', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'local_account_modification',
            _exclude=['track_id', 'step', 'number', 'mode'],
            _inherit_from=['frodo_karma', 'local_base'],
            action=self.track_state,
            login='test',
            registration_datetime='-',
            new='6000',
            old='0',
        )
        self.env.statbox.bind_entry(
            'local_phone_operation_cancelled',
            _inherit_from=['phone_operation_cancelled', 'local_base'],
            operation_type='mark',
        )
        self.env.statbox.bind_entry(
            'local_simple_bind_operation_created',
            _inherit_from=['simple_bind_operation_created', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'local_phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_base'],
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'local_simple_phone_bound',
            _inherit_from=['simple_phone_bound', 'local_base'],
        )
        self.env.statbox.bind_entry(
            'phone_reconfirmed',
            _inherit_from='local_simple_phone_bound',
            action='phone_operation_applied',
        )
        self.env.statbox.bind_entry(
            'account_phones_secure',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode', 'step', 'track_id', 'number'],
            entity='phones.secure',
            operation='created',
            old='-',
            old_entity_id='-',
            new=TEST_PHONE_NUMBER.masked_format_for_statbox,
            new_entity_id='1',
        )
        self.env.statbox.bind_entry(
            'aliasify',
            operation='aliasify',
            is_owner_changed='0',
            validation_period=TimeSpan(0),
            login=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'dealiasify',
            operation='dealiasify',
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_enabled',
            _exclude=['mode', 'step', 'track_id', 'number'],
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_search_enabled',
            _exclude=['mode', 'step', 'track_id', 'number'],
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_added',
            _exclude=['mode', 'step', 'track_id', 'number'],
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_removed',
            _exclude=['mode', 'step', 'track_id', 'number'],
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'base_antifraud_score',
            antifraud_reason='some-reason',
            antifraud_tags='',
            operation='confirm',
            scenario='register',
        )
        self.env.statbox.bind_entry(
            'antifraud_score_allow',
            _inherit_from=['base_antifraud_score'],
            antifraud_action='ALLOW',
        )
        self.env.statbox.bind_entry(
            'antifraud_score_deny',
            _inherit_from=['base_antifraud_score'],
            error='antifraud_score_deny',
            antifraud_action='DENY',
            mask_denial='0',
            status='error',
        )
        self.env.statbox.bind_entry(
            'antifraud_score_captcha',
            _inherit_from=['base_antifraud_score'],
            antifraud_action='ALLOW',
            status='error',
            error='antifraud_score_captcha',
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_enqueued',
            action='enqueued',
            caller=TEST_CONSUMER,
            user_ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            rule='fraud',
            sender='passport',
            number=TEST_PHONE_NUMBER.e164,
            global_smsid=self.env.yasms_fake_global_sms_id_mock.return_value,
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_not_sent',
            action='notdeliveredtosmsc',
            caller=TEST_CONSUMER,
            user_ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            rule='fraud',
            sender='passport',
            number=TEST_PHONE_NUMBER.e164,
            global_smsid=self.env.yasms_fake_global_sms_id_mock.return_value,
        )

    def aliasify_statbox_values(self, dealiasify=False, validation_period=0, login=TEST_LOGIN):
        return [
            self.env.statbox_logger.entry(
                'aliasify',
                validation_period=TimeSpan(validation_period),
                is_owner_changed='1' if dealiasify else '0',
                login=login,
            ),
            self.env.statbox_logger.entry('phonenumber_alias_added'),
            self.env.statbox_logger.entry(
                'account_modification',
                sid='65',
                entity='subscriptions',
                operation='added',
                uid=str(TEST_UID),
                ip=TEST_USER_IP,
                user_agent='curl',
                consumer='dev',
            ),
            self.env.statbox_logger.entry('phonenumber_alias_search_enabled'),
        ]

    def dealiasify_statbox_values(self, reason='owner_change', uid=2):
        return [
            self.env.statbox_logger.entry(
                'dealiasify',
                uid=str(uid),
                reason=reason,
            ),
            self.env.statbox_logger.entry('phonenumber_alias_removed', uid=str(uid)),
            self.env.statbox_logger.entry(
                'account_modification',
                sid='65',
                entity='subscriptions',
                operation='removed',
                uid=str(uid),
                ip=TEST_USER_IP,
                user_agent='curl',
                consumer='dev',
            ),
        ]
