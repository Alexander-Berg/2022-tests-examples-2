# -*- coding: utf-8 -*-
from nose.tools import eq_
from nose_parameterized import (
    param,
    parameterized,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.utils.common import remove_none_values
from passport.backend.utils.time import zero_datetime

from .base_email_bundle import (
    BaseEmailBundleTestCase,
    TEST_EMAIL,
    TEST_IP,
    TEST_RETPATH,
    TEST_UID,
)


@with_settings_hosts(
    PASSPORT_BASE_URL_TEMPLATE='https://0.passportdev.yandex.%(tld)s',
)
class TestSendConfirmationEmail(BaseEmailBundleTestCase):
    def setup_statbox_templates(self):
        super(TestSendConfirmationEmail, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'local_base',
            action='send_confirmation_email',
        )

    def assert_statbox_log(self, _email_created=True, **kwargs):
        kwargs = remove_none_values(kwargs)

        entries = [
            self.env.statbox.entry(
                'local_base',
                **kwargs
            ),
        ]

        if _email_created:
            entries.insert(
                0,
                self.env.statbox.entry(
                    'account_modification',
                    consumer='-',
                    event='account_modification',
                    entity='account.emails',
                    ip=TEST_IP,
                    uid=str(TEST_UID),
                    operation='added',
                    created_at=DatetimeNow(convert_to_datetime=True),
                    user_agent='-',
                    email_id='1',
                    old='-',
                    is_unsafe='1',
                    new=mask_email_for_statbox(TEST_EMAIL),
                    is_suitable_for_restore='0',
                ),
            )

        self.env.statbox.assert_has_written(entries)

    def check_mail_sent(self):
        eq_(
            len(self.env.mailer.messages),
            1,
        )

    def check_email_created(self):
        expected = [
            ('address', TEST_EMAIL),
            ('is_unsafe', '1'),
        ]

        for attr, value in expected:
            self.env.db.check(
                'extended_attributes',
                'value',
                value,
                uid=TEST_UID,
                type=EMAIL_NAME_MAPPING[attr],
                entity_type=EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                db='passportdbshard1',
            )

        self.env.db.check(
            'email_bindings',
            'bound',
            zero_datetime,
            address=TEST_EMAIL,
            uid=TEST_UID,
            db='passportdbshard1',
        )

    def check_ok(self, response, email=TEST_EMAIL, email_retpath=TEST_RETPATH, language=None):
        self.assert_ok_response(response)
        self.assert_statbox_log(
            email=mask_email_for_statbox(email),
            email_retpath=email_retpath,
            status='ok',
            consumer='dev',
        )
        self.check_email_created()
        self.check_mail_sent()

    def make_request(self, headers, post_data):
        return self.env.client.post(
            '/1/email/send_confirmation_email/?consumer=dev',
            data=post_data,
            headers=headers,
        )

    def get_incomplete_track(self):
        _, track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        return track_id

    @parameterized.expand([
        ('track_id.empty', lambda self: None, TEST_EMAIL, TEST_RETPATH),
        ('track_id.invalid', lambda self: 'incorrect_track', TEST_EMAIL, TEST_RETPATH),
        ('track.invalid_state', get_incomplete_track, TEST_EMAIL, TEST_RETPATH),
        ('email.invalid', lambda self: self.track_id, 'incorrect_email', TEST_RETPATH),
        ('email.empty', lambda self: self.track_id, '', TEST_RETPATH),
        ('email.empty', lambda self: self.track_id, '     ', TEST_RETPATH),
        ('email_retpath.invalid', lambda self: self.track_id, TEST_EMAIL, 'incorrect_retpath'),
        ('email_retpath.empty', lambda self: self.track_id, TEST_EMAIL, ''),
        param('language.invalid', lambda self: self.track_id, TEST_EMAIL, TEST_RETPATH, lang='jp'),
        param('language.empty', lambda self: self.track_id, TEST_EMAIL, TEST_RETPATH, lang=''),
    ])
    def test_should_be_err_on(self, err, track_id_getter, email, email_retpath, lang=None):
        response = self.make_request(
            headers=self.get_headers(),
            post_data=self.get_post_data(
                track_id=track_id_getter(self),
                email=email,
                email_retpath=email_retpath,
                language=lang,
            ),
        )

        self.assert_error_response(response, [err])

    def test_user_has_no_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                crypt_password='',
            ),
        )

        response = self.make_request(
            headers=self.get_headers(),
            post_data=self.get_post_data(
                track_id=self.track_id,
                email=TEST_EMAIL,
                email_retpath=TEST_RETPATH,
            ),
        )

        self.assert_error_response(response, ['account.without_password'])
        self.check_blackbox_called()

    def test_social_user_has_no_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login='uid-%s' % TEST_UID,
                aliases={
                    'social': 'uid-%s' % TEST_UID,
                },
                crypt_password='',
            ),
        )

        response = self.make_request(
            headers=self.get_headers(),
            post_data=self.get_post_data(
                track_id=self.track_id,
                email=TEST_EMAIL,
                email_retpath=TEST_RETPATH,
            ),
        )

        self.assert_state_response(response, 'complete_social')
        self.check_blackbox_called()

    def test_email_retpath_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                crypt_password='1:something',
            ),
        )

        response = self.make_request(
            headers=self.get_headers(),
            post_data=self.get_post_data(
                track_id=self.track_id,
                email=TEST_EMAIL,
                email_retpath=TEST_RETPATH,
            ),
        )

        self.check_ok(response)
        self.check_blackbox_called()

    def test_email_no_retpath_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                crypt_password='1:something',
            ),
        )

        response = self.make_request(
            headers=self.get_headers(),
            post_data=self.get_post_data(
                track_id=self.track_id,
                email=TEST_EMAIL,
            ),
        )

        self.check_ok(response, email_retpath=None)
        self.check_blackbox_called()

    def test_email_retpath_language_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                crypt_password='1:something',
            ),
        )

        response = self.make_request(
            headers=self.get_headers(),
            post_data=self.get_post_data(
                track_id=self.track_id,
                email=TEST_EMAIL,
                email_retpath=TEST_RETPATH,
                language='en',
            ),
        )

        self.check_ok(response, language='en')
        self.check_blackbox_called()
