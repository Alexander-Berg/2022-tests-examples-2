# -*- coding: utf-8 -*-
from passport.backend.api.common.phone_karma import PhoneKarma
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_OPERATION_ID,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)

from .base_test_data import (
    TEST_LOGIN,
    TEST_PHONE_ID,
    TEST_REPLACEMENT_PHONE_ID,
    TEST_REPLACEMENT_PHONE_NUMBER,
    TEST_SECURE_PHONE_ID,
    TEST_SECURE_PHONE_NUMBER,
)


class StatboxTestMixin(object):
    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode=self.mode,
            consumer='dev',
            step=self.step,
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'local_phone_base',
            _inherit_from='local_base',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'with_operation_id',
            operation_id=str(TEST_OPERATION_ID),
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'completed',
            _inherit_from=['local_phone_base', 'with_operation_id'],
            action='completed',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'phone_operation_created',
            _inherit_from='local_phone_base',
            _exclude=['mode', 'step', 'track_id'],
            action='phone_operation_created',
            uid=str(TEST_UID),
            operation_type=self.mode,
            phone_id=str(TEST_PHONE_ID),
        )
        self.env.statbox.bind_entry(
            'replace_secure_phone_operation_created',
            _inherit_from=[
                'replace_secure_phone_with_bound_phone_operation_created',
                'local_base',
                'with_operation_id',
            ],
            _exclude=['mode', 'step', 'track_id'],
            secure_phone_id=str(TEST_SECURE_PHONE_ID),
            secure_number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
            simple_phone_id=str(TEST_REPLACEMENT_PHONE_ID),
            simple_number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'dealiasify_secure_operation_created',
            _inherit_from=['dealiasify_secure_operation_created', 'local_phone_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'aliasify_secure_operation_created',
            _inherit_from=['aliasify_secure_operation_created', 'local_phone_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'mark_operation_created',
            _inherit_from=['mark_operation_created', 'local_phone_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'mark_operation_created',
            _inherit_from=['mark_operation_created', 'local_phone_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'remove_secure_operation_created',
            _inherit_from=['remove_secure_operation_created', 'local_phone_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'phone_operation_cancelled',
            _inherit_from=['local_phone_base', 'with_operation_id'],
            action='phone_operation_cancelled',
            uid=str(TEST_UID),
            operation_type=self.mode,
        )
        self.env.statbox.bind_entry(
            'code_sent',
            _inherit_from=['code_sent', 'local_phone_base', 'with_operation_id'],
            action='%s.%s.send_confirmation_code.code_sent' % (self.mode, self.step),
        )
        self.env.statbox.bind_entry(
            'send_code_error',
            _inherit_from=['local_phone_base'],
            uid=str(TEST_UID),
            action='%s.%s.send_confirmation_code' % (self.mode, self.step),
            error='sms_limit.exceeded',
        )
        self.env.statbox.bind_entry(
            'password_checked',
            _inherit_from=['local_phone_base', 'with_operation_id'],
            action='password_checked',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_phone_base', 'with_operation_id'],
        )
        self.env.statbox.bind_entry(
            'phone_secured',
            _inherit_from=['phone_secured', 'local_phone_base', 'with_operation_id'],
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'local_phone_base', 'with_operation_id'],
        )
        self.env.statbox.bind_entry(
            'simple_phone_bound',
            _inherit_from=['simple_phone_bound', 'local_phone_base', 'with_operation_id'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_removed',
            _inherit_from=['phonenumber_alias_subscription_removed', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_added',
            _inherit_from=['phonenumber_alias_subscription_added', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'secure_phone_removed',
            _inherit_from=['secure_phone_removed', 'local_phone_base', 'with_operation_id'],
        )
        self.env.statbox.bind_entry(
            'phone_unbound',
            _inherit_from=['phone_unbound', 'local_phone_base', 'with_operation_id'],
            number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'secure_phone_replaced',
            _inherit_from=['secure_phone_replaced', 'local_base', 'with_operation_id'],
            new_secure_number=TEST_REPLACEMENT_PHONE_NUMBER.masked_format_for_statbox,
            new_secure_phone_id=str(TEST_REPLACEMENT_PHONE_ID),
            old_secure_number=TEST_SECURE_PHONE_NUMBER.masked_format_for_statbox,
            old_secure_phone_id=str(TEST_SECURE_PHONE_ID),
        )
        self.env.statbox.bind_entry(
            'frodo_karma',
            _inherit_from=['frodo_karma', 'local_base'],
            new='6000',
            old='0',
            action='%s_%s' % (self.mode, self.step) if self.mode and self.step else '',
            login=TEST_LOGIN,
        )
        self.env.statbox.bind_entry(
            'phone_secure_replace_commit',
            _inherit_from=['frodo_karma', 'local_base'],
            _exclude=['step', 'mode', 'track_id'],
            registration_datetime='-',
            action='phone_secure_replace_commit',
        )
        self.env.statbox.bind_entry(
            'notification_sent',
            _inherit_from='local_phone_base',
            action='notify_user_by_sms_that_secure_phone_removal_started.notification_sent',
            uid=str(TEST_UID),
            sms_id='1',
        )
        self.env.statbox.bind_entry(
            'account_phones_secure',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
            entity='phones.secure',
            operation='created',
            old='-',
            old_entity_id='-',
            new=TEST_PHONE_NUMBER.masked_format_for_statbox,
            new_entity_id=str(TEST_PHONE_ID),
        )
        self.env.statbox.bind_entry(
            'account_modification_secure_phone_removed',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
            entity='phones.secure',
            operation='deleted',
            old=TEST_PHONE_NUMBER.masked_format_for_statbox,
            old_entity_id=str(TEST_PHONE_ID),
            new='-',
            new_entity_id='-',
        )
        self.env.statbox.bind_entry(
            'check_phone_karma',
            _inherit_from=['local_phone_base'],
            action='check_phone_karma',
            uid=str(TEST_UID),
            karma=str(PhoneKarma.white),
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_removed',
            _inherit_from=['phonenumber_alias_removed', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_added',
            _inherit_from=['phonenumber_alias_added', 'local_base'],
            _exclude=['mode', 'step', 'track_id'],
        )
        self.env.statbox.bind_entry(
            'base_pharma',
            _inherit_from=['local_base'],
            action='.'.join([self.mode or '-', self.step or '-', 'send_confirmation_code']),
            antifraud_reason='some-reason',
            antifraud_tags='',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            scenario='authorize',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'pharma_allowed',
            _inherit_from=['base_pharma'],
            antifraud_action='ALLOW',
        )
        self.env.statbox.bind_entry(
            'pharma_denied',
            _inherit_from=['base_pharma'],
            antifraud_action='DENY',
            error='antifraud_score_deny',
            mask_denial='0',
            status='error',
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_enqueued',
            action='enqueued',
            caller='dev',
            global_smsid=self.env.yasms_fake_global_sms_id_mock.return_value,
            identity='antifraud',
            number=TEST_PHONE_NUMBER.e164,
            rule='fraud',
            sender='passport',
            user_agent=TEST_USER_AGENT,
            user_ip=TEST_USER_IP,
        )
        self.env.yasms_private_logger.bind_entry(
            'yasms_not_sent',
            action='notdeliveredtosmsc',
            caller='dev',
            global_smsid=self.env.yasms_fake_global_sms_id_mock.return_value,
            identity='antifraud',
            number=TEST_PHONE_NUMBER.e164,
            rule='fraud',
            sender='passport',
            user_agent=TEST_USER_AGENT,
            user_ip=TEST_USER_IP,
        )
