# coding=utf-8
from json import loads

from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)


def challenge_log(action, tags):
    return '\t'.join([
        'tskv',
        'action=ufo_profile_checked',
        'af_action={}'.format(action),  # комментарий для привлечения внимания, чтобы строчку находить
        'af_is_auth_forbidden=0',
        'af_is_challenge_required=1',
        'af_reason=foobar',
        'af_tags={}'.format(','.join(tags)),  # комментарий для привлечения внимания, чтобы строчку находить
        'consumer=passport',
        'current=foobar',
        'decision_source=antifraud_api',
        'input_login=hebei5566@yandex.com',
        'ip=47.57.237.49',
        'is_challenge_required=1',
        'is_fresh_account=0',
        'is_mobile=0',
        'kind=ydb',
        'login=foobar',
        'mode=any_auth',
        'origin=hostroot_homer_auth_com',
        'py=1',
        'timestamp=2021-12-15 15:49:37',
        'timezone=+0300',
        'track_id=e97a0ed117348dbc39ee2242aef46c19cb',
        'tskv_format=passport-log',
        'type=multi_step_password',
        'ufo_distance=0',
        'ufo_status=1',
        'uid=123456',
        'unixtime=1639572577',
        'user_agent=foobar',
        'yandexuid=3083641691639546885',
        'request_id=foobar',
    ])


