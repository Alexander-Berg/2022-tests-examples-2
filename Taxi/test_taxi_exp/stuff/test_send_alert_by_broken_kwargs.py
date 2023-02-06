import json

import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run


CONVERT_LOGIN_TO_PHONE = {
    'owner_1': 'owner_1@yandex-team.ru',
    'owner_2': 'owner_2@yandex-team.ru',
}


@pytest.mark.config(
    EXP_COPY_EMAILS_FOR_ALERT=['serg-novikov@yandex-team.ru'],
    EXP_BACK_EMAIL_FOR_ALERTS='serg-novikov@yandex-team.ru',
)
@pytest.mark.now('2019-01-09T12:00:00')
@pytest.mark.pgsql('taxi_exp', files=('history.sql',))
async def test_send_alert_by_broken_kwargs(
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

    await cron_run.main(
        ['taxi_exp.stuff.send_alert_by_broken_kwargs', '-t', '0'],
    )

    assert _send_email.data == [
        {
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n'
                '<mails><mail><from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">Broken kwargs alert</subject>'
                '<body>owner_1!\n'
                'Your experiments (first, second, third) '
                'may use incorrect or\n'
                'missing arguments.\n'
                'Reason destructive changes were made in the consumers:\n'
                '\n'
                '    Experiment: first\n'
                '    Consumers: test_consumer\n'
                '\n'
                '    Experiment: second\n'
                '    Consumers: test_consumer\n'
                '\n'
                '    Experiment: third\n'
                '    Consumers: test_consumer\n'
                '\n'
                'Details: [{\'consumer\': \'test_consumer\', '
                '\'kwargs_history\': [\'{"kwargs": '
                '[{"name": "phone_id", "type": "datetime", '
                '"is_mandatory": false}], '
                '"updated": "2019-01-09T14:00:00+03:00", '
                '"metadata": {}, "library_version": "3-broken"}\', '
                '\'{"kwargs": [], "updated": "2019-01-09T15:00:00+03:00", '
                '"metadata": {}, '
                '"library_version": "4-broken"}\']}]</body></mail></mails>'
            ),
            'idempotence_token': (
                '8879b6907d44d14075ae826c60e99bad25bb43'
                'db74f513674e1d9dd4da22f1a7'
            ),
            'send_to': 'owner_1@yandex-team.ru',
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n'
                '<mails><mail><from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">Broken kwargs alert</subject>'
                '<body>owner_2!\n'
                'Your experiments (second, four) may use incorrect or\n'
                'missing arguments.\n'
                'Reason destructive changes were made in the consumers:\n'
                '\n'
                '    Experiment: second\n'
                '    Consumers: test_consumer\n'
                '\n'
                '    Experiment: four\n'
                '    Consumers: test_consumer\n'
                '\n'
                'Details: [{\'consumer\': \'test_consumer\', '
                '\'kwargs_history\': [\'{"kwargs": [{"name": "phone_id", '
                '"type": "datetime", "is_mandatory": false}], '
                '"updated": "2019-01-09T14:00:00+03:00", '
                '"metadata": {}, "library_version": "3-broken"}\', '
                '\'{"kwargs": [], "updated": "2019-01-09T15:00:00+03:00", '
                '"metadata": {}, '
                '"library_version": "4-broken"}\']}]</body></mail></mails>'
            ),
            'idempotence_token': (
                '19f9f94fd6e8f17c4c65d11693e70c892a85da'
                '0cc90958d3699a812f4d699a46'
            ),
            'send_to': 'owner_2@yandex-team.ru',
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
    ]
