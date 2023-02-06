# -*- coding: utf-8 -*-
import datetime
import uuid

import mock
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyInviteTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_DISPLAY_NAME_DATA_WITH_PERCENT,
    TEST_DISPLAY_NAME_WITH_PERCENT,
    TEST_EMAIL,
    TEST_FAMILY_ID,
    TEST_FAMILY_INVITE_ID,
    TEST_HOST,
    TEST_LANGUAGE,
    TEST_PHONE,
    TEST_TIMESTAMP,
    TEST_UID,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
    TEST_USER_TICKET1,
)
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms import YaSmsLimitExceeded
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.conf import settings
from passport.backend.core.models.family import FamilyInvite
from passport.backend.core.test.test_utils import (
    eq_,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import fake_user_ticket
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.core.types.phone_number.phone_number import (
    mask_for_statbox,
    mask_phone_number,
    PhoneNumber,
)


ID_BASE_URL_TEMPLATE = 'https://id.yandex.%(tld)s'
FAMILY_INVITE_URL_TEMPLATE = '%(base_url)s/profile/family/invite/%(invite_id)s'

TEST_E164_PHONE = PhoneNumber.parse(TEST_PHONE).e164
TEST_FORMATTED_PHONE = str(PhoneNumber.parse(TEST_PHONE))
TEST_DB_PHONE = mask_phone_number(TEST_FORMATTED_PHONE)
TEST_STATBOX_PHONE = mask_for_statbox(TEST_FORMATTED_PHONE)
TEST_DB_EMAIL = mask_email_for_statbox(TEST_EMAIL)
TEST_STATBOX_EMAIL = TEST_DB_EMAIL
FAMILY_INVITE_ISSUE_PER_FAMILY_COUNTER = 'invite_issue_%s'
FAMILY_INVITE_ISSUE_PER_UID_COUNTER = 'invite_issue_per_uid_%s'


class FakeDatetime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls.fromtimestamp(TEST_TIMESTAMP, tz=tz)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    ID_BASE_URL_TEMPLATE=ID_BASE_URL_TEMPLATE,
    FAMILY_INVITE_URL_TEMPLATE=FAMILY_INVITE_URL_TEMPLATE,
    FAMILY_INVITE_ISSUE_PER_FAMILY_COUNTER=FAMILY_INVITE_ISSUE_PER_FAMILY_COUNTER,
    FAMILY_INVITE_ISSUE_PER_UID_COUNTER=FAMILY_INVITE_ISSUE_PER_UID_COUNTER,
    FAMILY_DISABLE_SMS_INVITE=False,
    COUNTERS={
        FAMILY_INVITE_ISSUE_PER_FAMILY_COUNTER: 4,
        FAMILY_INVITE_ISSUE_PER_UID_COUNTER: 4,
    },
    FAMILY_INVITES_VIA_EMAIL_CHECK_ANTIFRAUD_SCORE=True,
)
class IssueInviteTestCase(BaseFamilyInviteTestcase, EmailTestMixin):
    default_url = '/1/bundle/family/issue_invite/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(IssueInviteTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'issue_invite',
                        'issue_invite_by_uid',
                    ],
                },
            ),
        )
        self.uuid_patch = mock.patch(
            'uuid.uuid4',
            new=lambda: uuid.UUID(TEST_FAMILY_INVITE_ID, version=4),
        )
        self.uuid_patch.start()
        self.datetime_now_patch = mock.patch(
            'passport.backend.api.views.bundle.family.issue_invite.datetime',
            new=FakeDatetime,
        )
        self.datetime_now_patch.start()
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.setup_antifraud_score_response()
        self.setup_statbox_templates()

    def tearDown(self):
        self.uuid_patch.stop()
        self.datetime_now_patch.stop()
        del self.uuid_patch
        del self.datetime_now_patch

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            consumer='dev',
            ip='1.2.3.4',
            user_agent='curl',
            mode='family',
            action='family_issue_invite',
        )
        self.env.statbox.bind_entry(
            'family_issue_invite',
            status='ok',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'antifraud_score_deny',
            status='error',
            error='antifraud_score_deny',
            uid=str(TEST_UID),
        )

    def setup_antifraud_score_response(self, allow=True, tags=None):
        response = antifraud_score_response(
            action=ScoreAction.ALLOW if allow else ScoreAction.DENY,
            tags=tags,
        )
        self.env.antifraud_api.set_response_value('score', response)

    def setup_kolmogor(self, family_rate=3, uid_rate=3):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                '%s,%s' % (family_rate, uid_rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def build_invite_url(self, tld, invite_id):
        return FAMILY_INVITE_URL_TEMPLATE % {
            'base_url': ID_BASE_URL_TEMPLATE % {'tld': tld},
            'invite_id': invite_id,
        }

    def build_email(
        self,
        address,
        language=TEST_LANGUAGE,
        invite_id=TEST_FAMILY_INVITE_ID,
        inviter_display_name=TEST_DISPLAY_NAME,
    ):
        tld = 'com.tr' if language == 'tr' else language
        data = {
            'language': language,
            'addresses': [address],
            'subject': 'family.invite_email.subject',
            'tanker_keys': {
                'family.invite_email.message': {
                    'INVITER_NAME': inviter_display_name,
                    'INVITE_URL_BEGIN': '<a href="%s">' % self.build_invite_url(tld, invite_id),
                    'INVITE_URL_END': '</a>',
                },
            },
        }
        return data

    def assert_antifraud_score_called(self):
        requests = self.env.antifraud_api.get_requests_by_method('score')
        assert len(requests) == 1

    def assert_antifraud_score_not_called(self):
        assert not self.env.antifraud_api.requests

    def assert_historydb_ok(self, send_method='none', contact='-'):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_issue_invite',
                'uid': str(TEST_UID),
            },
            {
                'name': 'contact',
                'value': contact,
                'uid': str(TEST_UID),
            },
            {
                'name': 'family_id',
                'value': TEST_FAMILY_ID,
                'uid': str(TEST_UID),
            },
            {
                'name': 'invite_id',
                'value': TEST_FAMILY_INVITE_ID,
                'uid': str(TEST_UID),
            },
            {
                'name': 'send_method',
                'value': send_method,
                'uid': str(TEST_UID),
            },
            {
                'name': 'user_agent',
                'value': 'curl',
                'uid': str(TEST_UID),
            },
            {
                'name': 'consumer',
                'value': 'dev',
                'uid': str(TEST_UID),
            },
        ]

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_statbox_ok(self, send_method='none', contact='', with_check_cookies=False, **kwargs):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry(
                'family_issue_invite',
                family_id=TEST_FAMILY_ID,
                invite_id=TEST_FAMILY_INVITE_ID,
                send_method=send_method,
                contact=contact,
                **kwargs
            )
        )
        self.env.statbox.assert_has_written(entries)

    def assert_ydb_exec(self, queries):
        self.env.fake_ydb.assert_queries_executed(queries)

    def assert_mail_sent(
        self,
        email=TEST_EMAIL,
        invite_id=TEST_FAMILY_INVITE_ID,
        language=TEST_LANGUAGE,
        inviter_display_name=TEST_DISPLAY_NAME,
    ):
        self.assert_emails_sent(
            [
                self.build_email(
                    address=email,
                    language=language,
                    invite_id=invite_id,
                    inviter_display_name=inviter_display_name,
                ),
            ],
        )

    def assert_mail_not_sent(self):
        self.assert_emails_sent([])

    def assert_sms_sent(
        self,
        uid=TEST_UID,
        phone=TEST_E164_PHONE,
        language=TEST_LANGUAGE,
        invite_id=TEST_FAMILY_INVITE_ID,
        display_name=TEST_DISPLAY_NAME,
    ):
        tld = 'com.tr' if language == 'tr' else language
        requests = self.env.yasms.requests
        eq_(len(requests), 1)
        translations = settings.translations.NOTIFICATIONS[language]
        url = self.build_invite_url(tld, invite_id)
        message = (
            translations['family.invite_sms.message']
            .replace('%INVITER_NAME%', display_name)
            .replace('%INVITE_URL%', url)
        )
        requests[0].assert_query_contains({
            'from_uid': str(uid),
            'phone': phone,
            'identity': 'family_invite_send.notify',
            'text': message,
        })

    def assert_sms_not_sent(self):
        requests = self.env.yasms.requests
        eq_(requests, [])

    def test_issue_ok(self):
        self.setup_bb_response(has_family=True)
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        resp = self.make_request(query_args={'scenario': 'test-scenario'})
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_historydb_ok()
        self.assert_statbox_ok(scenario='test-scenario', with_check_cookies=True)
        self.assert_ydb_exec(
            self.build_ydb_find() +
            self.build_ydb_insert(self.build_invite(send_method=0, contact='')),
        )

    def test_issue_ok_nearly_full(self):
        self.setup_bb_response(has_family=True)
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID, TEST_UID1])
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        resp = self.make_request()
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_ydb_exec(
            self.build_ydb_find() +
            self.build_ydb_insert(self.build_invite(send_method=0, contact='')),
        )

    def test_family_full_mixed(self):
        self.setup_bb_response(has_family=True, family_members=[TEST_UID, TEST_UID1, TEST_UID2])
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_empty(False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['family.max_capacity'])
        self.assert_historydb_empty()
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_statbox_check_cookies()
        self.assert_ydb_exec(self.build_ydb_find())

    def test_family_full_invites(self):
        self.setup_bb_response(has_family=True, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_invite(number=3) +
            self.build_ydb_empty(False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['family.max_capacity'])
        self.assert_historydb_empty()
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_statbox_check_cookies()
        self.assert_ydb_exec(self.build_ydb_find())

    def test_not_admin(self):
        self.setup_bb_response(has_family=True, own_family=False)
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_empty(False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['family.not_is_admin'])
        self.assert_historydb_empty()
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_statbox_check_cookies()
        self.assert_ydb_exec([])

    def test_send_email(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        resp = self.make_request(query_args={'email': TEST_EMAIL})
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_mail_sent()
        self.assert_sms_not_sent()
        self.assert_historydb_ok(send_method='email', contact=TEST_EMAIL)
        self.assert_statbox_ok(send_method='email', contact=TEST_STATBOX_EMAIL, with_check_cookies=True)
        self.assert_ydb_exec(
            self.build_ydb_find() +
            self.build_ydb_insert(self.build_invite(
                send_method=FamilyInvite.SEND_METHOD_EMAIL,
                contact=TEST_DB_EMAIL,
            )),
        )
        self.assert_antifraud_score_called()

    def test_send_unicode_email(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        resp = self.make_request(query_args={'email': 'test-email1@yandex.ин'})
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_historydb_ok(send_method='email', contact='test-email1@yandex.ин')
        self.assert_mail_sent(email='test-email1@yandex.xn--h1ak')

    def test_send_email_display_name_with_percent(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA_WITH_PERCENT,
        )
        self.setup_bb_family_response(
            admin_uid=TEST_UID, family_members=[TEST_UID],
        )
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        resp = self.make_request(query_args={'email': 'test-email1@yandex.ин'})
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_historydb_ok(
            send_method='email', contact='test-email1@yandex.ин',
        )
        self.assert_mail_sent(
            email='test-email1@yandex.xn--h1ak',
            inviter_display_name=TEST_DISPLAY_NAME_WITH_PERCENT,
        )

    def test_send_sms(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        resp = self.make_request(query_args={'sms_phone': TEST_PHONE})
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_sms_sent()
        self.assert_mail_not_sent()
        self.assert_historydb_ok(send_method='sms', contact=TEST_FORMATTED_PHONE)
        self.assert_statbox_ok(send_method='sms', contact=TEST_STATBOX_PHONE, with_check_cookies=True)
        self.assert_ydb_exec(
            self.build_ydb_find() +
            self.build_ydb_insert(self.build_invite(
                send_method=FamilyInvite.SEND_METHOD_SMS,
                contact=TEST_DB_PHONE,
            )),
        )
        self.assert_antifraud_score_not_called()

    def test_send_sms_disabled(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        with settings_context(
            FAMILY_DISABLE_SMS_INVITE=True,
        ):
            resp = self.make_request(query_args={'sms_phone': TEST_PHONE})
        self.assert_ok_response(resp)
        self.assert_sms_not_sent()
        self.assert_mail_not_sent()
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()

    def test_send_sms__yasms_error(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        self.env.yasms.set_response_side_effect('send_sms', YaSmsLimitExceeded())
        resp = self.make_request(query_args={'sms_phone': TEST_PHONE})
        self.assert_error_response(resp, ['sms_limit.exceeded'])

    def test_issue_limit_reached_by_family(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor(family_rate=5)
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_historydb_empty()
        self.assert_ydb_exec(self.build_ydb_find())

    def test_issue_limit_reached_by_uid(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor(uid_rate=4)
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_historydb_empty()
        self.assert_ydb_exec(self.build_ydb_find())

    def test_send_email__antifraud_denied(self):
        self.setup_bb_response(
            has_family=True,
            display_name=TEST_DISPLAY_NAME_DATA,
        )
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        self.setup_antifraud_score_response(allow=False)
        resp = self.make_request(query_args={'email': TEST_EMAIL})
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_historydb_empty()
        self.assert_ydb_exec(self.build_ydb_find())
        self.assert_antifraud_score_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('antifraud_score_deny'),
        ])

    def test_auth_by_uid__ok(self):
        self.setup_bb_response(has_family=True)
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_family_admin_response()),
        )
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=[
                'cookie',
                'host',
            ],
        )
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_ydb_exec(
            self.build_ydb_find() +
            self.build_ydb_insert(self.build_invite(send_method=0, contact='')),
        )

    def test_auth_by_user_ticket__ok(self):
        self.setup_bb_response(has_family=True)
        self.setup_bb_family_response(admin_uid=TEST_UID, family_members=[TEST_UID])
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_family_admin_response()),
        )
        self.setup_ydb(
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self.setup_kolmogor()
        ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=['bb:sessionid'],
            uids=[TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([ticket])

        resp = self.make_request(
            headers=dict(
                user_ticket=TEST_USER_TICKET1,
            ),
            exclude_headers=[
                'cookie',
                'host',
            ],
        )
        self.assert_ok_response(resp, invite_id=TEST_FAMILY_INVITE_ID)
        self.assert_mail_not_sent()
        self.assert_sms_not_sent()
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_ydb_exec(
            self.build_ydb_find() +
            self.build_ydb_insert(self.build_invite(send_method=0, contact='')),
        )