class TestXunistaterFunctions(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    @parameterized.expand(
        [
            # (parser_id, condition_set_id, stdin, stdout_expected)
            ('statbox.log', 'drive_auth.start.rps', 'tskv\taction=create_drive_session', '[["drive_auth.start.rps.total_dmmm",1]]'),
            ('statbox.log', 'drive_auth.build_nonce.rps', 'tskv\taction=build_nonce', '[["drive_auth.build_nonce.rps.total_dmmm",1]]'),
            ('statbox.log', 'drive_auth.stop.rps', 'tskv\taction=delete_drive_session', '[["drive_auth.stop.rps.total_dmmm",1]]'),
            ('statbox.log', 'drive_auth.issue_authorization_code.rps', 'tskv\taction=issue_authorization_code', '[["drive_auth.issue_authorization_code.rps.total_dmmm",1]]'),
            ('statbox.log', 'drive_auth.check_nonce.rps', 'tskv\taction=check_nonce', '[["drive_auth.check_nonce.rps.total_dmmm",1]]'),

            ('statbox.log', 'auth_social.rps', 'tskv\taction=auth\tmode=social', '[["auth_social.rps.total_dmmm",1]]'),
            ('statbox.log', 'auth_password.rps', 'tskv\taction=submitted\ttype=password\tmode=any_auth', '[["auth_password.rps.total_dmmm",1]]'),
            ('statbox.log', 'auth_2fa.rps', 'tskv\taction=submitted\ttype=2fa', '[["auth_2fa.rps.total_dmmm",1]]'),
            ('statbox.log', 'auth_2fa.rps', 'tskv\taction=rfc_otp_submitted\tmode=any_auth', '[["auth_2fa.rps.total_dmmm",1]]'),
            ('statbox.log', 'auth_2fa.rps', 'tskv\taction=otp_auth_finished\tmode=any_auth\ttype=otp', '[["auth_2fa.rps.total_dmmm",1]]'),
            ('statbox.log', 'auth_2fa.rps', 'tskv\taction=otp_auth_finished\tmode=any_auth\ttype=x_token', '[["auth_2fa.rps.total_dmmm",1]]'),
            ('statbox.log', 'auth_magic.rps', 'tskv\taction=submitted\ttype=magic', '[["auth_magic.rps.total_dmmm",1]]'),

            ('statbox.log', 'ufo_status.rps', 'tskv\taction=ufo_profile_checked\tmode=any_auth\tkind=ufo\tufo_status=0', '[["profile.ufo.ufo_status.0_dmmm",1]]'),
            ('statbox.log', 'ufo_failed.rps', 'tskv\taction=ufo_profile_checked\tmode=any_auth\tdecision_source=ufo_failed\tkind=ufo', '[["ufo_failed.rps_dmmm",1]]'),

            ('statbox.log', 'is_challenge_required.0.web_or_mobile.rps',
             'tskv\taction=ufo_profile_checked\tmode=any_auth\tis_mobile=0\tkind=ololo\tis_challenge_required=0',
             '[["profile.ololo.is_challenge_required.0.web_dmmm",1]]'),
            ('statbox.log', 'is_challenge_required.0.web_or_mobile.rps',
             'tskv\taction=ufo_profile_checked\tmode=any_auth\tis_mobile=1\tkind=ololo\tis_challenge_required=0',
             '[["profile.ololo.is_challenge_required.0.mobile_dmmm",1]]'),
            ('statbox.log', 'is_challenge_required.1.web_or_mobile.rps',
             'tskv\taction=profile_threshold_exceeded\tmode=any_auth\tis_mobile=0\tkind=ololo',
             '[["profile.ololo.is_challenge_required.1.web_dmmm",1]]'),
            ('statbox.log', 'is_challenge_required.1.web_or_mobile.rps',
             'tskv\taction=profile_threshold_exceeded\tmode=any_auth\tis_mobile=1\tkind=ololo',
             '[["profile.ololo.is_challenge_required.1.mobile_dmmm",1]]'),
            ('statbox.log', 'antifraud_tags_allow',
             challenge_log('ALLOW', ['sms,question,flash_call']),
             '[["challenge.af_tags.resolution.challenge.rps_dmmm",1], ["challenge.af_tags.content.sms,question,flash_call.rps_dmmm", 1]]'),
            ('statbox.log', 'antifraud_tags_allow',
             challenge_log('ALLOW', ['']),
             '[["challenge.af_tags.resolution.allow.rps_dmmm",1], ["challenge.af_tags.content..rps_dmmm", 1]]'),
            ('statbox.log', 'antifraud_tags_deny',
             challenge_log('DENY', ['']),
             '[["challenge.af_tags.resolution.deny.rps_dmmm",1]]'),

            ('graphite.log', 'builder.rps', 'tskv\tservice=passport', '[["builder.rps.total.passport_dmmm",1]]'),
            ('graphite.log', 'builder.duration', 'tskv\tservice=passport\tduration=0.633',
             '[["builder.duration.passport_dhhh",[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[12,0],[15,0],[17,0],[20,0],[25,0],[30,0],[35,0],[40,0],[45,0],'
             '[50,0],[60,0],[70,0],[80,0],[90,0],[100,0],[125,0],[150,0],[175,0],[200,0],[225,0],[250,0],[275,0],[300,0],[400,0],[500,1],[750,0],[1000,0],[2000,0],[3000,0],[4000,0],'
             '[5000,0],[10000,0]]]]'),
            ('graphite.log', 'builder.http_code.rps', 'tskv\tservice=passport\thttp_code=404', '[["builder.http_code.4xx.passport_dmmm",1]]'),
            ('graphite.log', 'builder.success.rps', 'tskv\tservice=passport\tresponse=success', '[["builder.rps.success.passport_dmmm",1]]'),
            ('graphite.log', 'builder.failed.rps', 'tskv\tservice=passport\tresponse=failed', '[["builder.rps.failed.passport_dmmm",1]]'),
            ('graphite.log', 'builder.timeout.rps', 'tskv\tservice=passport\tresponse=timeout', '[["builder.rps.timeout.passport_dmmm",1]]'),
            ('access.log', 'access_log.errors',
             'tskv\tconsumer=foo\tstatus=error\terror=request.several_credentials_missing',
             '[["errors.total_dmmm", 1], ["errors.foo_dmmm", 1]]'),
            ('access.log', 'access_log.errors',
             'tskv\tconsumer=foo\tstatus=error\terror=access.denied',
             '[["errors.total_dmmm", 1], ["errors.foo_dmmm", 1]]'),
            ('access.log', 'access_log.errors',
             'tskv\tconsumer=foo\tstatus=error\terror=AccessDenied',
             '[["errors.total_dmmm", 1], ["errors.foo_dmmm", 1]]'),
            ('access.log', 'access_log.errors',
             'tskv\tconsumer=foo\tstatus=error\terror=MissingHeader',
             '[["errors.total_dmmm", 1], ["errors.foo_dmmm", 1]]'),
        ])
    def test_xunistater_signal_parser_with_product_config(self, parser_id, condition_set_id, stdin, stdout_expected):
        # Проверка всех tskv парсеров из продового конфига xunistarter по одному
        result = self.env.xunistater_checker.check_xunistater_signal(parser_id, condition_set_id, stdin)
        assert result == loads(stdout_expected)

    def test_xunistater_signals_parser_with_product_config(self):
        """Проверка метода пакетной проверки генерации сигналов"""
        stdin = '''
            tskv\taction=auth\tmode=social
            tskv\taction=create_drive_session
            tskv\taction=auth\tmode=social
        '''
        expected_signals = {
            "drive_auth.start.rps.total_dmmm": 1,
            "auth_social.rps.total_dmmm": 2,
            }
        used_condition_set_ids = ['drive_auth.start.rps', 'auth_social.rps']

        self.env.xunistater_checker.check_xunistater_signals(stdin, used_condition_set_ids, expected_signals)
