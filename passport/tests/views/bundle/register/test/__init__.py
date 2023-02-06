# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_EMAIL,
    TEST_HOST,
    TEST_PHONE_NUMBER,
    TEST_SUID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_USER_LOGIN_NORMALIZED,
    TEST_USER_PASSWORD_QUALITY,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.email.email import (
    mask_email_for_statbox,
    punycode_email,
)


class StatboxTestMixin(object):

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'local_phone_base',
            _inherit_from='local_base',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted',
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['account_modification', 'local_base'],
            _exclude=['mode'],
            old='-',
            operation='created',
        )
        self.env.statbox.bind_entry(
            'account_register',
            _exclude=['mode'],
            _inherit_from=['frodo_karma', 'local_base'],
            action='account_register',
            suid=str(TEST_SUID),
            login=TEST_USER_LOGIN_NORMALIZED,
            registration_datetime=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'subscriptions',
            _inherit_from=['subscriptions', 'local_base'],
            _exclude=['mode'],
            operation='added',
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from=['account_created', 'local_base'],
            _exclude=['consumer'],
            login=TEST_USER_LOGIN_NORMALIZED,
            password_quality=str(TEST_USER_PASSWORD_QUALITY),
            track_id=self.track_id,
            language=TEST_ACCEPT_LANGUAGE,
        )
        self.env.statbox.bind_entry(
            'confirmed',
            _exclude=['track_id'],
            mode='email_validation',
            action='confirmed',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'get_key',
            _exclude=['track_id'],
            uid='1',
            host=TEST_HOST,
            mode='email_validation',
            action='get_key',
            email=mask_email_for_statbox(punycode_email(TEST_EMAIL)),
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_taken_away',
            _inherit_from=['phonenumber_alias_taken_away', 'local_base'],
            _exclude=['consumer'],
            uid='2',
            track_id=self.track_id,
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_subscription_removed',
            _inherit_from=['phonenumber_alias_subscription_removed', 'local_base'],
            _exclude=['mode', 'track_id'],
            uid='2',
        )
        self.env.statbox.bind_entry(
            'phonereg',
            _exclude=['mode', 'track_id'],
            _inherit_from=['frodo_karma', 'local_base'],
            action='phonereg',
            registration_datetime=DatetimeNow(convert_to_datetime=True),
            old='0',
        )
        self.env.statbox.bind_entry(
            'notification_sent',
            uid=str(TEST_UID),
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            action='phone_registration_login_reminder.notification_sent',
            track_id=self.track_id,
            sms_id='1',
        )
        self.env.statbox.bind_entry(
            'dealiasify_error',
            uid='2',
            error='alias.isnt_deleted',
            track_id=self.track_id,
            operation='dealiasify',
        )
        self.env.statbox.bind_entry(
            'aliasify',
            _inherit_from=['phonenumber_alias_given_out', 'local_base'],
            _exclude=['consumer', 'login'],
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'aliasify_error',
            _inherit_from='aliasify',
            error='alias.isnt_created',
        )
        self.env.statbox.bind_entry(
            'phone_save',
            operation='save',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            uid=str(TEST_UID),
            track_id=self.track_id,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'phone_save_error',
            _inherit_from='phone_save',
            error='phone.isnt_saved',
        )
        self.env.statbox.bind_entry(
            'registration_with_sms_error',
            _exclude=['user_agent'],
            action='registration_with_sms',
            error='registration_sms_per_ip_limit_has_exceeded',
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            _inherit_from=['phone_confirmed', 'local_phone_base'],
            _exclude=['operation_id', 'consumer'],
            code_checks_count='0',
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            _inherit_from=['secure_phone_bound', 'local_phone_base'],
            _exclude=['operation_id', 'consumer'],
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_removed',
            _inherit_from=['phonenumber_alias_removed', 'local_base'],
            _exclude=['mode'],
            uid='2',
        )
        self.env.statbox.bind_entry(
            'phonenumber_alias_added',
            _inherit_from=['phonenumber_alias_added', 'local_base'],
            _exclude=['mode'],
            uid='1',
        )
