import json

import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run

CONVERT_LOGIN_TO_PHONE = {
    'another_login': 'work_email@yandex-team.ru',
    'first-login': 'team-t@yandex-team.ru',
}


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', files=['owners_and_experiments.sql'])
@pytest.mark.now('2019-01-09T12:00:00')
@pytest.mark.config(
    EXP3_EXPIRATION_SETTINGS={
        'alert_settings': [
            {
                'days_left': 2,
                'message': '2 days of experiment life left for: {}',
            },
        ],
    },
    EXP3_ADMIN_CONFIG={
        'features': {'backend': {'chaos_tags_enabled': True}},
        'settings': {
            'backend': {
                'trusted_file_lines_count_change_threshold': {
                    'absolute': 10,
                    'percentage': 20,
                },
            },
        },
    },
    EXP_COPY_EMAILS_FOR_ALERT=['serg-novikov@yandex-team.ru'],
    EXP_BACK_EMAIL_FOR_ALERTS='serg-novikov@yandex-team.ru',
)
async def test_send_alert(
        taxi_exp_client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(f'{settings.STAFF_API_URL}/v3/persons')
    def _email_from_staff(*args, **kwargs):
        assert 'params' in kwargs
        assert 'login' in kwargs['params']
        return response_mock(
            text=json.dumps(
                {
                    'work_email': (
                        CONVERT_LOGIN_TO_PHONE[kwargs['params']['login']]
                    ),
                },
            ),
        )

    @patch_aiohttp_session(f'{settings.STICKER_API_URL}/send-internal/')
    def _send_email(method, url, headers, **kwargs):
        if not hasattr(_send_email, 'data'):
            _send_email.data = [kwargs['json']]
        else:
            _send_email.data.append(kwargs['json'])
        return response_mock(text='{}')

    # running cron
    await cron_run.main(
        ['taxi_exp.stuff.send_alert_by_expiration_experiments', '-t', '0'],
    )

    assert _send_email.data == [
        {
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n'
                '<mails><mail><from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">2 days left life of your '
                'experiments</subject>'
                '<body>2 days of experiment life left for: '
                'superapp, map_view</body></mail></mails>'
            ),
            'idempotence_token': (
                'cdd48f7d72f2749ad5d2b071c085f7fd113a9e'
                'f5bf1fa6e21cdb54b898db5b88'
            ),
            'send_to': 'work_email@yandex-team.ru',
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n'
                '<mails><mail><from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">2 days left life of your '
                'experiments</subject>'
                '<body>2 days of experiment life left for: '
                'superapp</body></mail></mails>'
            ),
            'idempotence_token': (
                '13ec0e8e0c11690b040be1c1f2727456f981af'
                '2ea1142ddb56f4bb7fe85c6194'
            ),
            'send_to': 'team-t@yandex-team.ru',
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
    ]
